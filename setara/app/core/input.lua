-- Button names used everywhere in the app (spec section 5, "Controls").
-- Engines never read raw keys or gamepad buttons: this module maps the
-- handheld's buttons and a PC keyboard to the same eleven names.
local M = {}

M.buttons = { "up", "down", "left", "right", "a", "b", "x", "y", "l", "r", "start" }

-- PC keyboard, for authoring and testing.
M.keyboard = {
  up = "up", down = "down", left = "left", right = "right",
  z = "a", x = "b", a = "x", s = "y", q = "l", w = "r",
  ["return"] = "start", space = "a", backspace = "b",
}

-- Handhelds follow the Nintendo layout: A is the right face button, B the
-- bottom one, X the top one, Y the left one. SDL names buttons by position
-- on an Xbox pad, so SDL "a" (bottom) is the handheld's B, and so on.
M.gamepad = {
  dpup = "up", dpdown = "down", dpleft = "left", dpright = "right",
  a = "b", b = "a", x = "y", y = "x",
  leftshoulder = "l", rightshoulder = "r", start = "start",
}

-- Fallback for pads SDL has no mapping for (raw joystick button numbers of
-- the common Anbernic and R36S firmwares). Overridden by data/buttons.json.
M.joystick = { [1] = "a", [2] = "b", [3] = "y", [4] = "x", [5] = "l", [6] = "r", [10] = "start", [8] = "start" }

-- Raw events learned on the calibration screen: "j3" (joystick button 3),
-- "gdpup" (gamepad button), "hu" (hat up) -> button name. Saved on the card
-- as data/buttons.json, so an unknown pad needs calibrating only once.
M.custom = nil
M.raw = nil        -- function(code) set while calibrating; swallows the event

M.down = {}        -- button -> seconds held
M.listener = nil   -- function(button) set by main

local function press(b)
  if not b then return end
  if not M.down[b] then M.down[b] = 0 end
  if M.listener then M.listener(b) end
end

local function release(b)
  if b then M.down[b] = nil end
end

-- Raw code -> button name, through the learned map when there is one.
-- A code the map does not know falls back to the built-in mapping, so a card
-- calibrated on one device still works in another.
local function lookup(code, fallback)
  return M.custom and M.custom[code] or fallback
end

-- A learned map counts only when it names all eleven buttons.
function M.complete(map)
  if type(map) ~= "table" then return false end
  local have = {}
  for _, name in pairs(map) do have[name] = true end
  for _, name in ipairs(M.buttons) do
    if not have[name] then return false end
  end
  return true
end

function M.keypressed(key) press(M.keyboard[key]) end
function M.keyreleased(key) release(M.keyboard[key]) end

function M.gamepadpressed(_, button)
  if M.raw then return M.raw("g" .. button) end
  press(lookup("g" .. button, M.gamepad[button]))
end

function M.gamepadreleased(_, button) release(lookup("g" .. button, M.gamepad[button])) end

function M.joystickpressed(joy, button)
  if joy:isGamepad() then return end
  if M.raw then return M.raw("j" .. button) end
  press(lookup("j" .. button, M.joystick[button]))
end

function M.joystickreleased(joy, button)
  if joy:isGamepad() then return end
  release(lookup("j" .. button, M.joystick[button]))
end

local hat_dirs = { u = "up", d = "down", l = "left", r = "right" }
local hat_state = {}

function M.joystickhat(joy, _, dir)
  if joy:isGamepad() then return end
  if M.raw then
    if dir ~= "c" and #dir == 1 then M.raw("h" .. dir) end
    return
  end
  local now = {}
  for c in dir:gmatch(".") do
    local b = lookup("h" .. c, hat_dirs[c])
    if b then now[b] = true end
  end
  for b in pairs(now) do
    if not hat_state[b] then press(b) end
  end
  for b in pairs(hat_state) do
    if not now[b] then release(b) end
  end
  hat_state = now
end

-- An analogue stick works as a D-pad too.
local axis_state = {}
function M.axis(joy)
  local x, y = joy:getAxis(1) or 0, joy:getAxis(2) or 0
  local now = { left = x < -0.6, right = x > 0.6, up = y < -0.6, down = y > 0.6 }
  for dir, on in pairs(now) do
    if on and not axis_state[dir] then
      if M.raw then M.raw("x" .. dir) else press(lookup("x" .. dir, dir)) end
    end
    if not on and axis_state[dir] and not M.raw then release(lookup("x" .. dir, dir)) end
    axis_state[dir] = on
  end
end

function M.update(dt)
  for b, t in pairs(M.down) do M.down[b] = t + dt end
  for _, joy in ipairs(love.joystick.getJoysticks()) do
    if joy:getAxisCount() >= 2 then M.axis(joy) break end
  end
end

-- Seconds both buttons have been held together, or 0.
function M.held(a, b)
  local ta, tb = M.down[a], M.down[b]
  if ta and tb then return math.min(ta, tb) end
  return 0
end

-- True when a pad is plugged in that SDL does not know: it needs calibrating.
function M.unknown_pad()
  for _, joy in ipairs(love.joystick.getJoysticks()) do
    if not joy:isGamepad() then return true end
  end
  return false
end

-- Test scripts press buttons through here.
function M.fake(b, hold)
  press(b)
  if not hold then M.down[b] = nil end
end

function M.fake_release(b) release(b) end

return M
