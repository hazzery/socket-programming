"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "socket-programming"
copyright = "2024, Harrison Parkes"
author = "Harrison Parkes"
release = "1.0.0"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinxcontrib.apidoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_typehints = "both"


# -- Apidoc configuration ---------------------------------------------------
# https://github.com/sphinx-contrib/apidoc?tab=readme-ov-file#configuration

apidoc_module_dir = "../"
apidoc_output_dir = "_sources"
apidoc_excluded_paths = [
    "tests",
    "logs",
    "__pycache__",
    "venv",
    "docs",
    "logging_config.py",
]
apidoc_separate_modules = True
apidoc_toc_file = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
