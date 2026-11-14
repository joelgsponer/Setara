#!/bin/sh
# Tests the card update: a good newer pack is installed, damaged packs are
# ignored and the old pack stays, progress survives.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SAVE="$(mktemp -d)"
S="$SAVE/love/setara"
mkdir -p "$S/update" "$S/data"
cp -r "$ROOT/dist/card/setara/data/love/setara/packs" "$S/"
echo '{"stars":{"en-1-01-a":3},"tutorial_done":true}' > "$S/data/progress.json"
python3 - "$ROOT" "$S" <<'PY'
import json, sys, zipfile, shutil
root, s = sys.argv[1], sys.argv[2]
src = f"{root}/packs/en-1.zip"
# 1. a good pack, one version newer
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(f"{s}/update/en-1.zip", "w") as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "manifest.json":
            m = json.loads(data); m["version"] += 1; data = json.dumps(m).encode()
        zout.writestr(item, data)
# 2. a pack cut off half way through the copy
data = open(f"{root}/packs/core.zip", "rb").read()
open(f"{s}/update/core.zip", "wb").write(data[: len(data) // 2])
# 3. a pack with one damaged file inside and a higher version
with zipfile.ZipFile(f"{root}/packs/fa-1.zip") as zin, zipfile.ZipFile(f"{s}/update/fa-1.zip", "w") as zout:
    done = False
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "manifest.json":
            m = json.loads(data); m["version"] += 5; data = json.dumps(m).encode()
        elif item.filename.endswith(".ogg") and not done:
            data = data[:-10] + b"0123456789"; done = True
        zout.writestr(item, data)
# 4. an empty shell that claims to be a newer core pack
with zipfile.ZipFile(f"{s}/update/hollow.zip", "w") as z:
    z.writestr("manifest.json", json.dumps({"format": 1, "pack": "core", "kind": "core", "version": 9, "files": {}}))
# 5. a pack that is already installed in the same version: left alone
shutil.copy(f"{root}/packs/garden-1.zip", f"{s}/update/garden-1.zip")
before = open(f"{s}/packs/garden-1.v1.zip", "rb").read()
open(f"{s}/garden-before.bin", "wb").write(before)
PY
out="$("$ROOT/tools/shoot.sh" "$ROOT/tests/update/check.lua" 4 "$SAVE" 2>&1)"
echo "$out" | grep -E "^[A-Z0-9_]+="
fail=0
echo "$out" | grep -q "EN1_VERSION=2" || { echo "FAIL: newer pack not installed"; fail=1; }
echo "$out" | grep -q "CORE=true" || { echo "FAIL: core pack lost"; fail=1; }
echo "$out" | grep -q "REJECTED=3" || { echo "FAIL: damaged packs not rejected"; fail=1; }
echo "$out" | grep -q "LEFT_IN_UPDATE=0" || { echo "FAIL: update folder not emptied"; fail=1; }
ls "$S/packs" | grep -q "^en-1\.v2\.zip" || { echo "FAIL: en-1.v2.zip missing"; fail=1; }
ls "$S/packs" | grep -q "^en-1\.v1\.zip" && { echo "FAIL: old en-1 not removed"; fail=1; }
ls "$S/packs" | grep -q "^fa-1\.v1\.zip" || { echo "FAIL: old fa-1 was lost"; fail=1; }
ls "$S/packs" | grep -q "^core\.v9\.zip" && { echo "FAIL: hollow core pack was installed"; fail=1; }
cmp -s "$S/garden-before.bin" "$S/packs/garden-1.v1.zip" || { echo "FAIL: installed pack was written over"; fail=1; }
grep -q '"en-1-01-a":3' "$S/data/progress.json" || { echo "FAIL: progress lost"; fail=1; }
[ $fail = 0 ] && echo "update ok"
exit $fail
