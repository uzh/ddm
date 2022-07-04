# Configuration file for the Sphinx documentation builder.
import os
# -- Project information

project = 'DDM'
copyright = '2022'
author = 'Nico Pfiffner'

release = '0.0'
version = '0.0.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/img/ddm_logo_black_descr.svg'
html_favicon = '_static/img/ddl_favicon_black.svg'
html_theme_options = {
    'logo_only': True,
    'prev_next_buttons_location': None,
}
html_css_files = ['css/custom.css']

todo_include_todos = True
