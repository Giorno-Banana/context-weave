"""Package the recorded development layout without changing historical manifests."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    target = parser.parse_args().output.resolve()
    layout = json.loads((ROOT/'DEVELOPMENT_LAYOUT.json').read_text(encoding='utf-8'))
    paths = list(layout['files_sha256'])+['DEVELOPMENT_LAYOUT.json']
    if target.exists() or target.is_relative_to(ROOT):
        parser.error('Use a new archive path outside the checkout')
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in paths:
            content = (ROOT/name).read_bytes()
            if name in layout['files_sha256'] and hashlib.sha256(content).hexdigest()!=layout['files_sha256'][name]:
                raise ValueError('Development file hash differs: '+name)
            bundle.writestr(name, content)
    with zipfile.ZipFile(target) as bundle:
        assert bundle.testzip() is None
    print(json.dumps(dict(verified=True, files=len(paths), official_submission=False,
                         sha256=hashlib.sha256(target.read_bytes()).hexdigest())))

if __name__=='__main__':main()
