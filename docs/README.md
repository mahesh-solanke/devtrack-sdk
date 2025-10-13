# DevTrack SDK Documentation

This directory contains the documentation for DevTrack SDK v0.3.0.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

### Building HTML Documentation

#### Using Make (Linux/macOS)

```bash
# Build HTML documentation
make html

# Clean build directory
make clean

# Show help
make help
```

#### Using Sphinx directly

```bash
# Build HTML documentation
sphinx-build -b html . _build/html

# Build with specific language
sphinx-build -T -b html -d _build/doctrees -D language=en . _build/html
```

#### Using Python module

```bash
# Build HTML documentation
python -m sphinx -T -b html -d _build/doctrees -D language=en . _build/html
```

### Viewing the Documentation

After building, open `_build/html/index.html` in your web browser.

## Documentation Structure

- `index.md` - Main documentation page with overview and quick start
- `fastapi_integration.md` - FastAPI integration guide
- `django_integration.md` - Django integration guide
- `conf.py` - Sphinx configuration
- `requirements.txt` - Documentation dependencies

## Configuration

The documentation is configured in `conf.py` with:

- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Extensions**: myst_parser, sphinx.ext.autodoc, sphinx.ext.viewcode, sphinx.ext.napoleon
- **MyST Extensions**: colon_fence, deflist, dollarmath, fieldlist, html_admonition, html_image, linkify, replacements, smartquotes, strikethrough, substitution, tasklist

## MyST Markdown Features

The documentation uses MyST (Markedly Structured Text) which extends Markdown with:

- **Admonitions**: `{note}`, `{warning}`, `{tip}`, etc.
- **Code blocks**: Syntax highlighting with language specification
- **Math**: LaTeX math expressions with `$...$` and `$$...$$`
- **Links**: Automatic linkification of URLs
- **Tables**: Markdown tables with enhanced features
- **Directives**: Sphinx directives like `{toctree}`, `{code-block}`, etc.

## Read the Docs Integration

The documentation is configured for Read the Docs with:

- `.readthedocs.yaml` - Read the Docs configuration
- `requirements.txt` - Python dependencies
- `conf.py` - Sphinx configuration

## Contributing to Documentation

1. Edit the Markdown files in this directory
2. Test locally with `make html`
3. Submit a pull request

## Troubleshooting

### Common Issues

1. **Linkify error**: Install `linkify-it-py` package
2. **Missing _static directory**: The directory is created automatically
3. **Toctree warnings**: Ensure all documents are included in the toctree

### Build Errors

If you encounter build errors:

1. Check that all dependencies are installed
2. Verify the Markdown syntax
3. Check the Sphinx configuration
4. Review the build log for specific errors

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Read the Docs](https://docs.readthedocs.io/)
- [sphinx-rtd-theme](https://sphinx-rtd-theme.readthedocs.io/)
