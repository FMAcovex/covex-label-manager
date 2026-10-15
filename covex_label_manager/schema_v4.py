"""Schema v4. Applied only to a staged synthetic/user-approved v3 snapshot."""
import hashlib

# Each element is one statement; never executescript inside the migration transaction.
STATEMENTS=[
'''CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY CHECK(version>0),
 migration_id TEXT NOT NULL UNIQUE,migration_checksum TEXT NOT NULL,
 applied_at TEXT NOT NULL,app_build TEXT NOT NULL)''',
'''CREATE TABLE design_variants(
 id INTEGER PRIMARY KEY,uid TEXT NOT NULL UNIQUE CHECK(length(uid)=32 AND uid NOT GLOB '*[^0-9a-f]*'),
 revision_id INTEGER NOT NULL REFERENCES versions(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
 origin_variant_id INTEGER REFERENCES design_variants(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
 code TEXT NOT NULL CHECK(length(code) BETWEEN 1 AND 40 AND code NOT GLOB '*[^A-Z0-9._-]*' AND code GLOB '[A-Z0-9]*'),
 name TEXT NOT NULL CHECK(length(trim(name))>0),reason TEXT NOT NULL CHECK(length(trim(reason))>0),
 state TEXT NOT NULL DEFAULT 'DRAFT' CHECK(state IN ('DRAFT','PENDING','APPROVED','RETIRED')),
 design_contract INTEGER NOT NULL DEFAULT 1 CHECK(design_contract=1),
 design_json TEXT NOT NULL CHECK(json_valid(design_json) AND json_type(design_json)='object'),
 design_sha256 TEXT NOT NULL CHECK(length(design_sha256)=64 AND design_sha256 NOT GLOB '*[^0-9a-f]*'),
 base_revision_sha256 TEXT NOT NULL CHECK(length(base_revision_sha256)=64 AND base_revision_sha256 NOT GLOB '*[^0-9a-f]*'),
 generation INTEGER NOT NULL DEFAULT 1 CHECK(generation>0),
 created_at TEXT NOT NULL,created_by TEXT NOT NULL,updated_at TEXT NOT NULL,
 approved_by TEXT,approval_ref TEXT,approval_date TEXT,approval_recorded_at TEXT,approval_recorded_by TEXT,
 approved_design_sha256 TEXT,evidence_path TEXT,evidence_sha256 TEXT,
 retired_at TEXT,retired_by TEXT,retirement_reason TEXT,
 UNIQUE(revision_id,code),CHECK(origin_variant_id IS NULL OR origin_variant_id<>id),
 CHECK(COALESCE((approved_by IS NULL AND approval_ref IS NULL AND approval_date IS NULL
 AND approval_recorded_at IS NULL AND approval_recorded_by IS NULL AND approved_design_sha256 IS NULL
 AND evidence_path IS NULL AND evidence_sha256 IS NULL AND state<>'APPROVED')
 OR (length(trim(approved_by))>0 AND length(trim(approval_ref))>0 AND length(approval_date)=10
 AND length(approval_recorded_at)>0 AND length(trim(approval_recorded_by))>0
 AND approved_design_sha256=design_sha256 AND length(evidence_path)>0
 AND length(evidence_sha256)=64 AND evidence_sha256 NOT GLOB '*[^0-9a-f]*' AND state IN ('APPROVED','RETIRED')),0)),
 CHECK(COALESCE((state='RETIRED' AND length(retired_at)>0 AND length(trim(retired_by))>0 AND length(trim(retirement_reason))>0)
 OR (state<>'RETIRED' AND retired_at IS NULL AND retired_by IS NULL AND retirement_reason IS NULL),0)))''',
'CREATE INDEX variants_revision_state ON design_variants(revision_id,state,id)',
'CREATE INDEX variants_origin ON design_variants(origin_variant_id)',
'ALTER TABLE issues ADD COLUMN design_variant_id INTEGER REFERENCES design_variants(id) ON DELETE RESTRICT',
'ALTER TABLE issues ADD COLUMN design_snapshot_json TEXT',
'ALTER TABLE issues ADD COLUMN design_snapshot_sha256 TEXT',
'CREATE INDEX issues_variant ON issues(design_variant_id)',
'''CREATE TRIGGER variants_origin_check BEFORE INSERT ON design_variants
 WHEN new.origin_variant_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM design_variants
 WHERE id=new.origin_variant_id AND revision_id=new.revision_id)
 BEGIN SELECT RAISE(ABORT,'Origen de variante incompatible'); END''',
'''CREATE TRIGGER variants_insert BEFORE INSERT ON design_variants
 WHEN new.state<>'DRAFT' OR new.generation<>1 OR canonical_hash(new.design_json)<>new.design_sha256
 BEGIN SELECT RAISE(ABORT,'Alta de variante inválida'); END''',
'''CREATE TRIGGER variants_no_delete BEFORE DELETE ON design_variants
 BEGIN SELECT RAISE(ABORT,'Las variantes se retiran; no se borran'); END''',
'''CREATE TRIGGER variants_update BEFORE UPDATE ON design_variants
 WHEN new.id IS NOT old.id OR new.uid IS NOT old.uid OR new.revision_id IS NOT old.revision_id
 OR new.origin_variant_id IS NOT old.origin_variant_id OR new.code IS NOT old.code
 OR new.created_at IS NOT old.created_at OR new.created_by IS NOT old.created_by
 OR new.base_revision_sha256 IS NOT old.base_revision_sha256 OR new.design_contract IS NOT old.design_contract
 OR new.generation<>old.generation+1 OR old.state='RETIRED'
 OR NOT ((old.state='DRAFT' AND new.state IN ('DRAFT','PENDING','RETIRED'))
 OR (old.state='PENDING' AND new.state IN ('DRAFT','APPROVED','RETIRED'))
 OR (old.state='APPROVED' AND new.state='RETIRED'))
 OR (old.state<>'DRAFT' AND (new.design_json IS NOT old.design_json OR new.design_sha256 IS NOT old.design_sha256
 OR new.name IS NOT old.name OR new.reason IS NOT old.reason))
 OR canonical_hash(new.design_json)<>new.design_sha256
 BEGIN SELECT RAISE(ABORT,'Variante congelada o transición inválida'); END''',
'''CREATE TRIGGER variants_approval_guard BEFORE UPDATE ON design_variants
 WHEN new.state='APPROVED' AND NOT EXISTS(SELECT 1 FROM versions WHERE id=new.revision_id AND state='APPROVED')
 BEGIN SELECT RAISE(ABORT,'La revisión documental no está aprobada'); END''',
'''CREATE TRIGGER variants_keep_approval BEFORE UPDATE ON design_variants
 WHEN old.state='APPROVED' AND (new.approved_by IS NOT old.approved_by OR new.approval_ref IS NOT old.approval_ref
 OR new.approval_date IS NOT old.approval_date OR new.approval_recorded_at IS NOT old.approval_recorded_at
 OR new.approval_recorded_by IS NOT old.approval_recorded_by OR new.approved_design_sha256 IS NOT old.approved_design_sha256
 OR new.evidence_path IS NOT old.evidence_path OR new.evidence_sha256 IS NOT old.evidence_sha256)
 BEGIN SELECT RAISE(ABORT,'Aprobación inmutable'); END''',
'''CREATE TRIGGER issues_snapshot_insert BEFORE INSERT ON issues
 WHEN new.design_snapshot_json IS NULL OR new.design_snapshot_sha256 IS NULL
 OR NOT json_valid(new.design_snapshot_json) OR json_type(new.design_snapshot_json)<>'object'
 OR json_extract(new.design_snapshot_json,'$.contract') IS NOT 1
 OR json_extract(new.design_snapshot_json,'$.revision_id') IS NOT new.version_id
 OR json_extract(new.design_snapshot_json,'$.variant_id') IS NOT new.design_variant_id
 OR json_type(new.design_snapshot_json,'$.design.layout.fields') IS NOT 'array'
 OR json_type(new.design_snapshot_json,'$.design.layout.crop') IS NOT 'array'
 OR json_array_length(new.design_snapshot_json,'$.design.layout.crop')<>4
 OR json_type(new.design_snapshot_json,'$.design.layout.area') IS NOT 'array'
 OR json_type(new.design_snapshot_json,'$.design.nominal_size_mm') IS NOT 'object'
 OR json_type(new.design_snapshot_json,'$.source') IS NOT 'object'
 OR json_type(new.design_snapshot_json,'$.profile') IS NOT 'object'
 OR json_type(new.design_snapshot_json,'$.revision_approval') IS NOT 'object'
 OR json_extract(new.design_snapshot_json,'$.design_sha256') IS NOT canonical_hash(json_extract(new.design_snapshot_json,'$.design'))
 OR json_extract(new.design_snapshot_json,'$.source.uid') IS NOT (SELECT uid FROM versions WHERE id=new.version_id)
 OR length(new.design_snapshot_sha256)<>64 OR canonical_hash(new.design_snapshot_json)<>new.design_snapshot_sha256
 OR (new.design_variant_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM design_variants
 WHERE id=new.design_variant_id AND revision_id=new.version_id AND state='APPROVED'))
 OR NOT EXISTS(SELECT 1 FROM versions WHERE id=new.version_id AND state='APPROVED')
 BEGIN SELECT RAISE(ABORT,'Emisión sin snapshot válido o diseño no aprobado'); END''',
'''CREATE TRIGGER issues_snapshot_immutable BEFORE UPDATE ON issues
 WHEN new.id IS NOT old.id OR new.uid IS NOT old.uid OR new.version_id IS NOT old.version_id
 OR new.design_variant_id IS NOT old.design_variant_id OR new.design_snapshot_json IS NOT old.design_snapshot_json
 OR new.design_snapshot_sha256 IS NOT old.design_snapshot_sha256
 BEGIN SELECT RAISE(ABORT,'Identidad y snapshot históricos inmutables'); END'''
]
CHECKSUM=hashlib.sha256('\n'.join(STATEMENTS).encode()).hexdigest()


def configure(db):
    from .canonical import json_digest
    db.create_function('canonical_hash',1,lambda value:json_digest(value) if value is not None else None,deterministic=True)
    db.execute('PRAGMA foreign_keys=ON')


def apply(db,at,build):
    configure(db)
    db.execute('BEGIN IMMEDIATE')
    try:
        for sql in STATEMENTS:db.execute(sql)
        db.execute('INSERT INTO schema_migrations VALUES(4,?,?,?,?)',('r3b2_variants_v4',CHECKSUM,at,build))
        for k,v in [('storage_format','4'),('minimum_writer_protocol','4')]:
            if db.execute('SELECT 1 FROM settings WHERE key=?',(k,)).fetchone():raise ValueError('Clave de formato ya existente.')
            db.execute('INSERT INTO settings VALUES(?,?)',(k,v))
        db.execute('PRAGMA user_version=4')
        db.commit()
    except BaseException:
        db.rollback();raise
