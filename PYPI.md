# PyPI Distribution Guide

## Publishing to PyPI

### Prerequisites
1. Create PyPI account: https://pypi.org/account/register/
2. Create API token: https://pypi.org/manage/account/token/
3. Install twine: `pip install twine`

### Publishing Steps

1. **Build the package**:
   ```bash
   python setup.py sdist bdist_wheel
   ```

2. **Check the package**:
   ```bash
   twine check dist/*
   ```

3. **Upload to Test PyPI** (optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

### Configuration

Create `~/.pypirc`:
```ini
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

### Version Updates

1. Update version in `setup.py` and `hospitable/__init__.py`
2. Update `CHANGELOG.md`
3. Commit changes
4. Create git tag: `git tag v0.1.1`
5. Push tag: `git push origin v0.1.1`
6. Build and upload new version

### Package Information

- **Package Name**: `hospitable-python`
- **Import Name**: `hospitable`
- **PyPI URL**: https://pypi.org/project/hospitable-python/
- **Install**: `pip install hospitable-python`

### Distribution Files

- **Wheel**: `hospitable_python-0.1.0-py3-none-any.whl`
- **Source**: `hospitable-python-0.1.0.tar.gz`

Both files are ready for PyPI upload.