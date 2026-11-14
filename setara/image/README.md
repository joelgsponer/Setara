# SD card

`make_card.py` assembles the folder that goes onto every card: the app, every
built pack, and the launchers. See [docs/device.md](../docs/device.md).

```sh
python3 image/make_card.py            # writes dist/card/setara/
```

It does not build a full firmware image. Which firmware to put under the app
on each device is the first open point of phase 0; once that is settled, the
image script belongs here.
