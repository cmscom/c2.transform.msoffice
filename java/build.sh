#!/bin/bash
# Build msdoc2txt.jar reproducibly in a pinned container: the same image
# and the pinned plugins give the same jar, byte for byte.
# Usage: java/build.sh [OUTPUT]  (default: src/c2/transform/msoffice/msdoc2txt.jar)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=${1:-$here/../src/c2/transform/msoffice/msdoc2txt.jar}
# maven:3.9.16-eclipse-temurin-21-noble (2026-09-26)
image=maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320
# Downloaded dependencies are kept between builds, outside the repository.
cache=${MSDOC2TXT_M2_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/msdoc2txt-m2}
mkdir -p "$cache"
docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e MAVEN_CONFIG=/var/maven/.m2 \
    -v "$cache":/var/maven/.m2 \
    -v "$here":/build -w /build \
    "$image" mvn -B -q -Duser.home=/var/maven clean package
cp "$here/target/msdoc2txt.jar" "$out"
sha256sum "$out"
