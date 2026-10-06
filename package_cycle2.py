"""Build an allowlisted Cycle 2 source archive; excludes credentials and data."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "dist/context-weave-0.3.0-cycle2-source.zip")
    target = parser.parse_args().output.resolve()
    files = {name: root / name for name in (
        "OPERATIONS.md", "PROVENANCE.md", "CYCLE2_STATUS.md", "SUBMISSION.md", "LICENSE",
        "requirements.txt", "requirements-local.txt", "Dockerfile", "compose.yaml", "Caddyfile",
        ".dockerignore", ".gitignore", "env.example", "start_local.ps1", "preflight.py",
        "evaluate_retrieval.py", "probe_http.py", "PILOT_RESULTS.md", "package_cycle2.py",
        "evaluation/pilot-20261001/sample-ids.json", "evaluation/pilot-20261001/sample-plan.json")}
    files["README.md"] = root / "README_CYCLE2.md"
    # Retain the packaging input name as well so rebuilding the archive works.
    files["README_CYCLE2.md"] = root / "README_CYCLE2.md"
    for path in sorted((root / "adaptive_evidence").glob("*.py")):
        files["adaptive_evidence/" + path.name] = path
    for name in ("test_contract.py", "test_adaptive.py", "test_planner.py", "test_retrieval_views.py",
                 "test_remote_encoder.py", "test_preflight.py", "test_cycle2_evaluation.py", "test_add_indexer.py"):
        files["tests/" + name] = root / "tests" / name
    manifest = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, path in files.items():
            bundle.write(path, name)
        bundle.writestr("SHA256SUMS.json", json.dumps(manifest, indent=2))
    with zipfile.ZipFile(target) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("Archive checksum failed")
        for name, expected in manifest.items():
            if hashlib.sha256(bundle.read(name)).hexdigest() != expected:
                raise RuntimeError("Source checksum mismatch")
    report = {"archive": target.name, "files": len(files) + 1, "bytes": target.stat().st_size,
              "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "verified": True,
              "official_submission": False, "contains_datasets_or_credentials": False}
    target.with_suffix(".manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
