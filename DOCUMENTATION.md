# Building the Documentation

This project uses Sphinx to generate comprehensive HTML documentation.

## Quick Start

### Install Documentation Dependencies

```bash
pip install -e .[docs]
```

### Build the Documentation

```bash
cd docs
make html
```

The generated documentation will be in `docs/_build/html/`. Open `docs/_build/html/index.html` in your browser.

## What's Included

The documentation includes:

- **Installation Guide**: Step-by-step installation instructions
- **Quick Start**: Get started quickly with basic examples
- **Usage Guide**: Comprehensive guide covering all features
- **API Reference**: Complete API documentation with type hints (auto-generated from docstrings)
- **Integration Guide**: How to use tablesQLite with recordsQL

## Building on Windows

```bash
cd docs
make.bat html
```

## Cleaning Build Artifacts

```bash
cd docs
make clean
```

## Hosting the Documentation

### Read the Docs (Recommended)

The project includes a `.readthedocs.yaml` configuration file. To host on Read the Docs:

1. Sign up at https://readthedocs.org/
2. Import your GitHub repository
3. Documentation will build automatically on each commit

### Local Preview

You can preview the documentation locally:

```bash
cd docs/_build/html
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Documentation Structure

- `docs/index.rst` - Main documentation index
- `docs/installation.rst` - Installation guide
- `docs/quickstart.rst` - Quick start tutorial
- `docs/usage.rst` - Detailed usage guide
- `docs/api.rst` - API reference
- `docs/integration.rst` - Integration with recordsQL
- `docs/conf.py` - Sphinx configuration

## Customization

The documentation uses:

- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Docstring Style**: Google-style docstrings (configured with Napoleon)
- **Auto-documentation**: Enabled with autodoc extension
- **Type Hints**: Displayed with sphinx-autodoc-typehints

To customize, edit `docs/conf.py`.
