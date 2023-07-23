# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#

# ================================== Imports ==================================

import os
import sys
import pkg_resources

# ============================== Build Environment ==============================
# Build behaviour is dependent on environment
on_rtd = os.environ.get('READTHEDOCS') == 'True'

# Configure the path
root = os.path.abspath('../../')
sys.path.insert(0, root)
sys.path.append(os.path.abspath('.'))

# Add custom Pygments style if HTML
if 'html' not in sys.argv:
    pygments_style = 'sphinx'

# on_rtd = True  # Uncomment for testing RTD builds locally


# ============================ Project information ============================

project = 'MyMagento'
copyright = '2023, Adam Korn'
author = 'Adam Korn'
repo = "my-magento"

# Simplify things by using the installed version
pkg = pkg_resources.require(repo)[0]
version = pkg.version
release = version


# ======================== General configuration ============================

# Doc with root toctree
master_doc = 'contents'  # .rst

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Source File type
source_suffix = ['.rst', '*.ipynb']

# LaTeX settings
latex_elements = {          # Less yucky looking font
    'preamble': r'''
\usepackage[utf8]{inputenc}
\usepackage{charter}
\usepackage[defaultsans]{lato}
\usepackage{inconsolata}
''',
}

# ============================ Extensions ====================================

# Add any Sphinx extension module names here, as strings
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx_readme',
    'sphinx_sitemap',
    'sphinx_github_style',
    'myst_nb',
]


# ====================== Extra Settings for Extensions ========================

# ~~~~ InterSphinx ~~~~
# Add references to Python, Requests docs
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# ~~~~ AutoSectionLabel ~~~~
# Make sure the target is unique
autosectionlabel_prefix_document = True


# ~~~~ Autodoc ~~~~
# Order based on source
autodoc_member_order = 'bysource'
#
# Remove typehints from method signatures and put in description instead
autodoc_typehints = 'description'
#
# Only add typehints for documented parameters (and all return types)
#  ->  Prevents parameters being documented twice for both the class and __init__
autodoc_typehints_description_target = 'documented_params'

# Shorten type hints
python_use_unqualified_type_names = True


# ~~~~ MyST{NB} ~~~~
# Turn off notebook execution until I have a store set up for testing/examples
jupyter_execute_notebooks = "off"


# ============================ HTML Theme Settings ============================

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Theme Options
# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html#theme-options
#
html_theme_options = {
    # Add the [+] signs to nav
    'collapse_navigation': False,
    # Prev/Next buttons also placed at the top bc it'd be cruel not to
    'prev_next_buttons_location': 'both',
}

html_context = {
    'display_github': True,
    'github_user': 'TDKorn',
    'github_repo': repo,
}

html_logo = "_static/magento_black.png"

html_baseurl = "https://my-magento.readthedocs.io/en/latest/"

if not on_rtd:
    site_url = "https://tdkorn.github.io/my-magento/"

sitemap_url_scheme = "{link}"

# ========================== Sphinx README ============================

readme_src_files = "README.rst"

readme_docs_url_type = "html"

# Blob to use when linking to GitHub source code
if on_rtd or bool(os.getenv('local')):
    readme_blob = 'last_tag'
else:
    # For gh-pages, don't need to generate README
    extensions.remove('sphinx_readme')
    # Use sphinx-github-style for linkcode
    linkcode_blob = 'main'

readme_admonition_icons = {
    "client": "💻",
    "search": "🔍",
    "docs": "📚",
    "example": "📋"
}

readme_rubric_heading = "="


# Settings to uncomment when generating PyPi README
#
# readme_raw_directive = False
#
# readme_inline_markup = False
#
# readme_tags = ["pypi"]

# ============================ Sphinx Github Style ============================
#
# Top level package name
top_level = pkg.get_metadata("top_level.txt").strip()

# Text to use for the linkcode link
linkcode_link_text = "View on GitHub"


# ---- Skip and Setup Method -------------------------------------------------

def skip(app, what, name, obj, would_skip, options):
    """Include __init__ as a documented method"""
    if name in ('__init__',):
        return False
    return would_skip


def setup(app):
    app.connect('autodoc-skip-member', skip)
    app.add_css_file("custom.css")
