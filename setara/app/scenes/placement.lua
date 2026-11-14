-- "Find my level": a two-minute game that walks up the levels with a few
-- questions each and suggests where to start. Nothing is stored about the
-- child; only the suggested level is remembered for the device.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local engines = require("engines")
local Quiz = require("core.quiz")

local Placement = {}
Placement.__index = Placement

local PER_LEVEL = 4
local PASS = 3

function Placement.new(subject)
  local self = setmetatable({ subject = subject, t = 0 }, Placement)
  self.levels = packs.levels(subject)
  self.index = 0
  return self
end

function Placement:enter()
  audio.say(packs.string("find_level_intro").audio)
  self.waiting = true
end

function Placement:leave()
  audio.stop()
  ui.clear_images()
end

function Placement:next_level()
  self.index = self.index + 1
  local level = self.levels[self.index]
  if not level then return self:finish(self.levels[#self.levels]) end
  local pack = packs.subjects[self.subject][level]
  local pool = {}
  for _, entry in ipairs(packs.review(pack)) do
    if #(entry.choices or {}) >= 3 then pool[#pool + 1] = entry end
  end
  if #pool < PER_LEVEL then return self:finish(level) end
  Quiz.shuffle(pool)
  local items, seen = {}, {}
  for _, entry in ipairs(pool) do
    if entry.answer ~= nil and not seen[entry.answer] and #items < PER_LEVEL then
      seen[entry.answer] = true
      items[#items + 1] = entry
    end
  end
  local ctx = { root = pack.root, pack = pack, top = 40, player = 1, next_player = function() end }
  ctx.say = function(clips, opts) audio.say(packs.clips(pack, clips), opts) end
  self.level = level
  self.engine = engines.get("listen_pick").new({ items = items }, ctx)
  self.engine.quiz.level = 4
  self.engine:start()
end

function Placement:finish(level)
  self.engine = nil
  self.result = level
  store.progress.level[self.subject] = level
  store.save_progress()
  sfx.play("done")
  local clips = {}
  for _, key in ipairs({ "find_level_done", "level_" .. level }) do
    for _, c in ipairs(packs.string(key).audio or {}) do clips[#clips + 1] = c end
  end
  audio.say(clips)
end

function Placement:update(dt)
  self.t = self.t + dt
  if self.waiting and not audio.busy() then
    self.waiting = false
    self:next_level()
  end
  local e = self.engine
  if e then
    e:update(dt)
    if e.finished then
      if e.quiz.first_right >= PASS then self:next_level() else self:finish(self.level) end
    end
  end
end

function Placement:input(b)
  if self.result then
    if b == "a" or b == "b" then app.pop() end
  elseif b == "b" then
    app.pop()
  elseif self.engine then
    if b == "x" then self.engine:again(true)
    elseif b == "y" then self.engine:help()
    else self.engine:input(b) end
  end
end

function Placement:draw()
  local color = ui.c[self.subject]
  ui.background(ui.mix(ui.c.bg, color, 0.12))
  if self.result then
    ui.guide(320, 130, 2.2, "happy", self.t)
    ui.card(230, 220, 180, 150, { fill = color, radius = 24 })
    ui.set(ui.c.white)
    text.centered("bold", tostring(self.result), 230, 220, 180, 150, 128)
    ui.badge("a", 320, 420, 18)
  elseif self.engine then
    self.engine:draw()
    ui.progress(self.index - 1, #self.levels, 120, 18, 400)
  else
    ui.guide(320, 200, 2.4, "talk", self.t)
  end
end

return Placement
