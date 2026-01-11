# tablesQLite Documentation

This directory contains the Sphinx documentation for tablesQLite.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install tablesqlite[docs]
```

Or install Sphinx and related packages manually:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

You also need the project dependencies for autodoc to work:

```bash
pip install expressQL sortedcontainers
```

### Building HTML Documentation

To build the HTML documentation:

```bash
cd docs
make html
```

On Windows:

```bash
cd docs
make.bat html
```

The generated HTML documentation will be in `_build/html/`. Open `_build/html/index.html` in a browser to view it.

### Other Build Targets

Sphinx supports various output formats:

- `make html` - HTML documentation (default)
- `make singlehtml` - Single HTML page
- `make latex` - LaTeX files for PDF generation
- `make epub` - EPUB ebook format
- `make text` - Plain text format
- `make man` - Manual pages
- `make help` - Show all available targets

### Cleaning Build Artifacts

To remove generated documentation:

```bash
make clean
```

## Documentation Structure

- `index.rst` - Main documentation index
- `installation.rst` - Installation instructions
- `quickstart.rst` - Quick start guide
- `usage.rst` - Detailed usage guide
- `api.rst` - API reference (auto-generated)
- `integration.rst` - Integration with recordsQL
- `conf.py` - Sphinx configuration
- `_static/` - Static files (CSS, images, etc.)
- `_templates/` - Custom templates
- `_build/` - Generated documentation (excluded from git)

## Configuration

The documentation is configured in `conf.py`. Key settings:

- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Extensions**:
  - `sphinx.ext.autodoc` - Automatic documentation from docstrings
  - `sphinx.ext.napoleon` - Support for Google-style docstrings
  - `sphinx.ext.viewcode` - Add links to highlighted source code
  - `sphinx.ext.intersphinx` - Link to other project documentation
  - `sphinx_autodoc_typehints` - Better type hint display

## Writing Documentation

The documentation is written in reStructuredText (RST) format. Some quick references:

- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

## Continuous Integration

You can integrate documentation building into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Build documentation
  run: |
    pip install -e .[docs]
    cd docs
    make html
```

## Hosting

The documentation can be hosted on:

- [Read the Docs](https://readthedocs.org/) - Free hosting for open source projects
- GitHub Pages
- Any static web hosting service

### Read the Docs Setup

1. Create an account on [Read the Docs](https://readthedocs.org/)
2. Import your GitHub repository
3. The documentation will be built automatically on each commit
4. Access it at `https://tablesqlite.readthedocs.io/`
