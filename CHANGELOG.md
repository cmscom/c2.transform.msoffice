# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 2.0.0b1 (2026-10-20)


### Breaking changes:

- Java 11 or later is required (1.0b6 ran on Java 8). [terapyon] 
- Support Plone 6.0, 6.1 and 6.2 on Python 3.10 to 3.14 only. Python 2, Plone 3 to 5 and the Windows code are removed. [terapyon] 
- The profile version is now `2000` and there is no upgrade step from 1.0b6: deactivate and activate the add-on again after upgrading. [terapyon] 
- `c2` and `c2.transform` are now PEP 420 namespace packages. Sites that also use `c2.*` packages with `pkg_resources` namespaces need `horse-with-no-namespace`. [terapyon] 


### New features:

- Add an uninstall profile that removes the transform, and register `application/vnd.ms-powerpoint` as an input explicitly. [terapyon] 
- Add the `C2_TRANSFORM_MSOFFICE_TIMEOUT` and `C2_TRANSFORM_MSOFFICE_JAVA_OPTS` environment variables for the timeout and the JVM options. [terapyon] 
- The bundled jar is built with Apache POI 5.5.1 (was 3.17). Its Java source is now in `java/`, with a reproducible build that CI checks. [terapyon] 


### Bug fixes:

- Always pass `-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8` to `java`, so non-ASCII text is not replaced by `?` when the process has no locale (for example in slim container images). [terapyon] 
- Decide success by the exit code of `java`. Text is no longer thrown away when the jar writes a warning to stderr, and a document without text no longer logs an error. A failed run logs its exit code but not the error output of `java`, which can quote parts of the document. [terapyon] 
- Extract text from `.ppt` files (PowerPoint 97-2003). The bundled jar closed the file before it read the text, so every `.ppt` gave no text. [terapyon] 
- Log text input and give empty text instead of failing an `assert`. [terapyon] 


### Internal:

- Move to `pyproject.toml` and a `src/` layout, with tox, pytest, ruff, towncrier, zest.releaser and a GitHub Actions workflow that runs the tests with Java. Replace the test sample with self-made documents. [terapyon] 

## 1.0b6 (2018-04-02)

- change from POI 3.6 to POI 3.17 with Java 8 [Tetsuya Morimoto]

## 1.0b5 (2018-02-28)

- modify setup.py for target Plone [terapyon]
- tested Plone 5.1

## 1.0b4 (2013-03-16)

- modify kill process for Popen [Takayuki Nagai]

## 1.0b3 (2010-10-06)

- adding terminated suspicious zombie process [terapyon]

## 1.0b2 (2010-02-19)

- remove the copyright in the files [terapyon]

## 1.0b1 (2010-02-01)

- modify getting from metadata and note in the msoffice file [terapyon]
- no support for Windows [terapyon]

## 0.3.2 (2010-01-19)

- setting some mimetypes [terapyon]

## 0.3.1 (2009-12-22)

- bug fix for Windows [terapyon]

## 0.3 (2009-12-22)

- support Windows OS

## 0.2 (2009-12-21)

- support Plone 4.x [terapyon]

## 0.1.2 (2009-12-17)

- modify typo

## 0.1.1 (2009-12-16)

- modify exception code
- adding java args for big size file

## 0.1 (2009-12-16)

- Initial release
