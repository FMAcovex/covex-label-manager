"""Controlled composition fixes; the source Word and PDF are never overwritten."""
import json
from copy import deepcopy
from pathlib import Path
import fitz
from .geometry import rel, edrofonio_template


def corrected_edrofonio(source, destination):
    """Fit the overflowing nested Word table to the original outer frame.

    Derived pending rendition: horizontal re-layout of the nested region only.
    No replacement of the stored source. The outer physical frame is unchanged.
    """
    left,right,top,bottom=84.8,474.4,133.60077,609.80078
    inner_right,inner_top,inner_bottom=516.9,259.60077,597.80078
    with fitz.open(source) as original:
        fields,area=edrofonio_template(source,[left,top,inner_right,bottom])
        with fitz.open(stream=original.tobytes(),filetype='pdf') as working:
            # This is the outer border crossing the too-wide nested table.
            # Remove only vector graphics in the derived copy, never text.
            p=working[0]
            p.add_redact_annot(fitz.Rect(right-.6,inner_top+.6,right+.6,inner_bottom-.6),fill=False)
            p.apply_redactions(images=0,graphics=2,text=1)
            with fitz.open() as output:
                page=output.new_page(width=original[0].rect.width,height=original[0].rect.height)
                page.show_pdf_page(fitz.Rect(0,0,page.rect.width,inner_top),original,0,clip=fitz.Rect(0,0,page.rect.width,inner_top))
                page.show_pdf_page(fitz.Rect(left,inner_top,right,inner_bottom),working,0,
                    clip=fitz.Rect(left,inner_top,inner_right,inner_bottom),keep_proportion=False)
                page.show_pdf_page(fitz.Rect(0,inner_bottom,page.rect.width,page.rect.height),original,0,
                    clip=fitz.Rect(0,inner_bottom,page.rect.width,page.rect.height))
                # Redaction can remove intersecting horizontal strokes: redraw
                # the real row borders from the Word-derived PDF geometry.
                ys={round(d['rect'].y0,5) for d in original[0].get_drawings() if d['rect'].height<.01 and d['rect'].width>400 and inner_top<=d['rect'].y0<=inner_bottom}
                for y in ys:
                    page.draw_line((left,y),(right,y),color=(.42,.42,.42),width=.5)
                page.draw_rect(fitz.Rect(left,top,right,bottom),color=(.42,.42,.42),width=.5)
                output.save(destination,deflate=True)
        crop=[left,top,right,bottom]
        # Translate configuration through the same inner-table horizontal map.
        old=[left,top,inner_right,bottom];factor=(right-left)/(inner_right-left)
        def region(r):
            x,y,w,h=r
            return rel(left+x*(inner_right-left)*factor,top+y*(bottom-top),w*(inner_right-left)*factor,h*(bottom-top),crop)
        fixed=deepcopy(fields)
        for f in fixed:
            f.update(zip(('x','y','w','h'),region([f[k] for k in ('x','y','w','h')])))
            if f.get('erase'):f['erase']=region(f['erase'])
            if 'second_x' in f:f['second_x']=region([f['second_x'],0,0,0])[0]
            if 'next_w' in f:f['next_w']=region([0,0,f['next_w'],0])[2]
            # Leave space inside the real border, not after it.
            if f['key']=='numero':
                f['w']=(right-3-(crop[0]+f['x']*(crop[2]-crop[0])))/(crop[2]-crop[0])
        return crop,fixed,region(area)
