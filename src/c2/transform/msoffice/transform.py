"""Extract plain text from Microsoft Office files with the bundled jar."""

from c2.transform.msoffice import logger
from c2.transform.msoffice.config import SITE_CHARSET
from c2.transform.msoffice.config import TRANSFORM_NAME
from pathlib import Path
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer

import os
import shlex
import subprocess


JAR_PATH = Path(__file__).with_name("msdoc2txt.jar")

TIMEOUT_ENV = "C2_TRANSFORM_MSOFFICE_TIMEOUT"
JAVA_OPTS_ENV = "C2_TRANSFORM_MSOFFICE_JAVA_OPTS"
DEFAULT_TIMEOUT = 60
DEFAULT_JAVA_OPTS = ("-Xmx512m",)
# The jar writes text in the JVM's default encoding. JDK 8-17 take it from
# file.encoding and JDK 19+ from stdout.encoding, so both are always set.
# They come after the options from the environment so they always win.
ENCODING_OPTS = ("-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8")


def timeout() -> int:
    """Seconds to wait for the jar, from the environment or the default."""
    value = os.environ.get(TIMEOUT_ENV, "").strip()
    if not value:
        return DEFAULT_TIMEOUT
    try:
        seconds = int(value)
    except ValueError:
        # Not only "abc": str.isdigit() accepts "²", which int() rejects.
        seconds = 0
    if seconds > 0:
        return seconds
    logger.warning(
        "Ignoring %s=%r: expected a positive integer; using %d",
        TIMEOUT_ENV,
        value,
        DEFAULT_TIMEOUT,
    )
    return DEFAULT_TIMEOUT


def java_command() -> list[str]:
    java_opts = shlex.split(os.environ.get(JAVA_OPTS_ENV, "")) or DEFAULT_JAVA_OPTS
    return ["java", *java_opts, *ENCODING_OPTS, "-jar", str(JAR_PATH)]


def msdoc2txt(data: bytes) -> str | None:
    """Return the text of an Office document, or None if extraction failed.

    The document goes to the jar on stdin and the text comes back on stdout.
    The exit code decides success: an empty stdout with exit code 0 is a
    document without text. Neither the document, the text nor the jar's
    stderr is logged: a Java exception can quote parts of the document.
    """
    seconds = timeout()
    try:
        command = java_command()
    except ValueError:
        # shlex could not split the options, for example an unclosed quote.
        logger.error("JVM options in %s could not be parsed", JAVA_OPTS_ENV)
        return None
    try:
        result = subprocess.run(  # noqa: S603
            command, input=data, capture_output=True, timeout=seconds
        )
    except subprocess.TimeoutExpired:
        # subprocess.run kills the process and waits for it.
        logger.error("msdoc2txt timed out after %d seconds", seconds)
        return None
    except FileNotFoundError:
        logger.error("msdoc2txt could not run: java was not found")
        return None
    except Exception:
        logger.exception("msdoc2txt could not run")
        return None
    if result.returncode != 0:
        logger.error("msdoc2txt failed with exit code %d", result.returncode)
        return None
    if not result.stdout:
        logger.debug("msdoc2txt returned no text")
    return result.stdout.decode("utf-8", errors="replace")


@implementer(ITransform)
class msoffice_to_text:
    __name__ = TRANSFORM_NAME

    inputs = (
        # MS-Word formats
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-word.document.macroEnabled.12",
        # MS-Excel formats
        "application/vnd.ms-excel",
        "application/msexcel",
        "application/x-msexcel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
        "application/vnd.ms-excel.sheet.macroEnabled.12",
        # MS-PowerPoint formats
        "application/vnd.ms-powerpoint",
        "application/powerpoint",
        "application/mspowerpoint",
        "application/x-mspowerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
    )

    output = "text/plain"

    output_encoding = SITE_CHARSET

    def __init__(self, name: str | None = None) -> None:
        if name:
            self.__name__ = name

    def name(self) -> str:
        return self.__name__

    def convert(
        self, orig: bytes | str, data: datastream, **kwargs: object
    ) -> datastream:
        """Set the text of ``orig`` (bytes) on ``data``.

        ``data`` is the datastream that portal_transforms made for the result.
        On any failure the text is empty, so saving the file still works.
        """
        if not isinstance(orig, bytes):
            logger.error(
                "msoffice_to_text expects bytes, got %s; no text is extracted",
                type(orig).__name__,
            )
            data.setData("")
            return data
        text = msdoc2txt(orig)
        data.setData(text or "")
        return data


def register() -> msoffice_to_text:
    return msoffice_to_text()
