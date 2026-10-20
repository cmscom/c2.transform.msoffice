from c2.transform.msoffice import config

import importlib
import mimetypes
import pytest


@pytest.fixture
def stdlib_mimetypes_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Forget the host's mime.types (slim images do not have one).

    mimetypes.init(files=[]) keeps the current database, so it is replaced.
    """
    monkeypatch.setattr(mimetypes, "_db", mimetypes.MimeTypes())


@pytest.mark.usefixtures("stdlib_mimetypes_only")
def test_import_adds_office_types_to_stdlib_mimetypes():
    importlib.reload(config)
    assert {
        ext: mimetypes.guess_type(f"file.{ext}")[0]
        for ext in ("docm", "docx", "pptm", "pptx", "xlsb", "xlsm", "xlsx")
    } == {
        "docm": "application/vnd.ms-word.document.macroEnabled.12",
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        "pptm": "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
        "pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        "xlsb": "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
        "xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }


def test_office_mimetypes_have_globs_and_icon():
    assert config.office_mimetypes[1] == {
        "name": "Office Word 2007 XML document",
        "mimetypes": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        "extensions": ("docx",),
        "globs": ("*.docx",),
        "icon_path": "application.png",
    }
