# msdoc2txt

The Java program behind c2.transform.msoffice. It reads a Microsoft Office
file on standard input and writes its text to standard output:

```shell
java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -jar msdoc2txt.jar < document.docx
```

It reads Word, Excel and PowerPoint files, both the binary (`.doc`, `.xls`,
`.ppt`) and the OOXML (`.docx`, `.xlsx`, `.pptx`) formats, with
[Apache POI](https://poi.apache.org/) 5.5.1, and RTF files with
[RTF Parser Kit](https://github.com/joniles/rtfparserkit). The output has
the non-empty parts in this order, each followed by a line break: document
properties, headers, footers, notes, text. On success the exit code is 0
and nothing is written to standard error; otherwise the exit code is not 0.

`--file PATH` reads a file instead of standard input, `--verbose` logs the
steps to standard error, and `--help` shows the options.

This source was moved here, with its history, from
<https://bitbucket.org/cmscom/msdoc2txt> (commit 290d060).

## Building

The jar is built in a container, so only Docker is needed:

```shell
java/build.sh
```

This writes `src/c2/transform/msoffice/msdoc2txt.jar`, the jar that the
Python package uses, and prints its sha256. `java/build.sh OUTPUT` writes
the jar somewhere else. Maven downloads are cached in
`~/.cache/msdoc2txt-m2` (set `MSDOC2TXT_M2_CACHE` to change it).

The build is reproducible: the Maven image is pinned by digest in
`build.sh`, every Maven plugin and dependency is pinned in `pom.xml`, and
`project.build.outputTimestamp` fixes the time stamps in the jar. The same
source gives the same jar, byte for byte. CI rebuilds the jar and fails if
it differs from the committed one, so commit the jar together with the
change of the source.

The bytecode targets Java 11 (`--release 11`); the jar runs on Java 11 or
later.

## Checking the output

```shell
java/check-output.sh src/c2/transform/msoffice/msdoc2txt.jar
```

runs the jar on the files in `tests/samples/` and compares the output, byte
for byte, with `java/expected/<sample>.txt`. It also checks the exit code
and that standard error is empty. Set `JAVA` to use another `java`. CI runs
it with Java 11 and Java 21.

When the output changes, find out why before you change an expected file.

## Updating a dependency

1. Change the version in `pom.xml` and set `project.build.outputTimestamp`
   to the current date.
2. Run `java/build.sh` and `java/check-output.sh`.
3. Commit `pom.xml`, the jar and, if the change is intended, the expected
   files.

`pom.xml` is part of the jar, so any change to it needs a rebuild, even a
change of a comment.

## How the jar is put together

`pom.xml` builds one jar with all dependencies, with maven-shade-plugin:

- POI finds its extractors with `ServiceLoader`. poi, poi-ooxml and
  poi-scratchpad each have a `META-INF/services` file with the same name;
  they are merged.
- The Log4j API, which POI uses, prints a warning to standard output when
  no logging implementation is present, and that would end up in the
  text. `src/main/resources/log4j2.component.properties` selects the
  simple provider of the API and turns it off.
- `module-info.class`, `META-INF/versions/` and signature files of the
  dependencies are left out.
- The manifest names the main class and the POI version
  (`Apache-POI-Version`).

## Licenses

The jar contains these libraries. Most are under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0):
Apache POI, XMLBeans, Commons (CLI, Codec, Collections, Compress, IO, Lang,
Math), the Log4j API, SparseBitSet and RTF Parser Kit. The license files of
POI and Commons Math have additional terms for parts of them, for example
for the ECMA-376 schemas in POI. curvesapi is under a BSD license.

The license and notice files that the libraries ship are kept in the jar
(the SparseBitSet and RTF Parser Kit jars have none): `META-INF/LICENSE` and
`META-INF/LICENSE.txt` have the license files one after another, and
`META-INF/NOTICE` the merged notices.
curvesapi has no license file in its jar, so `licenses/curvesapi-LICENSE.txt`
is a copy of `license.txt` of curvesapi 1.08
(<https://github.com/virtuald/curvesapi/blob/1.08/license.txt>); it goes
into the jar as `META-INF/LICENSE-curvesapi.txt`.
