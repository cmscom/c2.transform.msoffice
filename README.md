# c2.transform.msoffice

Make Microsoft Office files searchable in Plone.

The package adds a `portal_transforms` transform, `msoffice_to_text`, that
extracts plain text from Word, Excel and PowerPoint files. Plone uses it to
index the text of uploaded File objects, so a search finds words inside the
documents.

Text is extracted by a bundled Java program (`msdoc2txt.jar`, built on
[Apache POI](https://poi.apache.org/) 5.5.1). Its source is in `java/`.

## Supported versions

- Plone 6.0, 6.1 and 6.2
- Python 3.10 to 3.14 (as far as each Plone version supports them)
- Java 11 or later on `PATH` (CI checks the jar with Temurin 11 and 21)
- Linux and other POSIX systems. Windows is not supported.

## Accepted MIME types

The transform is registered for these MIME types:

- Word: `application/msword`,
  `application/vnd.openxmlformats-officedocument.wordprocessingml.document`,
  `application/vnd.ms-word.document.macroEnabled.12`
- Excel: `application/vnd.ms-excel`, `application/msexcel`,
  `application/x-msexcel`,
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
  `application/vnd.ms-excel.sheet.binary.macroEnabled.12`,
  `application/vnd.ms-excel.sheet.macroEnabled.12`
- PowerPoint: `application/vnd.ms-powerpoint`, `application/powerpoint`,
  `application/mspowerpoint`, `application/x-mspowerpoint`,
  `application/vnd.openxmlformats-officedocument.presentationml.presentation`,
  `application/vnd.ms-powerpoint.presentation.macroEnabled.12`

### Tested formats

The tests extract text from `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx` and
`.ppt` files, including the speaker notes of presentations. The other
formats are passed to the jar but are not covered by the tests.

## Installation

1. Install Java 11 or later (a headless JRE is enough) so that `java` is on
   the `PATH` of the Zope process.
2. Add `c2.transform.msoffice` to your project's dependencies, for example
   with pip:

   ```shell
   pip install c2.transform.msoffice
   ```

3. Restart Zope and activate **c2.transform.msoffice** in the add-ons control
   panel (or apply the `c2.transform.msoffice:default` profile).

Existing File objects get their text indexed the next time they are
reindexed, for example with "Clear and Rebuild" in the catalog.

### Upgrading from 1.0b6

2.0 needs Java 11 or later; 1.0b6 ran on Java 8.

2.0 has no upgrade step from 1.0b6. After upgrading the package, deactivate
the add-on and activate it again in the add-ons control panel. This replaces
the transform that 1.0b6 registered.

1.0b6 used `pkg_resources` namespace packages; 2.0 uses PEP 420 namespace
packages. If your site also uses other `c2.*` packages that still declare a
`pkg_resources` namespace, install
[horse-with-no-namespace](https://pypi.org/project/horse-with-no-namespace/)
so that both kinds can be imported together.

## How it works

For each document, the transform starts `java` with the bundled jar, writes
the document to its standard input and reads the text from its standard
output:

```shell
java -Xmx512m -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -jar msdoc2txt.jar < document.docx
```

- The text is always written in UTF-8, also when the process has no locale
  (as in slim container images).
- The exit code decides success. A document without text gives empty text.
- If `java` cannot be run, exits with an error or takes too long, the text is
  empty and an error is logged. Saving the file is not affected.
- Neither the document, its text nor the error output of `java` is written
  to the log, because a Java exception can quote parts of the document. A
  failed run logs only its exit code.

## Configuration

Set these environment variables for the Zope process:

- `C2_TRANSFORM_MSOFFICE_TIMEOUT`: seconds to wait for `java` before it is
  killed. Default `60`.
- `C2_TRANSFORM_MSOFFICE_JAVA_OPTS`: JVM options, split like a shell command
  line. They replace the default `-Xmx512m`, for example
  `-Xmx1g -XX:+UseSerialGC`. The encoding options are always added.

## Memory

Each transform runs its own JVM. Up to one JVM per Zope thread can run at the
same time, each with a heap of up to 512 MB (by default) plus the memory of
the JVM itself. Plan the memory of the server or container for that.

## Uninstall

Deactivate the add-on in the add-ons control panel. This removes the
transform. The MIME types are kept, because other add-ons may use them.

## Source code

- This package: <https://github.com/cmscom/c2.transform.msoffice>
- Java program: `java/` in this repository (moved from
  <https://bitbucket.org/cmscom/msdoc2txt>)

## Credits

This code was inspired by Products.OpenXml.

## Contributors

- Manabu Terada (main code)
- Mikio Hokari (Java code and extended calls)
- Takashi Nagai (Windows support)
- Takayuki Nagai (bug fix for 1.0b4)
- Tetsuya Morimoto (refactoring of the Java code and POI 3.17 support)

## License

c2.transform.msoffice is licensed under the GNU General Public License,
version 2 or later. See `LICENSE.txt` and `LICENSE.GPL`.

The bundled `msdoc2txt.jar` contains libraries under the Apache License 2.0
(some of their license files have additional terms, for example for the
ECMA-376 schemas in Apache POI) and under a BSD license (curvesapi). They
are compatible with the package when it is used under the GPL version 3.
The license files are in the jar, under `META-INF/`; see `java/README.md`.
