"""Unit tests for the transform. ``java`` is replaced; Plone is not started."""

from c2.transform.msoffice import transform
from pathlib import Path
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import ITransform

import logging
import pytest
import subprocess


JAR = str(Path(transform.__file__).with_name("msdoc2txt.jar"))
DOCUMENT = b"PK\x03\x04 secret document body"


class FakeRun:
    """Stands in for subprocess.run and records the calls."""

    def __init__(self, returncode=0, stdout=b"", stderr=b"", error=None):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.error = error
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if self.error is not None:
            raise self.error
        return subprocess.CompletedProcess(
            args, self.returncode, stdout=self.stdout, stderr=self.stderr
        )


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.delenv("C2_TRANSFORM_MSOFFICE_TIMEOUT", raising=False)
    monkeypatch.delenv("C2_TRANSFORM_MSOFFICE_JAVA_OPTS", raising=False)


def fake_run(monkeypatch, **kwargs) -> FakeRun:
    run = FakeRun(**kwargs)
    monkeypatch.setattr(transform.subprocess, "run", run)
    return run


def convert(orig) -> str:
    data = datastream("test")
    result = transform.msoffice_to_text().convert(orig, data)
    assert result is data
    return data.getData()


def test_implements_itransform():
    assert ITransform.providedBy(transform.msoffice_to_text())


def test_name_and_mimetypes():
    t = transform.register()
    assert t.name() == "msoffice_to_text"
    assert t.output == "text/plain"
    assert t.output_encoding == "utf-8"
    assert t.inputs == (
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-word.document.macroEnabled.12",
        "application/vnd.ms-excel",
        "application/msexcel",
        "application/x-msexcel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
        "application/vnd.ms-excel.sheet.macroEnabled.12",
        "application/vnd.ms-powerpoint",
        "application/powerpoint",
        "application/mspowerpoint",
        "application/x-mspowerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
    )


def test_success(monkeypatch, caplog):
    run = fake_run(monkeypatch, stdout="Hello 日本語\n".encode())
    with caplog.at_level(logging.DEBUG, logger="c2.transform.msoffice"):
        assert convert(DOCUMENT) == "Hello 日本語\n"
    assert caplog.records == []
    args, kwargs = run.calls[0]
    assert args == [
        "java",
        "-Xmx512m",
        "-Dfile.encoding=UTF-8",
        "-Dstdout.encoding=UTF-8",
        "-jar",
        JAR,
    ]
    assert kwargs == {"input": DOCUMENT, "capture_output": True, "timeout": 60}


def test_jar_is_in_the_package():
    assert Path(JAR).is_file()


def test_stderr_with_exit_code_zero_is_success(monkeypatch):
    fake_run(monkeypatch, stdout=b"text", stderr=b"WARNING: POI warning")
    assert convert(DOCUMENT) == "text"


def test_empty_stdout_with_exit_code_zero_is_success(monkeypatch, caplog):
    """A document without text gives empty output; it is not an error."""
    fake_run(monkeypatch, stdout=b"")
    with caplog.at_level(logging.DEBUG, logger="c2.transform.msoffice"):
        assert convert(DOCUMENT) == ""
    assert [r.levelname for r in caplog.records] == ["DEBUG"]


def test_stdout_that_is_not_utf8_does_not_raise(monkeypatch):
    fake_run(monkeypatch, stdout=b"ok \xff\xfe end")
    assert convert(DOCUMENT) == "ok �� end"


def test_non_zero_exit_code(monkeypatch, caplog):
    stderr = b"java.lang.IllegalArgumentException: UNKNOWN is not supported"
    fake_run(monkeypatch, returncode=1, stdout=b"partial", stderr=stderr)
    assert convert(DOCUMENT) == ""
    assert [(r.levelname, r.getMessage()) for r in caplog.records] == [
        ("ERROR", "msdoc2txt failed with exit code 1")
    ]


def test_stderr_is_not_logged(monkeypatch, caplog):
    """A Java exception can quote the document, for example a part name."""
    stderr = b"org.apache.poi.POIXMLException: /word/secret-part-name.xml"
    fake_run(monkeypatch, returncode=1, stderr=stderr)
    with caplog.at_level(logging.DEBUG, logger="c2.transform.msoffice"):
        assert convert(DOCUMENT) == ""
    assert "secret-part-name" not in caplog.text
    assert "secret document body" not in caplog.text


def test_timeout(monkeypatch, caplog):
    fake_run(
        monkeypatch,
        error=subprocess.TimeoutExpired(["java"], 60, output=b"partial"),
    )
    assert convert(DOCUMENT) == ""
    assert [r.getMessage() for r in caplog.records] == [
        "msdoc2txt timed out after 60 seconds"
    ]


def test_java_not_found(monkeypatch, caplog):
    fake_run(monkeypatch, error=FileNotFoundError(2, "No such file", "java"))
    assert convert(DOCUMENT) == ""
    assert [r.getMessage() for r in caplog.records] == [
        "msdoc2txt could not run: java was not found"
    ]


def test_other_exception(monkeypatch, caplog):
    fake_run(monkeypatch, error=OSError("Too many open files"))
    assert convert(DOCUMENT) == ""
    assert [r.getMessage() for r in caplog.records] == ["msdoc2txt could not run"]
    assert caplog.records[0].exc_info is not None


def test_str_input_is_not_sent_to_java(monkeypatch, caplog):
    run = fake_run(monkeypatch, stdout=b"never")
    assert convert("not bytes") == ""
    assert run.calls == []
    assert [r.getMessage() for r in caplog.records] == [
        "msoffice_to_text expects bytes, got str; no text is extracted"
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, 60),
        ("", 60),
        ("120", 120),
        (" 5 ", 5),
    ],
)
def test_timeout_from_environment(monkeypatch, value, expected):
    if value is not None:
        monkeypatch.setenv("C2_TRANSFORM_MSOFFICE_TIMEOUT", value)
    run = fake_run(monkeypatch, stdout=b"x")
    convert(DOCUMENT)
    assert run.calls[0][1]["timeout"] == expected


@pytest.mark.parametrize("value", ["abc", "0", "-3", "1.5", "²"])
def test_invalid_timeout_falls_back_to_default(monkeypatch, caplog, value):
    monkeypatch.setenv("C2_TRANSFORM_MSOFFICE_TIMEOUT", value)
    run = fake_run(monkeypatch, stdout=b"x")
    convert(DOCUMENT)
    assert run.calls[0][1]["timeout"] == 60
    assert [r.getMessage() for r in caplog.records] == [
        f"Ignoring C2_TRANSFORM_MSOFFICE_TIMEOUT={value!r}: "
        "expected a positive integer; using 60"
    ]


def test_java_opts_from_environment(monkeypatch):
    monkeypatch.setenv("C2_TRANSFORM_MSOFFICE_JAVA_OPTS", "-Xmx1g  -XX:+UseSerialGC")
    run = fake_run(monkeypatch, stdout=b"x")
    convert(DOCUMENT)
    assert run.calls[0][0] == [
        "java",
        "-Xmx1g",
        "-XX:+UseSerialGC",
        "-Dfile.encoding=UTF-8",
        "-Dstdout.encoding=UTF-8",
        "-jar",
        JAR,
    ]


def test_blank_java_opts_use_default(monkeypatch):
    monkeypatch.setenv("C2_TRANSFORM_MSOFFICE_JAVA_OPTS", "  ")
    run = fake_run(monkeypatch, stdout=b"x")
    convert(DOCUMENT)
    assert run.calls[0][0][1] == "-Xmx512m"


def test_java_opts_that_cannot_be_parsed(monkeypatch, caplog):
    monkeypatch.setenv("C2_TRANSFORM_MSOFFICE_JAVA_OPTS", '-Xmx1g "-Dunclosed')
    run = fake_run(monkeypatch, stdout=b"x")
    assert convert(DOCUMENT) == ""
    assert run.calls == []
    assert [r.getMessage() for r in caplog.records] == [
        "JVM options in C2_TRANSFORM_MSOFFICE_JAVA_OPTS could not be parsed"
    ]
    assert caplog.records[0].exc_info is None
