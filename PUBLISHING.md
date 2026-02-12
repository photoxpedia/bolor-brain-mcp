# Publishing Bolor Brain MCP to PyPI

Step-by-step guide to publish the package to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify email
   - Set up 2FA (required)

2. **TestPyPI Account** (for testing)
   - Create at https://test.pypi.org/account/register/

3. **Install Build Tools**
   ```bash
   pip install --upgrade build twine
   ```

## Pre-Publication Checklist

- [ ] Update `pyproject.toml` with your email
- [ ] Verify version number (start with 1.0.0)
- [ ] Ensure README.md is complete
- [ ] All tests pass (`pytest tests/`)
- [ ] LICENSE file is present
- [ ] No sensitive data in files

## Step 1: Update pyproject.toml

Edit the email in `pyproject.toml`:

```toml
authors = [
    {name = "Bolorerdene Bundgaa", email = "your@email.com"}  # <-- UPDATE THIS
]
```

## Step 2: Build Distribution Packages

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
python -m build
```

This creates:
- `dist/bolor_brain_mcp-1.0.0-py3-none-any.whl` (wheel)
- `dist/bolor-brain-mcp-1.0.0.tar.gz` (source)

## Step 3: Test on TestPyPI First

### Create API Token (TestPyPI)

1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "bolor-brain-mcp"
4. Scope: "Entire account" (or specific project once created)
5. Copy the token (starts with `pypi-`)

### Configure Token

```bash
# Create/edit ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
username = __token__
password = pypi-your-test-token-here

[pypi]
username = __token__
password = pypi-your-real-token-here
EOF

chmod 600 ~/.pypirc
```

### Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

### Test Installation

```bash
# In a fresh virtual environment
python -m venv test_env
source test_env/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple bolor-brain-mcp

# Test it works
python -c "from modules import HybridReasoner; print('OK')"

# Deactivate and remove
deactivate
rm -rf test_env
```

## Step 4: Publish to PyPI (Production)

### Create API Token (PyPI)

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "bolor-brain-mcp"
4. Copy the token
5. Add to `~/.pypirc` (see above)

### Upload to PyPI

```bash
python -m twine upload dist/*
```

### Verify

```bash
# Wait a few minutes for PyPI to index
pip install bolor-brain-mcp

# Test
python -c "from modules import HybridReasoner; print('OK')"
```

## Step 5: Post-Publication

### Tag the Release on GitHub

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Initial PyPI publication"
git push origin v1.0.0
```

### Create GitHub Release

1. Go to https://github.com/photoxpedia/bolor-brain-mcp/releases
2. Click "Draft a new release"
3. Tag: v1.0.0
4. Title: "Bolor Brain MCP v1.0.0"
5. Description:
   ```markdown
   ## Bolor Brain MCP v1.0.0

   First official release! 🎉

   **Install:**
   ```bash
   pip install bolor-brain-mcp
   ```

   **What's included:**
   - 5 reasoning engines (symbolic, graph, case-based, hypothesis, analogical)
   - MCP server for Claude Code integration
   - 9 reasoning tools
   - 4 pre-built skills (/reason, /debug, /decide, /learn-from)
   - 400+ tests
   - Comprehensive documentation

   **Quick Start:**
   See [MCP_SETUP.md](MCP_SETUP.md) for setup instructions.

   **Documentation:**
   - [README](README.md)
   - [MCP Setup Guide](MCP_SETUP.md)
   - [Examples](CLAUDE_CODE_EXAMPLES.md)
   - [Skills](skills/README.md)
   ```

### Update README Badges

Add PyPI badge to README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/bolor-brain-mcp.svg)](https://badge.fury.io/py/bolor-brain-mcp)
[![Downloads](https://pepy.tech/badge/bolor-brain-mcp)](https://pepy.tech/project/bolor-brain-mcp)
```

### Announce

Post to:
- Twitter/X
- HackerNews
- Reddit (r/ClaudeAI, r/Python)
- LinkedIn
- Claude Discord

Use the marketing materials from MARKETING.md.

## Updating the Package

### For Bug Fixes (1.0.1)

```bash
# Update version in pyproject.toml
version = "1.0.1"

# Build and upload
python -m build
python -m twine upload dist/*

# Tag
git tag -a v1.0.1 -m "Bug fix release"
git push origin v1.0.1
```

### For New Features (1.1.0)

```bash
# Update version in pyproject.toml
version = "1.1.0"

# Build and upload
python -m build
python -m twine upload dist/*

# Tag
git tag -a v1.1.0 -m "Feature release: <description>"
git push origin v1.1.0
```

### For Breaking Changes (2.0.0)

```bash
# Update version in pyproject.toml
version = "2.0.0"

# Build and upload
python -m build
python -m twine upload dist/*

# Tag
git tag -a v2.0.0 -m "Major release: <breaking changes>"
git push origin v2.0.0
```

## Semantic Versioning

Follow [semver.org](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (1.X.0): New features, backwards compatible
- **PATCH** (1.0.X): Bug fixes, backwards compatible

## Common Issues

### "File already exists"
- You can't overwrite existing versions
- Increment version number
- Delete dist/ and rebuild

### "Invalid credentials"
- Check API token
- Verify ~/.pypirc format
- Ensure token has correct scope

### "Package name already taken"
- Change project name in pyproject.toml
- Check availability: https://pypi.org/project/bolor-brain-mcp/

### "Long description failed"
- Verify README.md is valid markdown
- Check for syntax errors
- Test with: `python -m readme_renderer README.md`

## Package Maintenance

### Monitor

- PyPI downloads: https://pypistats.org/packages/bolor-brain-mcp
- GitHub stars/issues
- User feedback

### Respond to Issues

- Check GitHub issues regularly
- Fix critical bugs quickly
- Release patches as needed

### Keep Dependencies Updated

```bash
# Check for outdated dependencies
pip list --outdated

# Update requirements
# Test thoroughly before releasing
```

## Automation (Optional)

### GitHub Actions for Release

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add `PYPI_API_TOKEN` to GitHub secrets.

## Quick Reference

```bash
# Build
python -m build

# Test upload
python -m twine upload --repository testpypi dist/*

# Production upload
python -m twine upload dist/*

# Install from PyPI
pip install bolor-brain-mcp

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple bolor-brain-mcp
```

---

You're ready to publish! 🚀
