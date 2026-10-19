"""Independent, local R7A status-label catalogue.

The R3/R6 product-label SQLite v4 is never modified: the status catalogue has
its own sidecar SQLite schema, included in ordinary data-folder backups.
No SharePoint, product records, QA disposition or electronic signature.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sqlite3
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import fitz

from .canonical import canonical, digest
from .importer import docx_to_pdf
from .status_design import KINDS, StatusDesignError, validate_layout, validate_values
from .storage import sha256


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _row(row):
    return dict(row) if row is not None else None


def _require_note(text, name, n=3):
    if not isinstance(text, str) or len(text.strip()) < n or len(text) > 500:
        raise ValueError(name + ": indique un valor documentado válido.")
    return text.strip()


def _allowed_path(root, relative):
    if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Ruta documental inválida.")
    parent = root.resolve()
    path = (parent / relative).resolve()
    if not path.is_relative_to(parent):
        raise ValueError("Ruta documental fuera del catálogo.")
    return path


class StatusCatalogue:
    """One identity per status type, many immutable documentary revisions."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.db_path = self.root / "status_catalog.sqlite"
        self._schema_stamp = None

    @contextmanager
    def _connect(self):
        self.root.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.db_path, timeout=10)
        try:
            self._prepare_connection(db)
            with db:
                yield db
        finally:
            # Includes initialization/DDL failures and process interruption,
            # not only errors raised by the caller after yield.
            db.close()

    def _prepare_connection(self, db):
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=10000")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise ValueError("Catálogo de estados de una versión incompatible.")
        stat = self.db_path.stat()
        stamp = (stat.st_dev, stat.st_ino,
                 db.execute("PRAGMA schema_version").fetchone()[0])
        if version == 1 and stamp == self._schema_stamp:
            return
        db.executescript("""
        CREATE TABLE IF NOT EXISTS status_revisions(
          uid TEXT PRIMARY KEY CHECK(length(uid)=32),
          kind TEXT NOT NULL CHECK(kind IN ('sin_analizar','aprobado','rechazado')),
          revision TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'DRAFT'
            CHECK(state IN ('DRAFT','PENDING','APPROVED','RETIRED','CANCELLED')),
          source_path TEXT NOT NULL, source_sha TEXT NOT NULL,
          pdf_path TEXT NOT NULL, pdf_sha TEXT NOT NULL,
          layout_json TEXT NOT NULL, layout_sha TEXT NOT NULL,
          created_at TEXT NOT NULL, modified_at TEXT NOT NULL,
          approval_ref TEXT, approved_by TEXT, approved_at TEXT,
          retired_at TEXT, retired_reason TEXT,
          UNIQUE(kind,revision)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS status_one_vigente
          ON status_revisions(kind) WHERE state='APPROVED';
        CREATE TABLE IF NOT EXISTS status_issues(
          uid TEXT PRIMARY KEY CHECK(length(uid)=32),
          revision_uid TEXT NOT NULL REFERENCES status_revisions(uid),
          created_at TEXT NOT NULL,
          operator TEXT NOT NULL, pdf_path TEXT NOT NULL,
          pdf_sha TEXT NOT NULL, snapshot_json TEXT NOT NULL,
          origin_issue_uid TEXT REFERENCES status_issues(uid), reason TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS status_issues_by_revision
          ON status_issues(revision_uid,created_at);
        CREATE TABLE IF NOT EXISTS status_audit(
          uid TEXT PRIMARY KEY, at TEXT NOT NULL, event TEXT NOT NULL,
          subject TEXT NOT NULL, detail TEXT NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS status_revision_protected
          BEFORE UPDATE ON status_revisions
          WHEN old.state NOT IN ('DRAFT','PENDING') AND (
            new.kind IS NOT old.kind OR new.revision IS NOT old.revision
            OR new.source_path IS NOT old.source_path
            OR new.source_sha IS NOT old.source_sha
            OR new.pdf_path IS NOT old.pdf_path OR new.pdf_sha IS NOT old.pdf_sha
            OR new.layout_json IS NOT old.layout_json
            OR new.layout_sha IS NOT old.layout_sha
            OR new.approval_ref IS NOT old.approval_ref
            OR new.approved_by IS NOT old.approved_by
            OR new.approved_at IS NOT old.approved_at
            OR new.created_at IS NOT old.created_at
          )
          BEGIN SELECT RAISE(ABORT,'Revision documental protegida'); END;
        CREATE TRIGGER IF NOT EXISTS status_no_delete
          BEFORE DELETE ON status_revisions
          BEGIN SELECT RAISE(ABORT,'Se conserva el historial documental'); END;
        CREATE TRIGGER IF NOT EXISTS status_issues_no_update
          BEFORE UPDATE ON status_issues
          BEGIN SELECT RAISE(ABORT,'La emision historica es inmutable'); END;
        CREATE TRIGGER IF NOT EXISTS status_issues_no_delete
          BEFORE DELETE ON status_issues
          BEGIN SELECT RAISE(ABORT,'No se borran emisiones historicas'); END;
        """)
        db.execute("PRAGMA user_version=1")
        db.commit()
        self._schema_stamp = (stat.st_dev, stat.st_ino,
                              db.execute("PRAGMA schema_version").fetchone()[0])

    def _audit(self, db, event, subject, detail):
        db.execute("INSERT INTO status_audit VALUES(?,?,?,?,?)",
                   (uuid.uuid4().hex, _now(), event, subject, canonical(detail)))

    def list_revisions(self, kind=None):
        if kind is not None and kind not in KINDS:
            raise ValueError("Tipo de estado desconocido.")
        with self._connect() as db:
            sql = "SELECT * FROM status_revisions"
            args = ()
            if kind is not None:
                sql += " WHERE kind=?"
                args = (kind,)
            return [_row(r) for r in db.execute(sql + " ORDER BY created_at DESC, rowid DESC", args)]

    def get(self, uid):
        with self._connect() as db:
            record = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?", (uid,)).fetchone())
        if record is None:
            raise ValueError("Revisión de etiqueta de estado inexistente.")
        return record

    def current(self, kind):
        if kind not in KINDS:
            raise ValueError("Tipo de estado desconocido.")
        with self._connect() as db:
            return _row(db.execute("SELECT * FROM status_revisions WHERE kind=? AND state='APPROVED'",
                                   (kind,)).fetchone())

    def _verified(self, record):
        pdf = _allowed_path(self.root, record["pdf_path"])
        original = _allowed_path(self.root, record["source_path"])
        if not pdf.is_file() or not original.is_file():
            raise ValueError("Falta el original o PDF maestro de estado.")
        if sha256(pdf) != record["pdf_sha"] or sha256(original) != record["source_sha"]:
            raise ValueError("La fuente documental de estado ha cambiado.")
        layout = json.loads(record["layout_json"])
        if digest(layout) != record["layout_sha"]:
            raise ValueError("La geometría de estado ha cambiado.")
        with fitz.open(pdf) as doc:
            if validate_layout(layout, doc) != layout:
                raise ValueError("El diseño guardado no es canónico.")
        return pdf, layout

    def verify(self, uid):
        rec = self.get(uid)
        self._verified(rec)
        return rec

    def import_many(self, source, entries):
        """Import one PDF/DOCX as any subset of 3 *independent* DRAFT revisions.

        entries: dicts {kind,revision,layout}. Each layout has its own page/crop
        and fields, but can reference the same immutable source PDF.
        """
        source = Path(source).resolve()
        if not source.is_file() or source.name.startswith("~$") or source.suffix.lower() not in (".pdf", ".docx"):
            raise ValueError("Seleccione un PDF o DOCX local válido.")
        if source.stat().st_size > 50_000_000:
            raise ValueError("Documento demasiado grande.")
        if not isinstance(entries, list) or not 1 <= len(entries) <= 3:
            raise ValueError("Seleccione entre uno y tres diseños.")
        kinds = [e.get("kind") for e in entries if isinstance(e, dict)]
        if len(kinds) != len(entries) or len(set(kinds)) != len(kinds) or not set(kinds) <= set(KINDS):
            raise ValueError("Cada etiqueta debe tener un estado distinto.")
        with tempfile.TemporaryDirectory(prefix="covex-status-") as tmp:
            pdf_file = Path(docx_to_pdf(source, tmp))
            with fitz.open(pdf_file) as doc:
                if doc.is_encrypted or not 1 <= len(doc) <= 100:
                    raise ValueError("PDF de estado inaccesible.")
                normalized = []
                for e in entries:
                    revision = _require_note(e.get("revision"), "Revisión documental", 1)
                    if len(revision) > 40 or "/" in revision or "\\" in revision:
                        raise ValueError("Código de revisión inválido.")
                    layout = validate_layout(e.get("layout"), doc)
                    if layout["kind"] != e["kind"]:
                        raise ValueError("La identidad y el recorte no corresponden.")
                    normalized.append((e["kind"], revision, layout))
            source_hash, pdf_hash = sha256(source), sha256(pdf_file)
            target_dir = self.root / "status_masters" / "r7a"
            target_dir.mkdir(parents=True, exist_ok=True)
            originals = [(source, target_dir / (source_hash + source.suffix.lower())),
                         (pdf_file, target_dir / (pdf_hash + ".pdf"))]
            created = []
            uids = []
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                try:
                    for kind, revision, layout in normalized:
                        if db.execute("SELECT 1 FROM status_revisions WHERE kind=? AND revision=?",
                                      (kind, revision)).fetchone():
                            raise ValueError("Esta revisión ya figura en la Biblioteca de estados.")
                    for original, dest in originals:
                        if dest.exists():
                            if sha256(dest) != sha256(original):
                                raise ValueError("Conflicto de integridad en archivo de estado.")
                        else:
                            temporary = dest.with_suffix(dest.suffix + "." + uuid.uuid4().hex + ".tmp")
                            try:
                                shutil.copyfile(original, temporary)
                                if sha256(temporary) != sha256(original):
                                    raise ValueError("Copia documental no íntegra.")
                                os.replace(temporary, dest)
                                created.append(dest)
                            finally:
                                temporary.unlink(missing_ok=True)
                    for kind, revision, layout in normalized:
                        uid = uuid.uuid4().hex
                        rel_original = originals[0][1].relative_to(self.root).as_posix()
                        rel_pdf = originals[1][1].relative_to(self.root).as_posix()
                        db.execute("""INSERT INTO status_revisions(
                          uid,kind,revision,state,source_path,source_sha,pdf_path,pdf_sha,
                          layout_json,layout_sha,created_at,modified_at)
                          VALUES(?,?,?,'DRAFT',?,?,?,?,?,?,?,?)""",
                                   (uid, kind, revision, rel_original, source_hash,
                                    rel_pdf, pdf_hash, canonical(layout), digest(layout),
                                    _now(), _now()))
                        self._audit(db, "IMPORT_DRAFT", uid, {"kind": kind, "revision": revision,
                                        "source_sha": source_hash, "pdf_sha": pdf_hash})
                        uids.append(uid)
                    db.commit()
                except Exception:
                    db.rollback()
                    for dest in created:
                        dest.unlink(missing_ok=True)
                    raise
            return uids

    def new_revision(self, base_uid, revision, reason):
        """Clone a documented revision as a new independent DRAFT.

        The existing source PDF and its bytes are referenced, never replaced.
        A cloned layout never inherits approval or claims documentary vigencia.
        """
        revision = _require_note(revision, "Nueva revisión", 1)
        reason = _require_note(reason, "Motivo de nueva revisión", 5)
        if len(revision) > 40 or "/" in revision or "\\" in revision:
            raise ValueError("Código de revisión inválido.")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            original = _row(db.execute(
                "SELECT * FROM status_revisions WHERE uid=?", (base_uid,)).fetchone())
            if not original or original["state"] == "CANCELLED":
                raise ValueError("Revisión original inexistente o anulada.")
            self._verified(original)
            if db.execute("SELECT 1 FROM status_revisions WHERE kind=? AND revision=?",
                          (original["kind"], revision)).fetchone():
                raise ValueError("La nueva revisión ya existe para este estado.")
            uid = uuid.uuid4().hex
            db.execute("""INSERT INTO status_revisions(
                    uid,kind,revision,state,source_path,source_sha,pdf_path,pdf_sha,
                    layout_json,layout_sha,created_at,modified_at)
                    VALUES(?,?,?,'DRAFT',?,?,?,?,?,?,?,?)""",
                       (uid, original["kind"], revision,
                        original["source_path"], original["source_sha"],
                        original["pdf_path"], original["pdf_sha"],
                        original["layout_json"], original["layout_sha"], _now(), _now()))
            self._audit(db, "CLONE_STATUS_REVISION", uid,
                        {"source_uid": base_uid, "reason": reason})
            db.commit()
            return uid

    def save_draft(self, uid, layout, *, expected_layout_sha=None):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rec = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?", (uid,)).fetchone())
            if rec is None or rec["state"] != "DRAFT":
                raise PermissionError("Solo se modifica un borrador de etiqueta de estado.")
            if expected_layout_sha is not None and rec['layout_sha'] != expected_layout_sha:
                raise ValueError("Otro editor cambió este borrador. Sus cambios siguen en pantalla; cierre sin sobrescribir y vuelva a abrir para cotejarlos.")
            self._verified(rec)
            with fitz.open(_allowed_path(self.root, rec["pdf_path"])) as doc:
                layout = validate_layout(layout, doc)
            if layout["kind"] != rec["kind"]:
                raise ValueError("No se permite cambiar el tipo de etiqueta.")
            db.execute("UPDATE status_revisions SET layout_json=?,layout_sha=?,modified_at=? WHERE uid=?",
                       (canonical(layout), digest(layout), _now(), uid))
            self._audit(db, "UPDATE_DRAFT", uid, {"layout_sha": digest(layout)})
            db.commit()

    def submit(self, uid):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rec = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?", (uid,)).fetchone())
            if rec is None or rec["state"] != "DRAFT":
                raise PermissionError("Solo los borradores pueden enviarse a revisión.")
            self._verified(rec)
            db.execute("UPDATE status_revisions SET state='PENDING',modified_at=? WHERE uid=?", (_now(), uid))
            self._audit(db, "SUBMIT_DOCUMENT", uid, {})
            db.commit()

    def approve(self, uid, reviewer, reference, *, confirmation=False, replacement_reason=None):
        if confirmation is not True:
            raise PermissionError("Confirme el cotejo con documento aprobado externamente.")
        reviewer = _require_note(reviewer, "Responsable")
        reference = _require_note(reference, "Referencia de aprobación", 5)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rec = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?", (uid,)).fetchone())
            if rec is None or rec["state"] != "PENDING":
                raise PermissionError("La revisión no está pendiente de aprobación.")
            self._verified(rec)
            older = db.execute("SELECT uid FROM status_revisions WHERE kind=? AND state='APPROVED'",
                               (rec["kind"],)).fetchone()
            if older:
                replacement_reason = _require_note(replacement_reason, "Motivo de sustitución", 5)
                db.execute("""UPDATE status_revisions SET state='RETIRED',
                  retired_at=?,retired_reason=?,modified_at=? WHERE uid=?""",
                           (_now(), replacement_reason, _now(), older["uid"]))
                self._audit(db, "RETIRE_REPLACED", older["uid"], {"new_uid": uid, "reason": replacement_reason})
            db.execute("""UPDATE status_revisions SET state='APPROVED',
                approved_by=?,approval_ref=?,approved_at=?,modified_at=? WHERE uid=?""",
                       (reviewer, reference, _now(), _now(), uid))
            self._audit(db, "RECORD_EXTERNAL_APPROVAL", uid, {"reviewer": reviewer, "reference": reference})
            db.commit()

    def retire(self, uid, reason):
        reason = _require_note(reason, "Motivo de retirada", 5)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rec = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?", (uid,)).fetchone())
            if rec is None or rec["state"] not in ("APPROVED", "PENDING"):
                raise PermissionError("Esta revisión no puede retirarse.")
            db.execute("""UPDATE status_revisions SET state='RETIRED',
                retired_at=?,retired_reason=?,modified_at=? WHERE uid=?""",
                       (_now(), reason, _now(), uid))
            self._audit(db, "RETIRE_STATUS", uid, {"reason": reason})
            db.commit()

    def _sheet(self, record, data, destination, *, count=1, paper="A4",
               width_mm=None, margin_mm=8, gap_mm=3, proof=False, height_mm=None, composition=None):
        pdf, design = self._verified(record)
        values = validate_values(design, data, strict=not proof)
        if type(count) is not int or not 1 <= count <= 500:
            raise ValueError("Número de etiquetas entre 1 y 500.")
        sizes = {"A4": (210, 297), "A3": (297, 420), "A5": (148, 210), "Carta": (215.9, 279.4)}
        if paper not in sizes:
            raise ValueError("Formato de hoja no admitido.")
        from .status_design import _finite, MM_PER_POINT
        margin = _finite(margin_mm, "Margen", minimum=0, maximum=40)
        gap = _finite(gap_mm, "Separación", minimum=0, maximum=40)
        label_width = (_finite(width_mm, "Ancho", minimum=10, maximum=500)
                       if width_mm is not None else design["size_mm"][0])
        label_height = label_width * design["size_mm"][1] / design["size_mm"][0]
        if height_mm is not None:
            label_height=_finite(height_mm,'Alto',minimum=8,maximum=500)
        paper_w, paper_h = sizes[paper]
        cols = math.floor((paper_w - 2 * margin + gap + 1e-7) / (label_width + gap))
        rows = math.floor((paper_h - 2 * margin + gap + 1e-7) / (label_height + gap))
        if cols < 1 or rows < 1:
            raise ValueError("La etiqueta no cabe con el margen y formato seleccionados.")
        destination = Path(destination)
        if destination.exists():
            raise FileExistsError("No se sobrescribe ninguna emisión.")
        source_crop = fitz.Rect(design["crop"])
        with fitz.open(pdf) as source:
            out = fitz.open()
            composition_report=None
            try:
                capacity = cols * rows
                for number in range(count):
                    if number % capacity == 0:
                        page = out.new_page(width=paper_w/MM_PER_POINT, height=paper_h/MM_PER_POINT)
                    i = number % capacity
                    x = (margin + (i % cols) * (label_width + gap)) / MM_PER_POINT
                    y = (margin + (i // cols) * (label_height + gap)) / MM_PER_POINT
                    rect = fitz.Rect(x, y, x + label_width/MM_PER_POINT, y + label_height/MM_PER_POINT)
                    enhanced=design['contract']==2 or composition is not None or height_mm is not None
                    if enhanced:
                        from .status_scaling import paint
                        composition_report=paint(page,source,design,values,rect,settings=composition,strict=not proof)
                    else:page.show_pdf_page(rect, source, design["page"], clip=source_crop, keep_proportion=True)
                    scale = rect.width / source_crop.width
                    for field in ([] if enhanced else design["fields"]):
                        value = values[field["key"]]
                        if not value:
                            continue
                        fr = fitz.Rect(field["rect"])
                        tx = rect.x0 + (fr.x0 - source_crop.x0) * scale
                        ty = rect.y0 + (fr.y0 - source_crop.y0) * scale
                        fs = field["font_size"] * scale
                        font = "hebo" if field["bold"] else "helv"
                        if fitz.get_text_length(value, fontname=font, fontsize=fs) > fr.width * scale - 2:
                            raise StatusDesignError("Dato desbordado: " + field["label"])
                        if fs * 1.2 > fr.height * scale:
                            raise StatusDesignError("Altura insuficiente: " + field["label"])
                        page.insert_text((tx + 1, ty + fs * 1.1), value, fontname=font, fontsize=fs)
                    if proof:
                        warning = "PRUEBA - NO APTO PARA USO GMP"
                        strip = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + min(16, rect.height * 0.24))
                        page.draw_rect(strip, color=(0.85, 0.1, 0.1), fill=(1, 0.9, 0.9))
                        page.insert_text((strip.x0 + 3, strip.y0 + min(11, strip.height * 0.8)),
                                         warning, fontsize=7, color=(0.7, 0, 0))
                metadata={"title": "COVEX - " + ("PRUEBA NO GMP" if proof else "Etiqueta de estado")}
                if composition_report:
                    from .status_scaling import describe
                    metadata['subject']=describe(composition_report)+' · '+' · '.join(composition_report['warnings'])
                out.set_metadata(metadata)
                destination.parent.mkdir(parents=True, exist_ok=True)
                out.save(destination, deflate=True, garbage=4)
            finally:
                out.close()
        return destination

    def preview(self, revision_uid, values=None, **settings):
        record = self.get(revision_uid)
        dest = self.root / "cache" / ("status-proof-" + uuid.uuid4().hex + ".pdf")
        return self._sheet(record, values or {}, dest, proof=True, **settings)

    def emit(self, revision_uid, values, operator, *, count=1, paper="A4",
             width_mm=None, margin_mm=8, gap_mm=3, height_mm=None, composition=None):
        operator = _require_note(operator, "Operador")
        record = self.get(revision_uid)
        if record["state"] != "APPROVED":
            raise PermissionError("Solo puede emitirse la revisión vigente documentalmente.")
        self._verified(record)
        config = {"count": count, "paper": paper, "width_mm": width_mm,
                  "margin_mm": margin_mm, "gap_mm": gap_mm}
        if height_mm is not None:config['height_mm']=height_mm
        if composition is not None:config['composition']=composition
        dest = self.root / "emissions" / ("status-" + uuid.uuid4().hex + ".pdf")
        self._sheet(record, values, dest, proof=False, **config)
        try:
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                updated = _row(db.execute("SELECT * FROM status_revisions WHERE uid=?",
                                           (revision_uid,)).fetchone())
                if updated != record or updated["state"] != "APPROVED":
                    raise PermissionError("La revisión de estado ha cambiado desde la vista previa.")
                self._verified(updated)
                pdf_sha = sha256(dest)
                snapshot = {"contract": 1, "revision_uid": revision_uid,
                            "kind": record["kind"], "revision": record["revision"],
                            "source_sha": record["source_sha"], "pdf_sha": record["pdf_sha"],
                            "layout_sha": record["layout_sha"], "layout": json.loads(record["layout_json"]),
                            "values": validate_values(json.loads(record["layout_json"]), values),
                            "profile": config, "approval_ref": record["approval_ref"]}
                issue_uid = uuid.uuid4().hex
                db.execute("""INSERT INTO status_issues
                  (uid,revision_uid,created_at,operator,pdf_path,pdf_sha,snapshot_json)
                  VALUES(?,?,?,?,?,?,?)""",
                           (issue_uid, revision_uid, _now(), operator,
                            dest.relative_to(self.root).as_posix(), pdf_sha, canonical(snapshot)))
                self._audit(db, "ISSUE_STATUS_ONLY", issue_uid,
                            {"revision_uid": revision_uid, "pdf_sha": pdf_sha})
                db.commit()
            return issue_uid, dest
        except Exception:
            dest.unlink(missing_ok=True)
            raise

    def issues(self):
        with self._connect() as db:
            return [_row(r) for r in db.execute(
                """SELECT i.*,r.kind,r.revision FROM status_issues i
                JOIN status_revisions r ON r.uid=i.revision_uid
                ORDER BY i.created_at DESC,i.rowid DESC""")]

    def inspect_issue(self, issue_uid):
        """Verify the exact stored PDF and historical revision identity."""
        with self._connect() as db:
            record = _row(db.execute(
                """SELECT i.*,r.kind,r.revision,r.source_sha,r.pdf_sha AS master_sha,
                          r.layout_sha FROM status_issues i
                   JOIN status_revisions r ON r.uid=i.revision_uid
                   WHERE i.uid=?""", (issue_uid,)).fetchone())
        if record is None:
            raise ValueError("Emisión independiente inexistente.")
        path = _allowed_path(self.root, record["pdf_path"])
        if not path.is_file() or sha256(path) != record["pdf_sha"]:
            raise ValueError("El PDF histórico ha desaparecido o no coincide con su hash.")
        snapshot = json.loads(record["snapshot_json"])
        if (snapshot.get("contract") != 1
                or snapshot.get("revision_uid") != record["revision_uid"]
                or snapshot.get("kind") != record["kind"]
                or snapshot.get("revision") != record["revision"]
                or snapshot.get("source_sha") != record["source_sha"]
                or snapshot.get("pdf_sha") != record["master_sha"]
                or snapshot.get("layout_sha") != record["layout_sha"]):
            raise ValueError("El snapshot histórico no corresponde a la revisión emitida.")
        return record, path

    def reprint(self, issue_uid, operator, reason):
        operator = _require_note(operator, "Operador")
        reason = _require_note(reason, "Motivo de reimpresión", 5)
        with self._connect() as db:
            original = _row(db.execute("SELECT * FROM status_issues WHERE uid=?",
                                       (issue_uid,)).fetchone())
            if not original:
                raise ValueError("Emisión histórica no encontrada.")
            source = _allowed_path(self.root, original["pdf_path"])
            if not source.is_file() or sha256(source) != original["pdf_sha"]:
                raise ValueError("PDF histórico ausente o modificado; reimpresión bloqueada.")
            dest = self.root / "emissions" / ("status-reprint-" + uuid.uuid4().hex + ".pdf")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            try:
                if sha256(dest) != original["pdf_sha"]:
                    raise ValueError("La copia histórica no coincide.")
                new_uid = uuid.uuid4().hex
                with db:
                    db.execute("""INSERT INTO status_issues
                      (uid,revision_uid,created_at,operator,pdf_path,pdf_sha,snapshot_json,origin_issue_uid,reason)
                      VALUES(?,?,?,?,?,?,?,?,?)""",
                               (new_uid, original["revision_uid"], _now(), operator,
                                dest.relative_to(self.root).as_posix(), original["pdf_sha"],
                                original["snapshot_json"], issue_uid, reason))
                    self._audit(db, "REPRINT_STATUS_ONLY", new_uid,
                                {"original": issue_uid, "reason": reason})
                return new_uid, dest
            except Exception:
                dest.unlink(missing_ok=True)
                raise
