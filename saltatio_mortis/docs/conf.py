# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
project = 'Saltatio Mortis'
copyright = '2025, Mortis Team'
author = 'Ariotti Matteo, Chiara Konrad, Maddaloni Enrico, Puccini Nicolò, Fabrice Ghislain Tebou, Trotti Enrico, Yildiz Sidar'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Autodoc defaults: apply members/undoc/inheritance automatically
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Render type hints in the description to keep signatures clean
autodoc_typehints = 'description'

# Prefer Google style docstrings via napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Shorten qualified names in headings
add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
