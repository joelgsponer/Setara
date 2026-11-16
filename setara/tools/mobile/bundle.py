"""One .love file that holds the app and a choice of packs, unpacked, for
places where packs cannot sit beside the app as files: the phone apps.
(The browser build does the same in tools/web/make_web.py.)"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# What a phone gets when nothing else is asked for: enough to start in every
# subject, small enough to install anywhere.
STARTER = ["en-1", "en-1-letters", "fa-1", "fa-1-alphabet", "math-1", "garden-1", "teacher-en-1",
           "guide-en-1", "guide-fa-1", "guide-math-1", "guide-garden-1"]


def write_love(target: Path, only: list[str] | None = None, slow: bool = False, english: bool = False) -> list[str]:
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
        for pack in packs:
            if only is not None and pack.stem not in only and pack.stem != "core":
                continue
            inside.append(pack.stem)
            with zipfile.ZipFile(pack) as src:
                for name in src.namelist():
                    if name.endswith(".slow.ogg") and not slow:
                        continue
                    kind = zipfile.ZIP_DEFLATED if name.endswith(".json") else zipfile.ZIP_STORED
                    z.writestr(zipfile.ZipInfo(f"webpacks/{pack.stem}/{name}"), src.read(name), kind)
    return inside
