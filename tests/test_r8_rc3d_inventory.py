"""R8-RC3D: folder inventory is cancellable, detached from SQLite/Qt."""
import hashlib
import threading
import pytest
from covex_label_manager.catalog_migration import preview_existing, PreviewCancelled


def test_read_only_inventory_with_plain_snapshot(tmp_path):
    (tmp_path/"FICTICIA_01.pdf").write_bytes(b"%PDF-synthetic-not-for-production")
    report=preview_existing([],tmp_path)
    assert report["mode"]=="REVIEW_ONLY"
    assert len(report["files"])==1
    assert report["files"][0]["sha256"]==hashlib.sha256(b"%PDF-synthetic-not-for-production").hexdigest()
    assert report["files"][0]["status"]=="REVIEW_REQUIRED"


def test_folder_scan_can_cancel_without_writes(tmp_path):
    original=tmp_path/"DOCUMENTO.pdf"
    original.write_bytes(b"synthetic sample")
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    with pytest.raises(PreviewCancelled):
        preview_existing([],tmp_path,interrupt=lambda: True)
    assert hashlib.sha256(original.read_bytes()).hexdigest()==digest


def test_threaded_inventory_needs_no_sqlite_handle(tmp_path):
    (tmp_path/"FICTICIO.pdf").write_bytes(b"fictional")
    result=[]
    worker=threading.Thread(target=lambda:result.append(preview_existing([],tmp_path)))
    worker.start();worker.join(timeout=5)
    assert not worker.is_alive()
    assert len(result)==1 and result[0]["files"][0]["status"]=="REVIEW_REQUIRED"
