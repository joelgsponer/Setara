#!/usr/bin/env python3
"""Build the Android app: the official LÖVE for Android package with Setara
and a choice of packs inside, under Setara's own name.

  python3 tools/mobile/make_apk.py [--all | --only <pack> ...] [--english]
                                   [--keystore my.jks --alias setara --storepass ...]

Needs Java and three downloads, looked for in $SETARA_ANDROID (default
/opt/tools/android): love-embed.apk (love-11.5-android-embed.apk from the
love-android releases), apktool.jar, and Android build-tools (zipalign,
apksigner). See docs/mobile.md.

Without a keystore the app is signed with a throw-away test key: it installs
by hand on any phone, but it cannot go into a store and cannot be updated by
an app signed with another key. Use your own key for anything you hand out.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bundle import ROOT, STARTER, write_love   # noqa: E402

TOOLS = Path(os.environ.get("SETARA_ANDROID", "/opt/tools/android"))
PACKAGE = "org.setara.app"
# The app never opens a connection and never listens: these are taken out.
DROP = ["INTERNET", "BLUETOOTH", "RECORD_AUDIO", "VIBRATE", "WRITE_EXTERNAL_STORAGE"]


def run(*cmd: str) -> None:
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"{' '.join(cmd[:4])} ... failed:\n{done.stdout[-1500:]}\n{done.stderr[-1500:]}")


def find(name: str) -> str:
    for hit in sorted(TOOLS.rglob(name)):
        if hit.is_file():
            return str(hit)
    raise SystemExit(f"{name} not found under {TOOLS}: see docs/mobile.md")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "android")
    ap.add_argument("--all", action="store_true", help="every pack (over a gigabyte)")
    ap.add_argument("--only", action="append", help="these packs instead of the starter set")
    ap.add_argument("--slow", action="store_true", help="include the slow speech variants (much larger)")
    ap.add_argument("--english", action="store_true", help="start in English mode (for testers)")
    ap.add_argument("--keystore", type=Path)
    ap.add_argument("--alias", default="setara")
    ap.add_argument("--storepass", default=os.environ.get("SETARA_STOREPASS", ""))
    args = ap.parse_args()

    version = (ROOT / "app" / "version.lua").read_text().split('"')[1]
    work = args.out / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    run("java", "-jar", find("apktool.jar"), "d", "-f", "-o", str(work / "apk"), find("love-embed.apk"))
    apk = work / "apk"

    # the game
    only = None if args.all else (args.only or STARTER)
    inside = write_love(apk / "assets" / "game.love", only, args.slow, args.english)

    # the manifest: Setara's name, no network, lying or standing
    path = apk / "AndroidManifest.xml"
    m = path.read_text("utf-8")
    for perm in DROP:
        m = re.sub(rf'\s*<uses-permission[^>]*android\.permission\.{perm}"[^>]*/>', "", m)
    m = m.replace('android:usesCleartextTraffic="true"', 'android:usesCleartextTraffic="false"')
    m = m.replace("LÖVE for Android", "Setara")
    m = m.replace('android:screenOrientation="landscape"', 'android:screenOrientation="fullUser"')
    m = m.replace('android:allowBackup="true"', 'android:allowBackup="false"')
    # names that must be the app's own, so that it installs beside other LÖVE apps
    m = m.replace("org.love2d.android.DYNAMIC_RECEIVER", f"{PACKAGE}.DYNAMIC_RECEIVER")
    m = m.replace("org.love2d.android.androidx-startup", f"{PACKAGE}.androidx-startup")
    m = m.replace('<category android:name="tv.ouya.intent.category.GAME"/>', "")
    path.write_text(m, "utf-8")

    yml = (apk / "apktool.yml").read_text("utf-8")
    yml = yml.replace("renameManifestPackage: null", f"renameManifestPackage: {PACKAGE}")
    code = sum(int(n) * k for n, k in zip(version.split("."), (10000, 100, 1)))
    yml = re.sub(r"versionCode: \S+", f"versionCode: {code}", yml)
    yml = re.sub(r"versionName: \S+", f"versionName: {version}", yml)
    yml = yml.replace("doNotCompress:\n", "doNotCompress:\n- love\n", 1)   # the game is stored, not squeezed again
    (apk / "apktool.yml").write_text(yml, "utf-8")

    # the icon
    import cairosvg
    svg = (Path(__file__).parent / "icon.svg").read_bytes()
    for folder, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
        target = apk / "res" / f"drawable-{folder}" / "love.png"
        if target.exists():
            cairosvg.svg2png(bytestring=svg, write_to=str(target), output_width=size, output_height=size)

    unsigned, aligned = work / "unsigned.apk", work / "aligned.apk"
    run("java", "-jar", find("apktool.jar"), "b", "-o", str(unsigned), str(apk))
    run(find("zipalign"), "-f", "-p", "4", str(unsigned), str(aligned))

    keystore, storepass, test_key = args.keystore, args.storepass, False
    if not keystore:
        test_key = True
        keystore, storepass = args.out / "test-key.jks", "setara-test"
        if not keystore.exists():
            run("keytool", "-genkeypair", "-keystore", str(keystore), "-storepass", storepass, "-alias", args.alias,
                "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000", "-dname", "CN=Setara test key")
    name = "setara-" + version + ("" if args.all else "-starter" if not args.only else "-custom") + ".apk"
    final = args.out / name
    run(find("apksigner"), "sign", "--ks", str(keystore), "--ks-pass", f"pass:{storepass}", "--ks-key-alias", args.alias,
        "--out", str(final), str(aligned))
    run(find("apksigner"), "verify", str(final))
    shutil.rmtree(work, ignore_errors=True)
    print(f"{final}  ({final.stat().st_size / 1e6:.0f} MB, {len(inside) - 1} packs"
          + (", signed with the TEST key" if test_key else "") + ")")


if __name__ == "__main__":
    main()
