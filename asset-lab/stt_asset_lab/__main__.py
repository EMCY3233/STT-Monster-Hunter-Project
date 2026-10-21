import argparse
import json
import sys
from .model import AssetError, load

def main():
    parser = argparse.ArgumentParser(description='STT Asset Lab — STT Asset/1 inspector')
    parser.add_argument('asset')
    parser.add_argument('--validate', action='store_true', help='headless strict validation')
    args = parser.parse_args()
    try:
        data = load(args.asset)
        if args.validate:
            print(json.dumps({'name':data['name'], 'bones':len(data['bones']),
                              'vertices':len(data['vertices']), 'clips':[c['name'] for c in data['clips']]}))
        else:
            from .viewer import run
            run(data)
    except (AssetError, OSError) as exc:
        parser.exit(2, f'Asset error: {exc}\n')
    except Exception as exc:
        # Tk can be unavailable on minimal Python installations / headless hosts.
        if isinstance(exc, ImportError) or exc.__class__.__name__ == 'TclError':
            parser.exit(3, f'GUI unavailable: {exc}. Use --validate for headless inspection.\n')
        raise

if __name__ == '__main__':
    main()
