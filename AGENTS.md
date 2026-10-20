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
- `tests/`: pytest tests (not shipped in the wheel or the sdist).
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

## Releasing

Releases are made only by `.github/workflows/release.yml` on GitHub
Actions; nothing is needed on a maintainer's machine. It publishes to PyPI
with Trusted Publishing, so no PyPI token is used. The version is kept only
in `pyproject.toml`. The steps that need code are in
`.github/scripts/release.py`, tested by `tests/test_release_script.py`.

1. Make sure that `main` has the news fragments of the release in `news/`.
2. In GitHub: **Actions**, **Release**, **Run workflow**, branch `main`,
   enter the version (such as `2.0.0b2`: PEP 440 in its normalized form,
   without `v`) and run it.
3. `prepare` stops unless the version is after the one in `pyproject.toml`,
   has no tag yet, is neither a development version nor both a pre-release
   and a post-release (such as `2.0.0b2.post1`), and the run is on `main`,
   with news fragments. Then it writes the fragments into `CHANGELOG.md`,
   sets the version, commits "Preparing release <version>" as
   github-actions[bot] and makes the annotated tag `<version>`.
   `push-release` pushes both to GitHub.
4. `test` runs the tests of `plone-package.yml` on that commit, and
   `build` builds and checks the sdist and the wheel (the wheel must
   contain `msdoc2txt.jar`).
5. `publish` waits for a reviewer of the `pypi` environment. Review the
   deployment and approve it; it then uploads to PyPI.
6. `sign` signs the files with Sigstore, and `github-release` makes a
   GitHub Release with them, their signatures and the section of this
   version from `CHANGELOG.md`. Versions with `a`, `b` or `rc` are marked
   as pre-releases.
7. `development` sets the next development version (`2.0.0b2` gives
   `2.0.0b3.dev0`, `2.0.0` gives `2.0.1.dev0`, `2.0.0.post1` gives
   `2.0.0.post2.dev0`) and commits "Back to development: <version>".
   `push-development` pushes it. If `main` has moved since the release
   commit, it stops without pushing and says in its log how to do it by
   hand.

Only `push-release`, `push-development` and `github-release` can write to
the repository. They run only `actions/checkout`,
`actions/download-artifact`, `git` and `gh`. The push jobs get the commits
of the jobs before them as git bundles and push them only if each is one
commit on the expected parent that changes only the expected files
(`pyproject.toml`, `CHANGELOG.md` and removed news fragments for the
release, `pyproject.toml` for the development version). Keep it so: do not
add steps with other actions or tools to these jobs.

Only one release runs at a time. A run started while another release runs
waits (GitHub keeps only the latest waiting run and cancels older ones),
then starts from the `main` of the time it was started; its `push-release`
fails because `main` has moved, and nothing is pushed. Run the workflow
again.

### When a release fails or is rejected

- Before `push-release` pushed, nothing has changed: fix the cause and run
  the workflow again.
- After `push-release` pushed, but before `publish` ran (the tests or the
  build failed, or the deployment was rejected): PyPI has nothing of this
  version. Delete the tag (`git push origin :refs/tags/<version>` and
  `git tag -d <version>`), revert "Preparing release <version>" on `main`
  (this brings the news fragments back) and push, fix the cause, and run
  the workflow again with the same version.
- If `publish` ran, look at <https://pypi.org/project/c2.transform.msoffice/> for
  the files of this version. If even one of them is there, do not delete
  the tag: PyPI never accepts the same file again. Re-run `publish` to
  upload the missing files (it skips the existing ones), then re-run the
  jobs after it. A re-run uses the files of the same run: before you go
  on, check that the sha256 of each file that PyPI has already is the one
  of the file in the `dist` artifact of the run. To fix the release
  itself, release the next version.
- If a re-run of `github-release` fails because the release already
  exists, add the missing files to it with
  `gh release upload <version> <files> --clobber` (the files of the
  `dist` artifact and their `.sigstore.json` of the `signatures` artifact
  of the run), or delete the GitHub Release and re-run the job.
- If `push-development` failed, re-run it, or set the development version
  by hand as its log says.

### Settings needed once

- PyPI: the trusted publisher of `c2.transform.msoffice` is owner `cmscom`,
  repository `c2.transform.msoffice`, workflow `release.yml`, environment
  `pypi`.
- GitHub: the environment `pypi` with required reviewers. The workflow runs
  on the branch `main`, so a deployment rule of the environment must allow
  `main` (not only tags).
- `push-release` and `push-development` push to `main` with `GITHUB_TOKEN`.
  If `main` gets a branch protection rule or a ruleset, it must let these
  pushes through (as an exception for GitHub Actions); otherwise the
  release stops at the push. Check this when you add the protection.
  Commits pushed with `GITHUB_TOKEN` do not start other workflows, so
  `plone-package.yml` does not run again for them; the release runs those
  tests itself.

## Test samples

All files in `tests/samples/` were made for this package; do not add
documents of unknown origin. The `.docx`, `.doc`, `.xlsx`, `.xls` and
`presentation.pptx` files were converted with LibreOffice in headless mode
from short text and CSV files (`soffice --headless --convert-to docx
document.txt`, the CSV with `--infilter="CSV:44,34,76,1"`, and the
presentation by converting a PDF of the text with
`--infilter=impress_pdf_import`); `<cp:revision>` was then removed from
`docProps/core.xml` of the OOXML files, because the jar prints it as text.
`empty.docx` is a converted empty text file.

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
