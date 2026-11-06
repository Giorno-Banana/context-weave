# SourceTrail source and reproduction guide

The completed Full is reproduced from `releases/sourcetrail-0.32.0-full/` and the recorded recovery ZIP. Follow [FULL_RECOVERY.md](../docs/FULL_RECOVERY.md) for the source relationship and [OPERATIONS.md](../OPERATIONS.md) for startup and private configuration.

The package in `laboratory/legacy-cycle2/` is retained for development and historical research. It is a separate development target from the completed Full. From the repository root, install and test it with:

```shell
python -m pip install -e laboratory/legacy-cycle2
cd laboratory/legacy-cycle2
python -m unittest discover -s tests -p "test_*.py"
cd ../..
```

These checks use synthetic records and mocked encoders. They do not start an official evaluation or configure a deployment. Keep credentials and live databases outside the repository.

To verify the current development files or only the protected release materials, run from the repository root:

```shell
python catalog/verify_layout.py
python catalog/verify_layout.py --frozen-only
```

[versions.md](versions.md) navigates the recorded releases; `archive/` retains historical documentation. Source archives and their manifests retain their release identity. See [PROVENANCE.md](../PROVENANCE.md) and [LICENSE](../LICENSE) for source and license records.
