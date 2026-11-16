# Phones and tablets

Setara is built for a handheld with buttons, but the same app runs on a
phone or tablet, so that a teacher, a parent or a tester can use it without
the device. Nothing changes in what it is: no account, no network, the same
packs.

**None of this has been run on a real phone yet.** The Android package is
built and its contents checked; the single game file inside it runs under
LÖVE on a PC with touches; nobody has installed it.

## How it is used on glass

On a touch screen the app draws its eleven buttons itself (`app/core/touch.lua`):
beside the picture when the phone lies, under it when it stands. Several
fingers work at once, so L and R held together open teacher mode. The
system's Back key is B. On a PC, `SETARA_TOUCH=844x390 love app` shows what
a phone shows.

Not done: tapping a picture directly. Answers are still given with the
on-screen D-pad, as on the device.

## Android

```sh
python3 tools/mobile/make_apk.py            # the starter set, about 240 MB
python3 tools/mobile/make_apk.py --all      # every pack, over a gigabyte
python3 tools/mobile/make_apk.py --only en-1 --only math-1 --english
```

The result is `dist/android/setara-<version>-starter.apk`. It is the
official *LÖVE for Android* package (11.5) with Setara inside, renamed to
`org.setara.app`. The permissions for network, microphone, Bluetooth and
vibration are taken out: the app cannot open a connection.

What the script needs (in `/opt/tools/android`, or where `SETARA_ANDROID`
points): Java; `love-embed.apk` (`love-11.5-android-embed.apk` from the
love-android releases on GitHub); `apktool.jar` (Apktool 2.9); the Android
build-tools (for `zipalign` and `apksigner`).

**Installing by hand:** copy the APK to the phone, open it, allow "install
unknown apps" for the file manager. Works on Android 5 and later, on 32 and
64 bit ARM phones.

**Signing.** Without `--keystore` the app is signed with a throw-away test
key made on the spot. That is fine for trying it. For anything handed out,
make one key, keep it safe for good, and always sign with it; an app can
only be updated by a package signed with the same key:

```sh
keytool -genkeypair -keystore setara.jks -alias setara -keyalg RSA -keysize 2048 -validity 10000
python3 tools/mobile/make_apk.py --keystore setara.jks --storepass '…'
```

**Google Play** needs more than this script gives: a developer account
(one-time fee), an App Bundle instead of an APK, a current target API
level, a privacy policy page, and content in asset packs once the app is
over 200 MB. The honest route to the store is the Gradle project of
love-android with Setara's `game.love`; sideloading and sharing the APK
file need none of that.

**Which packs.** The starter set is level 1 of every subject, both
alphabets, the first lesson book and four guides. With `--all` the package
is over a gigabyte; phones install it, but it is a heavy file to pass
around. Adding packs to an installed app, as the handheld does from its
card, is not built for phones.

## iPhone and iPad

An iOS app can only be built on a Mac with Xcode, and installed on other
people's devices only through an Apple Developer account (yearly fee),
either TestFlight or the App Store. It cannot be built on Linux, so this
repository only prepares for it:

```sh
python3 tools/mobile/make_love.py           # dist/mobile/setara.love
```

Then, on a Mac:

1. Download the LÖVE 11.5 source and `love-11.5-apple-libraries.zip`
   (love2d.org), and put the libraries into the source tree as LÖVE's
   README says.
2. Open `platform/xcode/love.xcodeproj`, choose the target `love-ios`.
3. Add `setara.love` to the target's "Copy Bundle Resources". LÖVE then
   starts it directly.
4. Set the bundle identifier (`org.setara.app`), the display name
   (Setara), the icons (from `tools/mobile/icon.svg`) and your team.
5. In `Info.plist` allow all orientations; no usage descriptions are
   needed, since the app uses no camera, microphone, location or network.
6. Run it on a device; then Archive and upload for TestFlight.

App Store review asks for a privacy statement ("no data collected" is the
true answer) and may ask about content for children; the app has no
links, no purchases and no accounts.

## The browser as an app

The browser build (`tools/web/make_web.py`, see `hosting.md`) is also an
installable web app: on an iPhone, open the page in Safari, Share, "Add to
Home Screen"; on Android, the browser's "Install app". It then opens full
screen from its own icon and, once it has loaded completely one time, should
work without a connection. This is the only way onto an iPhone without a Mac
and a developer account. Whether iOS keeps a download of this size for
offline use has not been tried.

## What to check on the first real phone

- That the app starts at all with the pack file inside the package.
- Start-up time and memory with the starter set and with `--all`.
- That the buttons are large enough for an adult thumb and a child's, and
  that the picture is not too small on a standing phone.
- Sound: that speech starts without delay and stops when the app goes to
  the background.
- That progress survives closing the app and an update.
