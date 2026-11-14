-- First run: a spoken, one-minute tour of the buttons, learned by pressing
-- them. No text. Start skips it.
local ui = require("core.ui")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local g = love.graphics

local Tutorial = {}
Tutorial.__index = Tutorial

local STEPS = {
  { say = "tut_hello" },
  { say = "tut_up", want = "up" },
  { say = "tut_down", want = "down" },
  { say = "tut_left", want = "left" },
  { say = "tut_right", want = "right" },
  { say = "tut_a", want = "a" },
  { say = "tut_b", want = "b" },
  { say = "tut_x", want = "x" },
  { say = "tut_y", want = "y" },
  { say = "tut_done" },
}

function Tutorial.new()
  return setmetatable({ t = 0, step = 0, happy = 0 }, Tutorial)
end

function Tutorial:enter() self:next() end

function Tutorial:next()
  self.step = self.step + 1
  local step = STEPS[self.step]
  if not step then
    store.progress.tutorial_done = true
    store.save_progress()
    app.pop()
    return
  end
  self.said = 0
  audio.say(packs.string(step.say).audio, {
    on_done = function() if not step.want then self:next() end end,
    after = 0.4,
  })
end

function Tutorial:update(dt)
  self.t = self.t + dt
  self.happy = math.max(0, self.happy - dt)
  local step = STEPS[self.step]
  if step and step.want and not audio.busy() then
    -- nothing pressed for a while: say it again
    self.said = self.said + dt
    if self.said > 6 then
      self.said = 0
      audio.say(packs.string(step.say).audio)
    end
  end
end

function Tutorial:input(b)
  if b == "start" then
    audio.stop()
    self.step = #STEPS
    self:next()
    return
  end
  local step = STEPS[self.step]
  if step and step.want then
    if b == step.want then
      sfx.play("right")
      self.happy = 0.7
      self:next()
    else
      sfx.play("wrong")
    end
  end
end

-- The handheld itself, with the wanted button lit.
function Tutorial.device(want, t)
  local lit = math.floor(t * 3) % 2 == 0
  ui.card(90, 210, 460, 220, { fill = ui.c.shade, radius = 34 })
  ui.card(220, 232, 200, 150, { fill = ui.c.sky, radius = 8 })
  local dx, dy = 155, 310
  local dirs = { up = { 0, -34 }, down = { 0, 34 }, left = { -34, 0 }, right = { 34, 0 } }
  ui.set(ui.c.ink)
  g.rectangle("fill", dx - 16, dy - 50, 32, 100, 6, 6)
  g.rectangle("fill", dx - 50, dy - 16, 100, 32, 6, 6)
  for dir, o in pairs(dirs) do
    local on = want == dir and lit
    ui.arrow(dir, dx + o[1], dy + o[2], on and 13 or 9, on and ui.c.gold or ui.c.soft)
  end
  local bx, by = 485, 310
  local face = { x = { 0, -32 }, b = { 0, 32 }, y = { -32, 0 }, a = { 32, 0 } }
  for name, o in pairs(face) do
    local on = want == name and lit
    if on then
      ui.set(ui.c.gold)
      g.circle("fill", bx + o[1], by + o[2], 22)
    end
    ui.badge(name, bx + o[1], by + o[2], 15)
  end
end

function Tutorial:draw()
  ui.background(ui.c.sky)
  local step = STEPS[self.step] or {}
  local mood = self.happy > 0 and "happy" or (audio.busy() and "talk" or "idle")
  ui.guide(320, 110, 2.2, mood, self.t)
  Tutorial.device(step.want, self.t)
  ui.progress(self.step - 1, #STEPS, 120, 20, 400)
end

return Tutorial
