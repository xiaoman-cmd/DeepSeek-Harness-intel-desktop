#!/usr/bin/env python3
"""Pre-seed the Electron distribution into the @electron/get cache so the
desktop build skips the (unreliable) proxy download. Cache layout (from
@electron/get Cache.js): cacheRoot/<sha256(dirname of downloadUrl)>/<fileName>.
"""
import hashlib
import os
import urllib.request

VERSION = "44.7.0"
PLATFORM = "darwin"
ARCH = "x64"
# Resolve the deepseek-harness .desktop-build/downloads dir. Override with
# DSH_DOWNLOADS / DSH_REPO if checked out elsewhere.
_DOWNLOADS_REPO = os.environ.get("DSH_REPO") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "deepseek-harness"))
DOWNLOADS = os.environ.get("DSH_DOWNLOADS") or os.path.join(_DOWNLOADS_REPO, "apps/desktop/.desktop-build/downloads")
URL = f"https://github.com/electron/electron/releases/download/v{VERSION}/electron-v{VERSION}-{PLATFORM}-{ARCH}.zip"
FILENAME = f"electron-v{VERSION}-{PLATFORM}-{ARCH}.zip"

# cache dir = sha256 of URL with hash/search stripped and pathname -> dirname
from urllib.parse import urlparse
parsed = urlparse(URL)
parsed = parsed._replace(fragment="", query="")
dirname = os.path.dirname(parsed.path)
norm = f"{parsed.scheme}://{parsed.netloc}{dirname}"
cache_dir = hashlib.sha256(norm.encode()).hexdigest()

dest_dir = os.path.join(DOWNLOADS, cache_dir)
dest = os.path.join(dest_dir, FILENAME)
os.makedirs(dest_dir, exist_ok=True)

print(f"[seed] URL={URL}")
print(f"[seed] cache_dir(sha256)={cache_dir}")
print(f"[seed] dest={dest}")

if os.path.exists(dest) and os.path.getsize(dest) > 0:
    print("[seed] already present, skip")
else:
    tmp = dest + ".part"
    print(f"[seed] downloading (sandbox direct) ...")
    req = urllib.request.Request(URL, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
        total = 0
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    os.rename(tmp, dest)
    print(f"[seed] OK {total//1024}KB")

print("[seed] done")
