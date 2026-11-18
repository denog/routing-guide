#!/bin/sh
# Build a VyOS rolling container image from the nightly ISO.
# The squashfs is extracted in a throwaway Debian container, so the host
# only needs docker and curl.
#
# Usage: ./build.sh 2026.11.15-0018-rolling
set -eu

RELEASE="$1"
ISO="vyos-${RELEASE}-generic-amd64.iso"
URL="https://github.com/vyos/vyos-nightly-build/releases/download/${RELEASE}/${ISO}"
TAG="vyos:${RELEASE}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cd "$(dirname "$0")"
cp Dockerfile "$WORK/"

echo "downloading ${URL}"
curl -fL --retry 5 -o "$WORK/$ISO" "$URL"
sha256sum "$WORK/$ISO"

docker run --rm -v "$WORK:/work" -w /work debian:bookworm-slim sh -c "
  apt-get update -qq &&
  apt-get install -y -qq squashfs-tools-ng libarchive-tools >/dev/null &&
  bsdtar -xf $ISO live/filesystem.squashfs &&
  sqfs2tar live/filesystem.squashfs > rootfs.tar &&
  rm -rf live $ISO"

docker build -t "$TAG" "$WORK"
echo "built ${TAG}"
