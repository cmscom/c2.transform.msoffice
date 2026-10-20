#!/bin/bash
# Run msdoc2txt.jar on the test samples and compare its output, byte for
# byte, with java/expected/. Usage: java/check-output.sh path/to/msdoc2txt.jar
# Set JAVA to use another java command.
set -u
here=$(cd "$(dirname "$0")" && pwd)
samples="$here/../tests/samples"
jar=${1:?usage: check-output.sh path/to/msdoc2txt.jar}
java=${JAVA:-java}
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
status=0
for expected in "$here"/expected/*.txt; do
    name=$(basename "$expected" .txt)
    rc=0
    LC_ALL=C "$java" -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -jar "$jar" \
        < "$samples/$name" > "$work/out" 2> "$work/err" || rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "FAIL $name: exit code $rc"
        head -c 2000 "$work/err"
        echo
        status=1
        continue
    fi
    if [ -s "$work/err" ]; then
        echo "FAIL $name: stderr is not empty"
        head -c 2000 "$work/err"
        echo
        status=1
        continue
    fi
    if ! cmp -s "$expected" "$work/out"; then
        echo "FAIL $name: output differs (expected, actual)"
        diff <(od -c "$expected") <(od -c "$work/out") | head -40
        status=1
        continue
    fi
    echo "OK   $name"
done
exit $status
