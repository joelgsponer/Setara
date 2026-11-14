-- Button calibration for pads the system does not know. The screen lights one
-- button after another on a picture of the device; whatever is pressed is
-- remembered for it. The result is saved as data/buttons.json on the card.
-- Opens by itself for an unknown pad, or when a file named "calibrate" is
-- put next to the packs. Enter on a keyboard leaves without saving.
local ui = require("core.ui")
local sfx = require("core.sfx")
local input = require("core.input")
local json = require("core.json")
local Tutorial = require("scenes.tutorial")

local Calibrate = {}
Calibrate.__index = Calibrate

local ORDER = { "up", "down", "left", "right", "a", "b", "x", "y", "l", "r", "start" }

function Calibrate.new()
  return setmetatable({ t = 0, i = 1, map = {}, used = {}, idle = 0 }, Calibrate)
end

function Calibrate:enter()
  input.raw = function(code)
    if self.used[code] then return end
    self.used[code] = true
    self.map[code] = ORDER[self.i]
    self.i = self.i + 1
    self.idle = 0
    sfx.play("right")
    if self.i > #ORDER then self:finish(true) end
  end
end

function Calibrate:finish(save)
  input.raw = nil
  if save then
    input.custom = self.map
    love.filesystem.createDirectory("data")
    love.filesystem.write("data/buttons.json", json.encode(self.map))
  end
  -- Do not open by itself again; a "calibrate" file still asks for it.
  local store = require("core.store")
  store.progress.calibration_seen = true
  store.save_progress()
  love.filesystem.remove("calibrate")
  love.filesystem.remove("calibrate.txt")
  app.pop()
end

function Calibrate:leave() input.raw = nil end

-- A pad with a dead or missing button must not hold the device on this
-- screen: twenty seconds without a new press and it closes, saving nothing.
local GIVE_UP = 20

function Calibrate:update(dt)
  self.t = self.t + dt
  self.idle = self.idle + dt
  if self.idle > GIVE_UP then self:finish(false) end
end

-- Keyboard presses arrive here as ordinary buttons: only "start" matters.
function Calibrate:input(b)
  if b == "start" then self:finish(false) end
end

function Calibrate:draw()
  ui.background(ui.c.shade)
  local want = ORDER[self.i]
  ui.guide(320, 110, 2.2, "think", self.t)
  Tutorial.device(want, self.t)
  -- the shoulder buttons and Start are not on the picture's face: show them above it
  local lit = math.floor(self.t * 3) % 2 == 0
  for k, name in ipairs({ "l", "start", "r" }) do
    local x = ({ 130, 320, 510 })[k]
    if want == name and lit then
      ui.set(ui.c.gold)
      love.graphics.circle("fill", x, 196, 22)
    end
    ui.badge(name, x, 196, 15)
  end
  ui.progress(self.i - 1, #ORDER, 120, 20, 400)
end

return Calibrate
