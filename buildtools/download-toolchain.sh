#!/usr/bin/env bash
# Download the build toolchain pieces that are flaky/slow over the default network
# path and place them where the desktop build expects them. Mirrors: npmmirror.
#
# Usage:
#   DSH_REPO=/path/to/deepseek-harness ./download-toolchain.sh
#
# Resolves deepseek-harness via DSH_REPO, falling back to a sibling directory of
# this repo's parent (same layout this build was produced on).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${DSH_REPO:-$(cd "$HERE/../.." && pwd)/deepseek-harness}"
DOWNLOADS="$REPO/apps/desktop/.desktop-build/downloads"
mkdir -p "$DOWNLOADS"

echo "==> toolchain target repo: $REPO"

echo "==> 1/3 install undici (proxy bootstrap for global fetch)"
( cd "$HERE" && npm install undici )

echo "==> 2/3 download electron ${EVER:-44.7.0} via npmmirror into @electron/get cache"
EVER=44.7.0
FNAME="electron-v${EVER}-darwin-x64.zip"
# @electron/get cache key = sha256 of the *github release dirname* (the real download URL host+dir)
KEY="$(python3 -c "import hashlib,os,urllib.parse;u=urllib.parse.urlparse('https://github.com/electron/electron/releases/download/v${EVER}/${FNAME}');u=u._replace(fragment='',query='');print(hashlib.sha256((u.scheme+'://'+u.netloc+os.path.dirname(u.path)).encode()).hexdigest())")"
CACHE_DIR="$DOWNLOADS/$KEY"
mkdir -p "$CACHE_DIR"
if [ ! -s "$CACHE_DIR/$FNAME" ]; then
  curl -sL --noproxy '*' -o "$CACHE_DIR/$FNAME" \
    "https://cdn.npmmirror.com/binaries/electron/v${EVER}/${FNAME}"
  echo "    electron -> $CACHE_DIR/$FNAME"
else
  echo "    electron already cached"
fi

echo "==> 3/3 download dmgbuild-bundle via npmmirror"
BVER=1.2.5
BHASH=75c8a6c
DMG_TAR="dmgbuild-bundle-x86_64-${BHASH}.tar.gz"
if [ ! -x "$HERE/dmgbuild-bundle/dmgbuild" ]; then
  curl -sL --noproxy '*' -o "/tmp/$DMG_TAR" \
    "https://cdn.npmmirror.com/binaries/electron-builder-binaries/dmg-builder@${BVER}/${DMG_TAR}"
  mkdir -p "$HERE/dmgbuild-bundle"
  tar -xzf "/tmp/$DMG_TAR" -C "$HERE/dmgbuild-bundle"
  chmod +x "$HERE/dmgbuild-bundle/dmgbuild" "$HERE/dmgbuild-bundle/python/bin/dmgbuild"
  echo "    dmgbuild -> $HERE/dmgbuild-bundle/dmgbuild"
else
  echo "    dmgbuild already present"
fi

echo "==> done. Use these env vars when building:"
echo "    export CUSTOM_DMGBUILD_PATH=$HERE/dmgbuild-bundle/dmgbuild"
echo "    (undici proxy bootstrap is wired via NODE_OPTIONS in the build command — see BUILD.md)"
