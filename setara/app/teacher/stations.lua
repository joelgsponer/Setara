-- Station Timer: splits a mixed class into three groups and rotates them:
-- with the teacher, on the handhelds, writing. Makes multi-level classes and
-- few devices workable.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local T = require("teacher.common")
local g = love.graphics

local Stations = {}
Stations.__index = Stations

local KEYS = { "st_teacher", "st_device", "st_writing" }
local GROUP = { "E07A3F", "3F7FBF", "4E9A51" }

function Stations.new()
  return setmetatable({ t = 0, minutes = 10, left = 0, turn = 0, running = false }, Stations)
end

function Stations:leave() T.stop() end

function Stations:update(dt)
  self.t = self.t + dt
  if not self.running then return end
  self.left = self.left - dt
  if self.left <= 0 then
    self.turn = self.turn + 1
    sfx.play("chime")
    if self.turn >= 3 then
      self.running, self.finished = false, true
      audio.say(T.S("st_done").audio)
    else
      self.left = self.minutes * 60
      audio.say(T.S("st_swap").audio)
    end
  end
end

function Stations:input(b)
  if b == "b" then app.pop()
  elseif b == "a" then
    if self.finished or (not self.running and self.left <= 0) then
      self.finished, self.turn, self.left, self.running = false, 0, self.minutes * 60, true
      sfx.play("chime")
    else
      self.running = not self.running
    end
  elseif not self.running and self.left <= 0 then
    if b == "left" or b == "down" then self.minutes = math.max(3, self.minutes - 1) sfx.play("move")
    elseif b == "right" or b == "up" then self.minutes = math.min(20, self.minutes + 1) sfx.play("move") end
  end
end

local function group_mark(i, cx, cy, r)
  local c = GROUP[i]
  g.setColor(tonumber(c:sub(1, 2), 16) / 255, tonumber(c:sub(3, 4), 16) / 255, tonumber(c:sub(5, 6), 16) / 255)
  if i == 1 then g.circle("fill", cx, cy, r)
  elseif i == 2 then g.rectangle("fill", cx - r, cy - r, r * 2, r * 2, 4, 4)
  else g.polygon("fill", cx, cy - r, cx + r, cy + r, cx - r, cy + r) end
end

function Stations:draw()
  T.header("tool_stations")
  -- three stations; each group is a shape and a colour, so no reading is needed
  for s = 1, 3 do
    local x = 14 + (s - 1) * 206
    ui.card(x, 56, 200, 190, { fill = ui.c.paper })
    ui.set(ui.c.ink)
    local str = T.S(KEYS[s])
    if str.fa and str.fa[1] then text.centered("fabold", str.fa[1], x + 4, 60, 192, 44, 24) end
    local group = (s - 1 - self.turn) % 3 + 1
    group_mark(group, x + 100, 160, 44)
  end
  -- the clock
  local show = (self.running or self.left > 0) and self.left or self.minutes * 60
  ui.card(170, 262, 300, 110, { fill = self.running and ui.c.shade or ui.c.paper, border = ui.c.teacher, width = 4 })
  ui.set(ui.c.teacher)
  text.centered("bold", T.timer(math.max(0, show)), 170, 262, 300, 110, 72)
  if not self.running and self.left <= 0 then
    ui.arrow("left", 150, 317, 10, ui.c.ink)
    ui.arrow("right", 490, 317, 10, ui.c.ink)
  end
  for i = 1, 3 do
    ui.set(i <= self.turn and ui.c.teacher or ui.c.line)
    g.circle("fill", 296 + (i - 1) * 24, 392, 7)
  end
  T.hints({ { "a", self.running and "hint_stop" or "hint_start" } })
end

return Stations
