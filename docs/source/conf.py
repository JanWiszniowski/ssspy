# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SSSPy'
copyright = '2025, Jan Wiszniowski'
author = 'Jan Wiszniowski'
licence = 'GNU Lesser General Public License, Version 3 (https://www.gnu.org/copyleft/lesser.html)'
release = '0.0.1'
release_date = '2025-02-06'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import sys
import os
from datetime import datetime
from matplotlib import pyplot as plt

sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx_favicon',
    'sphinx_rtd_theme',
    'sphinxcontrib.bibtex',
    'sphinx_mdinclude',
    'matplotlib.sphinxext.plot_directive',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
bibtex_bibfiles = ['refs.bib']
bibtex_reference_style = 'author_year'
bibtex_default_style = 'unsrt'
html_logo = 'ssspy.png'

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
if html_theme == "sphinx_rtd_theme":
	html_theme_options = {
		# 'analytics_id': 'G-XXXXXXXXXX',  #  Provided by Google in your dashboard
		'analytics_anonymize_ip': False,
		'logo_only': False,
		'prev_next_buttons_location': 'bottom',
		'style_external_links': False,
		'vcs_pageview_mode': '',
		'style_nav_header_background': 'blue',
		'flyout_display': 'hidden',
		'version_selector': True,
		'language_selector': True,
		# Toc options
		'collapse_navigation': True,
		'sticky_navigation': True,
		'navigation_depth': 4,
		'includehidden': True,
		'titles_only': False
	}

# -- Options for LaTeX output -------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}
