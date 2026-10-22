"""Audit verified ARC exports for the actual scope of the current converters.

Read-only. No material links or game/animation identities inferred from names.
"""
import argparse,json
from collections import Counter
from pathlib import Path
from extract_arc import verify
from convert_mod230_obj import convert
from inspect_tex3ds_header import inspect as inspect_tex


def catalog(folder):
    folder=Path(folder);bundle=verify(folder);manifest=json.loads((folder/'manifest.json').read_text())
    records=[]
    for entry in manifest['entries']:
        kind=entry['signature_candidate']
        if kind not in ('MOD_candidate','TEX_candidate'):continue
        row=dict(index=entry['index'],internal_path=entry['path'],source_payload_sha256=entry['sha256'],
                 kind=kind,semantic_identity_verified=False)
        data=(folder/entry['output_file']).read_bytes()
        try:
            if kind=='MOD_candidate':
                obj,report=convert(data)
                row.update(status='static_obj_dry_run_ok',meshes=report['meshes'],output_bytes_dry_run=len(obj),
                           skeleton_converted=False,material_association_verified=False)
            else:
                report=inspect_tex(data)
                if not report['exact_header_table_payload_fit']:raise ValueError('trailing texture bytes')
                row.update(status='tex_header_within_converter_scope',width=report['width'],height=report['height'],
                    format=report['color_format_name'],pixel_conversion_performed=False)
        except (ValueError,IndexError) as exc:row.update(status='outside_current_converter_scope',reason=str(exc))
        records.append(row)
    return dict(source_archive_sha256=bundle['source_sha256'],manifest_sha256=bundle['manifest_sha256'],
        export_integrity_verified=True,summary=dict(Counter(r['status'] for r in records)),
        inspected_resources=len(records),not_inspected_resources=bundle['entry_count']-len(records),records=records,
        names_used_to_infer_material_pairing=False,commercial_derivatives_written=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=catalog(a.folder)
    with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))
