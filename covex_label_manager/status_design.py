"""R7A status-label layout contract and *proof-only* PDF renderer.

No persistence, no QA disposition changes, no production emission. Importing a
PDF never implies documentary approval. Legacy masters are not interpreted as
R7A layouts because their fields use different fixed-position geometry.
"""
from __future__ import annotations

from datetime import datetime
import math
import re
from pathlib import Path

import fitz

KINDS = ("sin_analizar", "aprobado", "rechazado")
MM_PER_POINT = 25.4 / 72
MAX_FIELDS = 32
MAX_PAGES = 100
KEY = re.compile(r"^[a-z][a-z0-9_]{0,39}$")


class StatusDesignError(ValueError):
    """Unsafe or invalid status-label geometry/data."""


def _finite(value, name, *, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise StatusDesignError(name + ": se requiere un número.")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise StatusDesignError(name + ": se requiere un número.") from exc
    if not math.isfinite(number) or (minimum is not None and number < minimum) or (maximum is not None and number > maximum):
        raise StatusDesignError(name + ": valor fuera de rango.")
    return number


def _rectangle(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise StatusDesignError(name + ": indique cuatro coordenadas.")
    x0, y0, x1, y1 = (_finite(v, name) for v in value)
    if x1 <= x0 or y1 <= y0:
        raise StatusDesignError(name + ": rectángulo vacío o invertido.")
    return fitz.Rect(x0, y0, x1, y1)


def _inside(outer, inner):
    return (inner.x0 >= outer.x0 - 0.00001 and inner.y0 >= outer.y0 - 0.00001
            and inner.x1 <= outer.x1 + 0.00001 and inner.y1 <= outer.y1 + 0.00001)


def validate_layout(layout, document):
    """Return normalized layout after verifying actual source-PDF page bounds.

    Field boxes use PDF points in the *uncropped page* coordinate system, so
    changing the crop must be reviewed and cannot silently move variable text.
    """
    if not isinstance(layout, dict) or layout.get("contract") != 1:
        raise StatusDesignError("Contrato de diseño de estado no reconocido.")
    kind = layout.get("kind")
    if kind not in KINDS:
        raise StatusDesignError("Clase de etiqueta de estado desconocida.")
    if not isinstance(document, fitz.Document) or not 1 <= len(document) <= MAX_PAGES:
        raise StatusDesignError("PDF inexistente, vacío o con demasiadas páginas.")
    page_index = layout.get("page")
    if type(page_index) is not int or not 0 <= page_index < len(document):
        raise StatusDesignError("Página de estado fuera del documento.")
    page_rect = document[page_index].rect
    crop = _rectangle(layout.get("crop"), "Recorte")
    if not _inside(page_rect, crop):
        raise StatusDesignError("Recorte fuera de la página PDF.")
    if crop.width * MM_PER_POINT < 10 or crop.height * MM_PER_POINT < 8:
        raise StatusDesignError("Recorte demasiado pequeño para una etiqueta.")
    fields = layout.get("fields")
    if not isinstance(fields, list) or len(fields) > MAX_FIELDS:
        raise StatusDesignError("Lista de campos inválida o excesiva.")
    normalized = []
    used = set()
    boxes = []
    for item in fields:
        if not isinstance(item, dict):
            raise StatusDesignError("Definición de campo inválida.")
        key = item.get("key")
        if not isinstance(key, str) or not KEY.fullmatch(key) or key in used:
            raise StatusDesignError("Clave de campo inválida o duplicada.")
        used.add(key)
        area = _rectangle(item.get("rect"), "Campo " + key)
        if not _inside(crop, area):
            raise StatusDesignError("Campo " + key + " fuera del recorte.")
        for prior in boxes:
            if (area & prior).is_empty is False and (area & prior).get_area() > 0.01:
                raise StatusDesignError("Campos variables solapados.")
        boxes.append(area)
        size = _finite(item.get("font_size", 10), "Tipografía " + key, minimum=5, maximum=72)
        if not isinstance(item.get("required", False), bool):
            raise StatusDesignError("Obligatoriedad inválida.")
        if not isinstance(item.get("bold", False), bool):
            raise StatusDesignError("Negrita inválida.")
        label = item.get("label", key)
        if not isinstance(label, str) or not label.strip() or len(label) > 80:
            raise StatusDesignError("Descripción de campo inválida.")
        normalized.append({"key": key, "label": label.strip(), "rect": list(area),
                           "font_size": size, "bold": item.get("bold", False),
                           "required": item.get("required", False)})
    return {"contract": 1, "kind": kind, "page": page_index,
            "crop": list(crop), "fields": normalized,
            "size_mm": [round(crop.width * MM_PER_POINT, 3),
                        round(crop.height * MM_PER_POINT, 3)]}


def make_layout(pdf_path, kind, page=0, crop=None):
    """Prepare a PENDING design; never infer approval or documentary version."""
    with fitz.open(pdf_path) as doc:
        if crop is None:
            if type(page) is not int or not 0 <= page < len(doc):
                raise StatusDesignError("Seleccione una página válida.")
            crop = list(doc[page].rect)
        return validate_layout({"contract": 1, "kind": kind, "page": page,
                                "crop": crop, "fields": []}, doc)


def validate_values(layout, values, *, strict=True):
    if not isinstance(values, dict):
        raise StatusDesignError("Datos variables inválidos.")
    output = {}
    allowed = {field["key"] for field in layout["fields"]}
    if strict and set(values) - allowed:
        raise StatusDesignError("Los datos contienen campos no definidos en el diseño.")
    for field in layout["fields"]:
        key = field["key"]
        value = values.get(key, "")
        if value is None:
            value = ""
        if not isinstance(value, str) or any(c in value for c in ("\r", "\n", "\0")):
            raise StatusDesignError("El valor de " + key + " debe ser una sola línea de texto.")
        if len(value) > 300:
            raise StatusDesignError("El valor de " + key + " es excesivamente largo.")
        value = value.strip()
        if strict and field["required"] and not value:
            raise StatusDesignError("Falta el dato obligatorio " + field["label"] + ".")
        output[key] = value
    return output


def render_proof(pdf_path, layout, values, destination, *, width_mm=None):
    """Render a watermarked, single-page proof. Does not touch approved masters.

    The source PDF remains untouched, content is vector-copied, and all rendered
    text is checked against its configured box before drawing.
    """
    pdf_path, destination = Path(pdf_path), Path(destination)
    if pdf_path.resolve() == destination.resolve():
        raise StatusDesignError("La prueba nunca debe sustituir el PDF original.")
    with fitz.open(pdf_path) as source:
        design = validate_layout(layout, source)
        data = validate_values(design, values, strict=False)
        crop = fitz.Rect(design["crop"])
        width = crop.width if width_mm is None else _finite(width_mm, "Ancho", minimum=10, maximum=500) / MM_PER_POINT
        scale = width / crop.width
        height = crop.height * scale
        if min(width, height) < 25:
            raise StatusDesignError("La prueba quedaría ilegible.")
        output = fitz.open()
        try:
            page = output.new_page(width=width, height=height)
            dest = fitz.Rect(0, 0, width, height)
            page.show_pdf_page(dest, source, design["page"], clip=crop, keep_proportion=True)
            for field in design["fields"]:
                value = data[field["key"]]
                if not value:
                    continue
                box = fitz.Rect(field["rect"])
                x = (box.x0 - crop.x0) * scale
                y = (box.y0 - crop.y0) * scale
                w = box.width * scale
                h = box.height * scale
                font = "hebo" if field["bold"] else "helv"
                size = field["font_size"] * scale
                if fitz.get_text_length(value, fontname=font, fontsize=size) > w - 2 or size * 1.2 > h:
                    raise StatusDesignError("El texto no cabe en el campo " + field["label"] + ".")
                page.insert_text((x + 1, y + min(h - 1, size * 1.1)), value,
                                 fontname=font, fontsize=size, overlay=True)
            # Proof watermark is always present, regardless of source status.
            mark = "PRUEBA - NO APTO PARA USO GMP"
            page.draw_rect(fitz.Rect(0, 0, width, min(18, height * 0.35)),
                           fill=(1, 0.91, 0.91), color=(0.8, 0.2, 0.2), overlay=True)
            page.insert_text((3, min(12, height * 0.25)), mark, fontsize=min(8, max(4, width/40)),
                             color=(0.7, 0.05, 0.05), overlay=True)
            output.set_metadata({"title": "COVEX - PRUEBA de etiqueta de estado",
                               "subject": "No autorizada para uso GMP"})
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise FileExistsError("No se sobrescribe una prueba existente.")
            output.save(destination, garbage=4, deflate=True)
        finally:
            output.close()
    return destination
