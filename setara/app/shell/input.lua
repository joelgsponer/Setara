-- Button names used everywhere in the app (spec section 5, "Controls").
-- Engines never read raw keys or gamepad buttons; the shell maps both the
-- handheld's buttons and a PC keyboard to these names.
return {
  buttons = {
    "up", "down", "left", "right", -- move, or answer directly (four choices)
    "a",      -- yes, choose, continue
    "b",      -- back one step, never loses progress
    "x",      -- say it again, slowly
    "y",      -- explain in Dari
    "l", "r", -- player 1 / player 2 buzzers; hold both 2 s on home = teacher mode
    "start",  -- pause: volume, brightness, hand over
  },
  -- PC keyboard mapping for authoring and testing. Gamepad mapping: TODO
  -- once the firmware for each device is chosen (phase 0).
  keyboard = {
    up = "up", down = "down", left = "left", right = "right",
    z = "a", x = "b", a = "x", s = "y", q = "l", w = "r", ["return"] = "start",
  },
}
