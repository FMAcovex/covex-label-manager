"""Library business rules independent of Tk and SQLite."""
import unicodedata
from .contracts import LibraryRepository,FILTER_FIELDS

def searchable(value):
    return ''.join(c for c in unicodedata.normalize('NFD',str(value).casefold()) if unicodedata.category(c)!='Mn')

class LibraryService:
    def __init__(self,repository:LibraryRepository):self.repository=repository

    def entries(self,query='',filters=None,view='all'):
        words=searchable(query).split();filters=filters or {}
        rows=[]
        for row in self.repository.library_records():
            blob=searchable(' '.join(str(value) for value in row.values()))
            if not all(word in blob for word in words):continue
            if any(row.get(k,'')!=v for k,v in filters.items() if v):continue
            if view=='favorites' and not row['favorite']:continue
            if view=='recent' and (not row['last_used'] or row['version_id']!=row['last_version_id']):continue
            rows.append(row)
        if view=='recent':rows.sort(key=lambda r:r['last_used'],reverse=True)
        return rows

    def facets(self):
        rows=self.repository.library_records()
        return {key:sorted({str(r.get(key,'')) for r in rows if r.get(key,'')}) for key in FILTER_FIELDS}

    def favorite(self,row):self.repository.set_favorite(row['id'],not row['favorite'])
    def opened(self,row):self.repository.mark_recent(row['id'],row['version_id'])
    def update_metadata(self,label_id,values,source_ref):
        if not source_ref.strip():raise ValueError('Indique la referencia fuente; no deducimos metadatos del nombre.')
        self.repository.set_label_metadata(label_id,values,source_ref.strip())
