"""Make Microsoft Office files searchable in Plone."""

# Importing config registers the Office types with the mimetypes module.
from c2.transform.msoffice import config  # noqa: F401

import logging


__version__ = "2.0.0.dev0"

PACKAGE_NAME = "c2.transform.msoffice"

logger = logging.getLogger(PACKAGE_NAME)
