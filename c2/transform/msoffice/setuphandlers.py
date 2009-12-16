#!/usr/bin/env python
# encoding: utf-8
"""
setuphandlers.py

Created by Manabu Terada on 2009-12-02.
Copyright (c) 2009 CMScom. All rights reserved.
"""
from Products.CMFCore.utils import getToolByName
import config
from c2.transform.msoffice import logger

def setupOpenXml(context):
    """Add our transform in PT for MS Office"""

    site = context.getSite()
    # Registering our transform in PT
    transforms_tool = getToolByName(site, 'portal_transforms')
    if config.TRANSFORM_NAME not in transforms_tool.objectIds():
        # Not already installed
        transforms_tool.manage_addTransform(config.TRANSFORM_NAME, 'c2.transform.msoffice.transform')
    return


def removeOpenXml(context):
    """Removing various resources from plone site"""

    # At the moment, there's no uninstall support in GenericSetup. So
    # this is run by the old style quickinstaller uninstall handler.

    site = context
    # Removing our transform from PT
    transforms_tool = getToolByName(site, 'portal_transforms')
    transforms_tool.unregisterTransform(config.TRANSFORM_NAME)
    return

