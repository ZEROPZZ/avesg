# -*- coding: utf-8 -*-

# -- Project information -----------------------------------------------------

project = 'AVESG'
copyright = '2023, zero'
author = 'zero'

# -- General configuration ---------------------------------------------------

extensions = [
  'sphinx.ext.autodoc',  # automatic documentation generation
  'sphinx.ext.viewcode',  # display source code
  'sphinx.ext.todo',  # todo extension
  'sphinx.ext.mathjax',  # math support
]

source_suffix = '.rst'  # source file extension
master_doc = 'index'  # main document
language = 'zh_CN'  # language code (Chinese)

# -- Project-specific configuration ------------------------------------------

# Project logo
logo = 'images/logo.png'

# Project version
version = '0.1'
release = '0.1.0'

# Project description
description = 'AVESG: A Self-Learning Robot Project'

# -- Theme configuration ----------------------------------------------------

html_theme =html_theme = 'alabaster'
html_theme_options = {
  'style_nav_header_background': '#333',
    'collapse_navigation': True,
}

# -- Autodoc configuration --------------------------------------------------

autoclass_content = 'both'
autodoc_member_order = 'bysource'

# -- Todo extension configuration ---------------------------------------------

todo_include_todos = True

# -- MathJax configuration -------------------------------------------------

mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js'

# -- Other configuration ----------------------------------------------------

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme_path = ['_themes']

# -- Python-specific configuration --------------------------------------------

primary_domain = 'py'
default_role = 'py:obj'
