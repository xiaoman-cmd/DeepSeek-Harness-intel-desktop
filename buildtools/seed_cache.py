#!/usr/bin/env python3
"""Pre-seed the primary-runtime download cache (sha256-named files) via DIRECT connection.
The desktop build's downloadPrimaryRuntimeAsset first checks join(cache, sha256); if present it
skips the network entirely. We populate that cache so the proxy-flaky large downloads are avoided.
"""
import hashlib, json, os, sys, urllib.parse, urllib.request

# Resolve the deepseek-harness checkout. Override with DSH_REPO if checked out elsewhere.
# Default assumes deepseek-harness is a sibling of this repo's parent directory.
REPO = os.environ.get("DSH_REPO") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "deepseek-harness"))
CACHE = os.path.join(REPO, "apps/desktop/.desktop-build/downloads")
LOCK = os.path.join(REPO, "scripts/primary-runtime/lock.json")
UA = {"User-Agent": "curl/8.0"}

def build_assets():
    d = json.load(open(LOCK))
    nv = d["nodeVersion"]; pv = d["pythonVersion"]; pr = d["pythonRelease"]
    t = d["targets"]["mac-x64"]
    assets = []
    # Node
    node_fn = f"node-v{nv}-{t['nodeArchive']}"
    assets.append((f"https://nodejs.org/dist/v{nv}/{node_fn}", t["nodeSha256"], "sha256"))
    # Python (filename encodeURIComponent'd like the build does)
    py_fn = f"cpython-{pv}+{pr}-{t['pythonTarget']}-install_only_stripped.tar.gz"
    py_url = "https://github.com/astral-sh/python-build-standalone/releases/download/" + pr + "/" + urllib.parse.quote(py_fn, safe="")
    assets.append((py_url, t["pythonSha256"], "sha256"))
    # Wheels: target-specific + global
    for w in t["wheels"] + d["wheels"]:
        assets.append((w["url"], w["sha256"], "sha256"))
    return assets

def download(url, dest_tmp, algo):
    h = hashlib.new(algo)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as resp:
        total = int(resp.headers.get("content-length") or 0)
        got = 0
        with open(dest_tmp, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                got += len(chunk)
        return h.hexdigest(), total

def main():
    os.makedirs(CACHE, exist_ok=True)
    assets = build_assets()
    print(f"Seeding {len(assets)} assets into {CACHE}")
    ok = 0
    for url, sha, algo in assets:
        dest = os.path.join(CACHE, sha)
        if os.path.exists(dest):
            # verify existing
            h = hashlib.new(algo)
            with open(dest, "rb") as f:
                for c in iter(lambda: f.read(1 << 20), b""):
                    h.update(c)
            if h.hexdigest() == sha:
                print(f"[CACHED] {sha[:12]} {url.split('/')[-1]}")
                ok += 1
                continue
            else:
                os.remove(dest)
        tmp = dest + ".part"
        print(f"[GET] {url.split('/')[-1]} ...", end=" ", flush=True)
        try:
            got_sha, total = download(url, tmp, algo)
            if got_sha != sha:
                os.remove(tmp)
                print(f"SHA MISMATCH (got {got_sha[:12]} want {sha[:12]})")
                continue
            os.rename(tmp, dest)
            print(f"OK {total//1024}KB")
            ok += 1
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            print(f"FAIL {type(e).__name__}: {str(e)[:120]}")
    print(f"DONE: {ok}/{len(assets)} seeded")
    sys.exit(0 if ok == len(assets) else 1)

if __name__ == "__main__":
    main()
