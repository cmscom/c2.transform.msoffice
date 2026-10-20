# Notes for contributors and coding agents

## Rules

- This is a public package. Write code, comments, documentation, commit
  messages and pull requests in English.
- Do not add design documents, specs or plans to the repository.
- Record user-facing changes as towncrier fragments in `news/`
  (`news/+<name>.<type>` or `news/<issue>.<type>`, types as in
  `pyproject.toml`), not in `CHANGELOG.md`.

## Layout

- `src/c2/transform/msoffice/`: the package. `c2` and `c2.transform` are
  PEP 420 namespace packages, so they have no `__init__.py`.
  - `transform.py`: the `msoffice_to_text` transform that runs the jar.
  - `config.py`: MIME types; importing it adds them to `mimetypes`.
  - `setuphandlers.py`: install and uninstall (`post_handler`s).
  - `msdoc2txt.jar`: the bundled Java program (Apache POI 5.5.1), built
    from `java/` with `java/build.sh`; do not change it by hand.
- `tests/`: pytest tests (not shipped in the wheel).
  - `test_transform.py`, `test_config.py`: unit tests; `java` is replaced.
  - `test_setup.py`: install and uninstall in a Plone site.
  - `test_java.py`: runs the real jar on the files in `tests/samples/`.
- `java/`: the source of `msdoc2txt.jar` (see `java/README.md`).
  - `build.sh`: builds the jar reproducibly in a pinned container.
  - `check-output.sh`: compares the output of a jar for the samples with
    `java/expected/`, byte for byte.

## Development

Run the tests and the linters with tox:

```shell
tox -e py314-Plone62      # one Python and Plone version
tox -e ruff-check         # lint and format check
tox -e ruff-fix           # fix and format
tox -e mypy               # type check src and tests
tox                       # the whole matrix
```

Extra arguments go to pytest, for example
`tox -e py314-Plone62 -- tests/test_transform.py`.

`tests/test_java.py` needs `java` on `PATH`. Without it the tests are
skipped; set `C2_TRANSFORM_MSOFFICE_REQUIRE_JAVA=1` to make them fail
instead, as CI does. Write expected values in tests as literals.

After a change in `java/`, run `java/build.sh` (needs Docker) and
`java/check-output.sh src/c2/transform/msoffice/msdoc2txt.jar`, and commit
the jar with the change; CI rebuilds it and fails if it differs. If the
output changes, find out why before you change a file in `java/expected/`.

## Test samples

All files in `tests/samples/` were made for this package; do not add
documents of unknown origin. The `.docx`, `.doc`, `.xlsx`, `.xls` and
`presentation.pptx` files were converted with LibreOffice in headless mode
from short text and CSV files (`soffice --headless --convert-to docx
document.txt`, the CSV with `--infilter="CSV:44,34,76,1"`, and the
presentation by converting a PDF of the text with
`--infilter=impress_pdf_import`); `<cp:revision>` was then removed from
`docProps/core.xml` of the OOXML files, because the jar prints it as text. `empty.docx` is a converted empty text file.

`presentation.ppt` was written with the Apache POI 3.17 classes of the jar
bundled at the time (`HSLFSlideShow` with one text box), because it is much
smaller than the one LibreOffice writes. POI's empty template names a person
as the last editor in the Current User stream, so the name was cleared with
`getSlideShowImpl().getCurrentUserAtom().setLastEditUsername("")`.

`presentation-notes.pptx` was written with the same POI classes
(`XMLSlideShow` with one text box and speaker notes; on the notes slide only
the body placeholder was kept), and `<cp:revision>` was removed as above.
`presentation-notes.ppt` is that file converted with LibreOffice in headless
mode (`soffice --headless --convert-to ppt`), because POI cannot create
notes in a `.ppt`.

Check new samples for names in their metadata before adding them, and add
their output to `java/expected/`.
