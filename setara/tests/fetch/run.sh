#!/bin/sh
# Tests fetching a pack on a phone build: a good pack is fetched, checked and
# installed; a pack that was changed on the way is thrown away; a server that
# is not there leaves the app as it was. Needs built packs.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$(mktemp -d)"
PORT=$((20000 + $$ % 20000))
python3 - "$ROOT" "$WORK" "$PORT" <<'PY'
import json, shutil, sys
from pathlib import Path
root, work, port = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(root / "tools" / "mobile"))
import bundle, hashlib
store = work / "store"; store.mkdir()
entries = []
for pid in ("teacher-en-1", "garden-4-rights"):
    manifest, files = bundle.lighter_pack(root / "packs" / f"{pid}.zip")
    data = bundle.pack_zip(manifest, files)
    digest = hashlib.sha256(data).hexdigest()
    if pid == "garden-4-rights":                      # changed on the way: one byte flipped
        data = data[:-200] + bytes([data[-200] ^ 1]) + data[-199:]
    (store / f"{digest[:20]}.zip").write_bytes(data)
    entries.append({"pack": pid, "version": manifest["version"], "kind": manifest.get("kind", "learner"),
                    "subject": manifest.get("subject"), "level": manifest.get("level"), "optional": bool(manifest.get("optional")),
                    "title_en": manifest.get("title_en", ""), "title_fa": manifest.get("title_fa", []),
                    "size": len(data), "sha256": digest, "file": f"{digest[:20]}.zip"})
entries.append(dict(entries[0], pack="en-9", file="nothere.zip"))
shutil.copytree(root / "app", work / "app")
(work / "app" / "catalogue.json").write_text(json.dumps({"base": f"http://127.0.0.1:{port}/", "packs": entries}))
save = work / "save" / "love" / "setara" / "packs"; save.mkdir(parents=True)
src = root / "dist" / "card" / "setara" / "data" / "love" / "setara" / "packs"
for name in ("core", "en-1"):
    for f in src.glob(f"{name}.v*.zip"):
        shutil.copy(f, save / f.name)
PY
(cd "$WORK/store" && python3 -m http.server "$PORT" >/dev/null 2>&1) &
SERVER=$!
sleep 1
cat > "$WORK/check.lua" <<'LUA'
local t = ...
t.wait(4) t.skip_tutorial()
local packs, fetch = require("core.packs"), require("core.fetch")
local function get(id)
  local entry
  for _, e in ipairs(fetch.catalogue.packs) do if e.pack == id then entry = e end end
  assert(fetch.start(entry), "could not start")
  local result
  for _ = 1, 600 do
    t.wait(0.1)
    result = fetch.update()
    if result then break end
  end
  if result == "done" then packs.install_updates() packs.load() end
  return result
end
print("GOOD=" .. tostring(get("teacher-en-1")) .. " installed=" .. tostring(packs.list["teacher-en-1"] ~= nil))
print("CHANGED=" .. tostring(get("garden-4-rights")) .. " installed=" .. tostring(packs.list["garden-4-rights"] ~= nil))
print("MISSING=" .. tostring(get("en-9")) .. " installed=" .. tostring(packs.list["en-9"] ~= nil))
print("LEFT_IN_UPDATE=" .. #love.filesystem.getDirectoryItems("update"))
print("STILL=" .. tostring(packs.list["en-1"] ~= nil and packs.core ~= nil))
LUA
LOVE="${SETARA_LOVE:-/opt/tools/squashfs-root/AppRun}"
out="$(XDG_DATA_HOME="$WORK/save" SETARA_SCRIPT="$WORK/check.lua" SETARA_SPEED=1 SETARA_SEED=7 ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a "$LOVE" "$WORK/app" 2>&1)"
kill $SERVER 2>/dev/null
echo "$out" | grep -E "^[A-Z_]+="
fail=0
echo "$out" | grep -q "GOOD=done installed=true" || { echo "FAIL: good pack not fetched and installed"; fail=1; }
echo "$out" | grep -q "CHANGED=failed installed=false" || { echo "FAIL: a changed pack was not thrown away"; fail=1; }
echo "$out" | grep -q "MISSING=failed installed=false" || { echo "FAIL: a missing file was not reported"; fail=1; }
echo "$out" | grep -q "LEFT_IN_UPDATE=0" || { echo "FAIL: files left in update/"; fail=1; }
echo "$out" | grep -q "STILL=true" || { echo "FAIL: installed packs were harmed"; fail=1; }
rm -rf "$WORK"
[ $fail = 0 ] && echo "fetch ok"
exit $fail
