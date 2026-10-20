"""Make Microsoft Office files searchable in Plone."""

# Importing config registers the Office types with the mimetypes module.
from c2.transform.msoffice import config  # noqa: F401

from importlib.metadata import version

import logging


PACKAGE_NAME = "c2.transform.msoffice"

# The version is kept only in pyproject.toml, where zest.releaser changes it.
__version__ = version(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)
