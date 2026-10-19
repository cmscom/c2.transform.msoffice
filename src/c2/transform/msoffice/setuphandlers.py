from c2.transform.msoffice import config
from c2.transform.msoffice import logger
from plone.base.interfaces import INonInstallable
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer


TRANSFORM_MODULE = "c2.transform.msoffice.transform"


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide the uninstall profile from site creation and the add-ons list."""
        return ["c2.transform.msoffice:uninstall"]


def post_install(context):
    """Register the Office MIME types and the transform.

    ``context`` is the setup tool. Running it again changes nothing.
    """
    mtr = getToolByName(context, "mimetypes_registry")
    for mt_dict in config.office_mimetypes:
        main_mt = mt_dict["mimetypes"][0]
        mt_name = mt_dict["name"]
        if mtr.lookup(main_mt):
            logger.info("%s (%s) MIME type already registered", main_mt, mt_name)
            continue
        mtr.manage_addMimeType(
            mt_name,
            mt_dict["mimetypes"],
            mt_dict["extensions"],
            mt_dict["icon_path"],
            binary=True,
            globs=mt_dict["globs"],
        )
        logger.info("%s (%s) MIME type registered", main_mt, mt_name)

    transforms = getToolByName(context, "portal_transforms")
    if config.TRANSFORM_NAME in transforms.objectIds():
        logger.info(
            "%s is already registered in portal_transforms; skipped",
            config.TRANSFORM_NAME,
        )
        return
    transforms.manage_addTransform(config.TRANSFORM_NAME, TRANSFORM_MODULE)


def uninstall(context):
    """Remove the transform. The MIME types stay; others may use them."""
    transforms = getToolByName(context, "portal_transforms")
    if config.TRANSFORM_NAME not in transforms.objectIds():
        return
    try:
        transforms.unregisterTransform(config.TRANSFORM_NAME)
    except KeyError as error:
        # unregisterTransform unmaps first and raises KeyError when a MIME
        # type was never mapped to this transform.
        logger.warning(
            "Could not unregister %s from portal_transforms: %r",
            config.TRANSFORM_NAME,
            error,
        )
