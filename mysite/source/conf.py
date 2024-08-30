# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Self-Service-Kiosk Django'
copyright = '2024, Christopher Trautmann'
author = 'Christopher Trautmann'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ['_static']

import os
import sys
import django
from inspect import isfunction, ismethod

sys.path.insert(0, os.path.abspath('C:/Users/chris/PyCharmProjects/Self-Service-Kiosk/mysite'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
    "sphinxcontrib_django",
]

django_settings = "mysite.settings"

html_theme = 'sphinx_rtd_theme'

autodoc_inherit_docstrings = False  # Docstrings nicht von übergeordneten Klassen erben

# Customize autodoc behavior
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': False,
}

locale_dirs = ['locales/']  # Pfad zu den Übersetzungsdateien
gettext_compact = False     # optional


