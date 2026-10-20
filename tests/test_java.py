"""Tests that run the bundled jar with a real ``java``.

They are skipped when ``java`` is not on PATH, unless
C2_TRANSFORM_MSOFFICE_REQUIRE_JAVA=1 is set (CI sets it); then they fail.
"""

from pathlib import Path
from plone import api
from plone.app.contenttypes.content import File
from plone.app.contenttypes.indexers import SearchableText_file
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.Portal import PloneSite

import logging
import os
import pytest
import shutil


SAMPLES = Path(__file__).parent / "samples"
REQUIRE_JAVA = "C2_TRANSFORM_MSOFFICE_REQUIRE_JAVA"

DOC = "application/msword"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
XLS = "application/vnd.ms-excel"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PPT = "application/vnd.ms-powerpoint"
PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


@pytest.fixture
def java() -> None:
    if shutil.which("java") is None:
        if os.environ.get(REQUIRE_JAVA) == "1":
            pytest.fail(f"java is not on PATH and {REQUIRE_JAVA}=1")
        pytest.skip("java is not on PATH")


@pytest.fixture
def no_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run java without a locale, like a slim container image."""
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.delenv("LANG", raising=False)


def add_file(portal: PloneSite, name: str, content_type: str) -> File:
    with api.env.adopt_roles(["Manager"]):
        return api.content.create(
            container=portal,
            type="File",
            id=name.replace(".", "-"),
            title="Sample",
            file=NamedBlobFile(
                data=(SAMPLES / name).read_bytes(),
                filename=name,
                contentType=content_type,
            ),
        )


def text_of(portal: PloneSite, name: str, content_type: str) -> str:
    text: str = SearchableText_file(add_file(portal, name, content_type))()
    return text


def transformed(portal: PloneSite, name: str, content_type: str) -> str:
    data = portal.portal_transforms.convertTo(
        "text/plain", (SAMPLES / name).read_bytes(), mimetype=content_type
    )
    text: str = data.getData()
    return text


@pytest.mark.usefixtures("java", "no_locale")
class TestRealJava:
    def test_docx_words_are_searchable(self, portal):
        text = text_of(portal, "document.docx", DOCX)
        for word in ("simple", "example", "document", "metadata", "comments"):
            assert word in text

    def test_japanese_is_not_garbled(self, portal):
        assert "これは日本語の文書の例です。" in text_of(portal, "document.docx", DOCX)

    def test_docx_text(self, portal):
        assert transformed(portal, "document.docx", DOCX) == (
            "This is a simple example of a document with a full set of metadata "
            "and comments.\nこれは日本語の文書の例です。\n\n"
        )

    @pytest.mark.parametrize(
        ("name", "content_type", "expected"),
        [
            (
                "document.doc",
                DOC,
                [
                    "This is a simple example of a document",
                    "これは日本語の文書の例です。",
                ],
            ),
            ("spreadsheet.xls", XLS, ["Fruit\tCount", "Apple\t3", "みかん\t5"]),
            ("spreadsheet.xlsx", XLSX, ["Fruit\tCount", "Apple\t3", "みかん\t5"]),
            (
                "presentation.pptx",
                PPTX,
                ["Presentation slide example", "スライドの例です。"],
            ),
            (
                "presentation-notes.pptx",
                PPTX,
                [
                    "Presentation with notes",
                    "ノート付きのスライドです。",
                    "Speaker notes example",
                    "発表者のノートです。",
                ],
            ),
        ],
    )
    def test_other_formats(self, portal, name, content_type, expected):
        text = text_of(portal, name, content_type)
        for part in expected:
            assert part in text

    def test_document_without_text(self, portal, caplog):
        with caplog.at_level(logging.INFO, logger="c2.transform.msoffice"):
            assert transformed(portal, "empty.docx", DOCX) == ""
        assert caplog.records == []

    def test_ppt_gives_no_text_with_the_bundled_jar(self, portal, caplog):
        """Known issue: the bundled jar cannot read .ppt files (see the xfail)."""
        obj = add_file(portal, "presentation.ppt", PPT)
        assert obj.file.data == (SAMPLES / "presentation.ppt").read_bytes()
        # Creating the File indexes it once already.
        caplog.clear()
        with caplog.at_level(logging.ERROR, logger="c2.transform.msoffice"):
            text = SearchableText_file(obj)()
        assert "Presentation slide example" not in text
        assert [r.getMessage() for r in caplog.records] == [
            "msdoc2txt failed with exit code 1"
        ]

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "The bundled msdoc2txt.jar (POI 3.17) fails on every .ppt: "
            "CurrentUserAtom.<init> -> 'Block 3 not found' / 'Unable to read 512 "
            "bytes from 2048 in stream of length -1'. MSDocExtracter seems to close "
            "the POIFS before HSLF reads the Current User stream. To be fixed when "
            "the jar is updated."
        ),
    )
    def test_ppt_text_is_searchable(self, portal):
        text = text_of(portal, "presentation.ppt", PPT)
        assert "Presentation slide example" in text
        assert "スライドの例です。" in text


def test_saving_works_without_java(portal, monkeypatch, tmp_path, caplog):
    monkeypatch.setenv("PATH", str(tmp_path))
    obj = add_file(portal, "document.docx", DOCX)
    assert obj.file.data == (SAMPLES / "document.docx").read_bytes()
    # Creating the File indexes it once already.
    caplog.clear()
    with caplog.at_level(logging.ERROR, logger="c2.transform.msoffice"):
        text = SearchableText_file(obj)()
    assert "simple example" not in text
    assert [r.getMessage() for r in caplog.records] == [
        "msdoc2txt could not run: java was not found"
    ]
