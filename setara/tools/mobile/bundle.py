"""Phone builds: one .love file that holds the app and a starter set of packs,
and a "store" folder of every pack as a download, with the list of them (the
catalogue) baked into the app.

Phone packs are lighter than card packs: no slow speech variants, and the
teacher's guides without speech (a teacher with a phone reads the page).
The manifest of a lighter pack lists only the files it still has, so it
verifies like any other pack.
"""

import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# What a phone gets inside the app: enough to start in every subject.
STARTER = ["en-1", "fa-1", "math-1", "garden-1", "teacher-en-1"]


def lighter_pack(path: Path) -> tuple[dict, dict[str, bytes]]:
    """A card pack as (manifest, files) for a phone."""
    with zipfile.ZipFile(path) as src:
        manifest = json.loads(src.read("manifest.json"))
        guide = manifest.get("kind") == "guide"
        files = {}
        for name in src.namelist():
            if name == "manifest.json" or name.endswith(".slow.ogg") or (guide and name.endswith(".ogg")):
                continue
            files[name] = src.read(name)
    manifest["files"] = {k: v for k, v in manifest["files"].items() if k in files}
    return manifest, files


def pack_zip(manifest: dict, files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        stamp = (2026, 1, 1, 0, 0, 0)   # the same bytes every time, so the hash is stable
        z.writestr(zipfile.ZipInfo("manifest.json", stamp), json.dumps(manifest, ensure_ascii=False, sort_keys=True),
                   zipfile.ZIP_DEFLATED)
        for name in sorted(files):
            kind = zipfile.ZIP_DEFLATED if name.endswith(".json") else zipfile.ZIP_STORED
            z.writestr(zipfile.ZipInfo(name, stamp), files[name], kind)
    return buf.getvalue()


def write_store(store: Path, base_url: str) -> dict:
    """Every pack as a download in `store`, named by its hash (a file name on
    the wire says nothing about its content). Returns the catalogue."""
    store.mkdir(parents=True, exist_ok=True)
    for old in store.glob("*.zip"):
        old.unlink()
    entries = []
    for path in sorted((ROOT / "packs").glob("*.zip")):
        if path.stem == "core":
            continue
        manifest, files = lighter_pack(path)
        data = pack_zip(manifest, files)
        digest = hashlib.sha256(data).hexdigest()
        (store / f"{digest[:20]}.zip").write_bytes(data)
        entries.append({
            "pack": manifest["pack"], "version": manifest["version"], "kind": manifest.get("kind", "learner"),
            "subject": manifest.get("subject"), "level": manifest.get("level"), "optional": bool(manifest.get("optional")),
            "title_en": manifest.get("title_en", ""), "title_fa": manifest.get("title_fa", []),
            "size": len(data), "sha256": digest, "file": f"{digest[:20]}.zip",
        })
    catalogue = {"base": base_url.rstrip("/") + "/", "packs": entries}
    (store / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False), "utf-8")
    return catalogue


def write_love(target: Path, only: list[str] | None = None, english: bool = False, catalogue: dict | None = None) -> list[str]:
    """Write the .love; returns the ids of the packs put in."""
    packs = sorted((ROOT / "packs").glob("*.zip"))
    if not any(p.stem == "core" for p in packs):
        raise SystemExit("no core pack in packs/: run the builder first")
    inside = []
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w") as z:
        for path in sorted((ROOT / "app").rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                z.write(path, path.relative_to(ROOT / "app").as_posix(), zipfile.ZIP_DEFLATED)
        if english:
            z.writestr("english", "")
        if catalogue:
            z.writestr("catalogue.json", json.dumps(catalogue, ensure_ascii=False), zipfile.ZIP_DEFLATED)
        for pack in packs:
            if only is not None and pack.stem not in only and pack.stem != "core":
                continue
            inside.append(pack.stem)
            manifest, files = lighter_pack(pack)
            z.writestr(f"webpacks/{pack.stem}/manifest.json", json.dumps(manifest, ensure_ascii=False), zipfile.ZIP_DEFLATED)
            for name, data in files.items():
                kind = zipfile.ZIP_DEFLATED if name.endswith(".json") else zipfile.ZIP_STORED
                z.writestr(zipfile.ZipInfo(f"webpacks/{pack.stem}/{name}"), data, kind)
    return inside
