from Acquisition import aq_base
from c2.transform.msoffice import PACKAGE_NAME
from plone.base.interfaces import INonInstallable
from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView
from Products.CMFPlone.Portal import PloneSite
from Products.GenericSetup.tool import SetupTool
from Products.PortalTransforms.TransformEngine import TransformTool
from zope.component import getUtility

import logging
import pytest


TRANSFORM_NAME = "msoffice_to_text"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DEFAULT_PROFILE = "profile-c2.transform.msoffice:default"
UNINSTALL_PROFILE = "profile-c2.transform.msoffice:uninstall"


@pytest.fixture
def transforms(portal: PloneSite) -> TransformTool:
    return portal.portal_transforms


@pytest.fixture
def setup_tool(portal: PloneSite) -> SetupTool:
    return portal.portal_setup


def test_addon_installed(installer):
    assert installer.is_product_installed(PACKAGE_NAME) is True


def test_latest_version(profile_last_version):
    assert profile_last_version(f"{PACKAGE_NAME}:default") == "2000"


def test_transform_installed(transforms):
    assert TRANSFORM_NAME in transforms.objectIds()
    transform = transforms[TRANSFORM_NAME]
    assert transform.module == "c2.transform.msoffice.transform"
    assert "application/vnd.ms-powerpoint" in transform.inputs


def test_install_restores_a_missing_mimetype(portal, setup_tool):
    mtr = portal.mimetypes_registry
    mtr.manage_delObjects([DOCX])
    assert mtr.lookup(DOCX) == ()
    setup_tool.runAllImportStepsFromProfile(DEFAULT_PROFILE)
    [mimetype] = mtr.lookup(DOCX)
    assert mimetype.name() == "Office Word 2007 XML document"
    assert mimetype.extensions == ("docx",)
    assert mimetype.globs == ("*.docx",)
    assert mimetype.binary


def test_install_twice(transforms, setup_tool, caplog):
    transform = transforms[TRANSFORM_NAME]
    with caplog.at_level(logging.INFO, logger=PACKAGE_NAME):
        setup_tool.runAllImportStepsFromProfile(DEFAULT_PROFILE)
    assert transforms.objectIds().count(TRANSFORM_NAME) == 1
    assert aq_base(transforms[TRANSFORM_NAME]) is aq_base(transform)
    assert (
        PACKAGE_NAME,
        logging.INFO,
        "msoffice_to_text is already registered in portal_transforms; skipped",
    ) in caplog.record_tuples


def test_uninstall_profile_is_hidden(portal):
    hidden = getUtility(INonInstallable, name=PACKAGE_NAME)
    assert hidden.getNonInstallableProfiles() == ["c2.transform.msoffice:uninstall"]


class TestUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer: InstallerView) -> None:
        installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self, installer):
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_transform_removed(self, transforms):
        assert TRANSFORM_NAME not in transforms.objectIds()

    def test_mimetypes_are_kept(self, portal):
        assert len(portal.mimetypes_registry.lookup(DOCX)) == 1

    def test_uninstall_twice(self, transforms, setup_tool):
        setup_tool.runAllImportStepsFromProfile(UNINSTALL_PROFILE)
        assert TRANSFORM_NAME not in transforms.objectIds()

    def test_missing_mapping_still_removes_the_transform(
        self, installer, transforms, caplog
    ):
        installer.install_product(PACKAGE_NAME)
        # A site where the DOCX -> text/plain mapping got lost:
        # unregisterTransform raises KeyError before it deletes the transform.
        del transforms._mtmap[DOCX]["text/plain"]
        with caplog.at_level(logging.WARNING, logger=PACKAGE_NAME):
            installer.uninstall_product(PACKAGE_NAME)
        assert installer.is_product_installed(PACKAGE_NAME) is False
        assert TRANSFORM_NAME not in transforms.objectIds()
        assert [r.getMessage() for r in caplog.records] == [
            "Could not unmap msoffice_to_text in portal_transforms: "
            "KeyError('text/plain'); the transform was removed anyway"
        ]

    def test_install_after_a_missing_mapping_adds_the_transform(
        self, installer, transforms
    ):
        installer.install_product(PACKAGE_NAME)
        del transforms._mtmap[DOCX]["text/plain"]
        installer.uninstall_product(PACKAGE_NAME)
        installer.install_product(PACKAGE_NAME)
        assert TRANSFORM_NAME in transforms.objectIds()
        assert [t.name() for t in transforms._mtmap[DOCX]["text/plain"]] == [
            "msoffice_to_text"
        ]
