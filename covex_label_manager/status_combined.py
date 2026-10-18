"""R7B: opt-in bridge between approved R7A state revisions and combined emission.

The old status_masters table is left untouched. New revisions are never selected
silently, and no state is inferred from a product's quality disposition.
"""
from __future__ import annotations

import json
from pathlib import Path

from .status_catalog import StatusCatalogue
from .status_design import validate_values
from .canonical import digest


def resolve_status(store, status, *, historical=None):
    """Resolve an explicit state revision; otherwise preserve legacy behaviour.

    An archival snapshot may authorize *inspection* of a retired revision, but
    this resolver never re-approves it for new production.
    """
    status = status or {}
    kind = status.get("kind", "ninguna")
    if kind == "ninguna":
        if status.get("revision_uid"):
            raise ValueError("Una etiqueta sin estado no admite revisión documental.")
        return None
    uid = status.get("revision_uid")
    if not uid:
        if historical is not None:
            raise ValueError("No se admite histórico de estado R7A sin identidad.")
        return store.status_master(kind)
    if not isinstance(uid, str) or len(uid) != 32 or any(c not in "0123456789abcdef" for c in uid):
        raise ValueError("Identidad de revisión de estado inválida.")
    catalog = StatusCatalogue(store.root)
    rec = catalog.verify(uid)
    if rec["kind"] != kind:
        raise ValueError("La revisión seleccionada pertenece a otro tipo de etiqueta de estado.")
    if rec["state"] != "APPROVED":
        if historical is None or rec["state"] != "RETIRED":
            raise PermissionError("La revisión de estado no está vigente: emisión combinada bloqueada.")
    if not rec["approved_at"] or not rec["approval_ref"]:
        raise PermissionError("No existe aprobación documental externa registrada.")
    layout = json.loads(rec["layout_json"])
    vals = status.get("fields", {})
    if not isinstance(vals, dict):
        raise ValueError("Los campos variables del estado deben ser un objeto.")
    # Source-specific field requirements are validated at render time too,
    # after per-container values (e.g. lote) have been merged.
    if set(vals) - {f["key"] for f in layout["fields"]}:
        raise ValueError("Existen datos de estado ajenos al diseño aprobado.")
    asset = {
        "kind": rec["kind"], "name": rec["kind"], "version": rec["revision"],
        "state": "APPROVED", "master_pdf": rec["pdf_path"],
        "original_file": rec["source_path"], "pdf_sha256": rec["pdf_sha"],
        "source_sha256": rec["source_sha"], "crop_json": json.dumps(layout["crop"]),
        "approved_by": rec["approved_by"], "approval_ref": rec["approval_ref"],
        "approved_at": rec["approved_at"], "r7b_uid": uid,
        "r7b_layout": layout, "r7b_layout_sha": rec["layout_sha"],
        "r7b_source_sha": rec["source_sha"],
    }
    if historical is not None:
        # Historic approvals can survive retirement but never be replaced.
        # Evidence comes from an immutable, hash-verified issue snapshot.
        if not isinstance(historical, dict) or asset != historical:
            raise ValueError("La fuente histórica de estado ya no coincide.")
    return asset


def status_fingerprint(store, status):
    asset = resolve_status(store, status)
    if asset is None:
        return None
    return digest(dict(asset))


def field_values(layout, material_values, status, *, strict):
    values = {}
    state_values = status.get("fields", {})
    if not isinstance(state_values, dict):
        raise ValueError("Datos de estado inválidos.")
    for field in layout["fields"]:
        key = field["key"]
        value = state_values.get(key)
        if value is None:
            value = status.get(key)
        if value is None and key == "lote":
            value = material_values.get("lote")
        if value is None:
            value = ""
        values[key] = value
    return validate_values(layout, values, strict=strict)
