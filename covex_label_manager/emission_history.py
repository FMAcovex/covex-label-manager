"""History/reprint coordination shared by Qt and Tk. No schema or PDF compositor."""
import json
import uuid
from .canonical import digest,json_digest
from .editor_layout import source_identity
from .emission_selection import parse_ranges
from .storage import sha256

LEGACY_WARNING='Registro heredado sin snapshot: se usará la revisión documentada actual. No se acredita reproducción exacta del diseño histórico.'


def original(store,issue_id):
    row=store.issue(issue_id)
    if row is None:raise ValueError('La emisión seleccionada ya no existe.')
    row=dict(row);path=(store.root/row['pdf_path']).resolve()
    if not path.is_relative_to(store.root.resolve()/'emissions'):raise ValueError('Ruta del PDF histórico fuera de emisiones.')
    if not path.is_file():raise ValueError('No se encuentra el PDF histórico. Restaure una copia verificada.')
    if row['pdf_sha256'] and sha256(path)!=row['pdf_sha256']:raise ValueError('El PDF histórico ha sido modificado. Apertura y reimpresión bloqueadas.')
    snap=None
    if row['design_snapshot_json'] is not None:
        if not row['design_snapshot_sha256'] or json_digest(row['design_snapshot_json'])!=row['design_snapshot_sha256']:raise ValueError('Integridad del snapshot comprometida.')
        snap=json.loads(row['design_snapshot_json'])
        if snap.get('contract')!=1 or snap.get('revision_id')!=row['version_id'] or snap.get('variant_id')!=row['design_variant_id'] or digest(snap['design'])!=snap['design_sha256']:raise ValueError('Identidad o diseño del snapshot incompatible.')
        if digest(snap['profile'])!=json_digest(row['profile_json']) or digest(snap['status'])!=json_digest(row['status_json'] or '{}'):raise ValueError('Perfil o estado histórico incompatible con el snapshot.')
    elif row['design_snapshot_sha256'] is not None:raise ValueError('Snapshot histórico incompleto.')
    # Includes even legacy PDFs without a registered digest in the review token.
    return row,path,snap,digest([row,sha256(path)])


def reprint_document(api,row,snap):
    v=api.resolved_design(row['version_id'],row['design_variant_id'],True)
    if snap:
        current_variant=api.variant(row['design_variant_id']) if row['design_variant_id'] else None
        if snap['revision_uid']!=v['uid'] or snap['source']!=source_identity(v) or snap['variant_uid']!=(current_variant['uid'] if current_variant else None):raise ValueError('La identidad documental ya no corresponde al snapshot histórico.')
        from .emission_contract import snapshot
        current=snapshot(api._repository,v['id'],row['design_variant_id'],snap['profile'],snap['status'],None,
                         historical_status=snap.get('status_master') if snap['status'].get('revision_uid') else None)
        # Approved designs/evidence cannot be substituted under an old identity.
        if any(digest(current[k])!=digest(snap[k]) for k in ('design','design_sha256','revision_approval','variant_approval','generation','status_master')):raise ValueError('El diseño o su aprobación documental cambió. Reimpresión bloqueada.')
    return v


class HistoryService:
    def __init__(self,api):self.api=api
    def inspect(self,issue_id):
        row,path,snap,fingerprint=original(self.api._repository,issue_id)
        warnings=[];blocked=None
        if snap is None:warnings.append(LEGACY_WARNING)
        if not row['pdf_sha256']:warnings.append('PDF heredado sin hash registrado. No se acredita su integridad retrospectiva.')
        try:
            v=reprint_document(self.api,row,snap)
            from .emission_contract import snapshot
            document_token=digest(snapshot(self.api._repository,v['id'],row['design_variant_id'],json.loads(row['profile_json']),json.loads(row['status_json'] or '{}'),None,
                     historical_status=snap.get('status_master') if snap and snap['status'].get('revision_uid') else None))
        except (ValueError,OSError,KeyError,TypeError) as ex:blocked=str(ex);document_token=None
        return {'issue':row,'path':path,'snapshot':snap,'warnings':warnings,'reprint_allowed':blocked is None,
            'blocked':blocked,'token':digest([fingerprint,document_token])}
    def prepare(self,issue_id,selection,reason,start_slot=1,acknowledge_legacy=False,expected_token=None):
        report=self.inspect(issue_id)
        if expected_token is not None and report['token']!=expected_token:raise ValueError('La emisión o la documentación cambió. Vuelva a comprobarla.')
        if not report['reprint_allowed']:raise PermissionError(report['blocked'])
        if report['warnings'] and not acknowledge_legacy:raise PermissionError('Confirme expresamente las advertencias del registro heredado antes de reimprimir.')
        if len(reason.strip())<5:raise ValueError('Indique un motivo de reimpresión de al menos 5 caracteres.')
        row=report['issue'];indices=parse_ranges(selection,row['count_containers'])
        if not set(indices).issubset(json.loads(row['selected_indices'])):raise ValueError('Seleccione solo números incluidos en esta emisión; se conserva la numeración original.')
        profile=json.loads(row['profile_json'])
        try:
            slot=int(str(start_slot))
            if str(slot)!=str(start_slot).strip():raise ValueError()
        except (ValueError,TypeError):raise ValueError('La casilla inicial debe ser un entero.')
        profile['start_slot']=slot;plan=self.api.sheet_plan(profile,len(indices)*row['copies_per_container'])
        return report,indices,profile,plan
    def reproduce(self,issue_id,selection,reason,operator,*,start_slot=1,acknowledge_legacy=False,expected_token=None,proof=False):
        if not operator.strip():raise ValueError('Indique el responsable de la emisión en Configuración.')
        with self.api.work.catalog_lock():
            report,indices,profile,plan=self.prepare(issue_id,selection,reason,start_slot,acknowledge_legacy,expected_token)
            row=report['issue'];v=self.api.resolved_design(row['version_id'],row['design_variant_id'],not proof)
            values=json.loads(row['variables_json']);per=json.loads(row['per_container_json'] or '{}');status=json.loads(row['status_json'] or '{}')
            from .status_combined import resolve_status
            asset=resolve_status(self.api._repository,status,
                historical=report['snapshot'].get('status_master') if report['snapshot'] and status.get('revision_uid') else None)
            out=self.api.output_path('cache' if proof else 'emissions',('PRUEBA_REIMP_' if proof else 'REIMP_')+str(issue_id)+'_'+uuid.uuid4().hex+'.pdf')
            result=self.api.render(v,values,profile,indices,row['count_containers'],row['copies_per_container'],out,proof,
                per_container=per,status=status,status_master=asset,history_snapshot=report['snapshot'],
                reprint_context={'issue_id':issue_id,'fingerprint':original(self.api._repository,issue_id)[3]})
            if self.inspect(issue_id)['token']!=report['token']:
                out.unlink(missing_ok=True);raise ValueError('La emisión o la documentación cambió durante la generación. No se ha registrado una reimpresión.')
            if proof:return None,out,result
            try:
                pk=self.api.add_issue(v['id'],operator,row['count_containers'],row['copies_per_container'],indices,values,profile,out,
                    source_issue_id=issue_id,reason=reason.strip(),per_container=per,status=status)
            except Exception as ex:
                # A transport/filesystem exception can arrive after SQLite commit.
                # Reconcile by this unique output before touching its PDF. If the
                # database cannot answer, keep the file for diagnosis/recovery.
                try:
                    committed=self.api._repository.db.execute('SELECT id,source_issue_id FROM issues WHERE pdf_path=?',(out.relative_to(self.api._repository.root).as_posix(),)).fetchone()
                except Exception as uncertain:
                    raise ValueError('Resultado de registro incierto. PDF conservado; consulte Historial antes de reintentar.') from uncertain
                if committed:
                    if committed['source_issue_id']!=issue_id:raise ValueError('Registro incompatible. PDF conservado para revisión.') from ex
                    self.inspect(committed['id'])
                    return committed['id'],out,result
                try:out.unlink(missing_ok=True)
                except OSError:pass
                raise ValueError('Reimpresión no registrada. Consulte Historial antes de reintentar. '+str(ex)) from ex
            return pk,out,result
