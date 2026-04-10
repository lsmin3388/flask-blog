"""Sphinx configuration for Flask Blog documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'Flask Blog'
copyright = '2026, lsmin3388'
author = 'lsmin3388'
release = '2.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_member_order = 'bysource'


def autodoc_process_docstring(app, what, name, obj, options, lines):
    """Strip Flasgger YAML specs (after ---) from docstrings."""
    for i, line in enumerate(lines):
        if line.strip() == '---':
            del lines[i:]
            break


def setup(app):
    app.connect('autodoc-process-docstring', autodoc_process_docstring)
