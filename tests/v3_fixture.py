"""Offline test-only v3 builder; bypasses the v4 constructor, not application paths."""
import sqlite3
from pathlib import Path
from covex_label_manager.storage import Store


def create(root,seed=True):
    s=Store.__new__(Store);s.root=Path(root);s.root.mkdir(parents=True,exist_ok=True)
    for name in ('sources','pdf_masters','status_masters','emissions','backups','cache'):(s.root/name).mkdir(exist_ok=True)
    s.db_file=s.root/'labels.sqlite';s.db=sqlite3.connect(s.db_file);s.db.row_factory=sqlite3.Row
    s.db.execute('PRAGMA foreign_keys=ON');s._schema()
    if seed:s.seed_data();s._seed_r1_variant()
    return s


def add_legacy_issue(s,version_id,operator,count,copies,indices,values,profile,pdf_path,source_issue_id=None,reason='',per_container=None,status=None):
    import json
    from covex_label_manager.storage import now,sha256
    with s.txn() as c:
        cur=c.execute('''INSERT INTO issues(version_id,created_at,operator,count_containers,copies_per_container,
        selected_indices,variables_json,profile_json,pdf_path,source_issue_id,reason,per_container_json,status_json,pdf_sha256)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(version_id,now(),operator,count,copies,json.dumps(indices),json.dumps(values),json.dumps(profile),
        str(Path(pdf_path).relative_to(s.root)),source_issue_id,reason,json.dumps(per_container or {}),json.dumps(status or {}),sha256(pdf_path)))
    return cur.lastrowid
