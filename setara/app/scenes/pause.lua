-- Pause (Start button): volume, carry on, go home. Drawn over the scene below.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local g = love.graphics

local Pause = {}
Pause.__index = Pause

-- opts.home: opened from the home screen (no "go home" row)
-- opts.teacher: also shows the class size
function Pause.new(opts)
  opts = opts or {}
  local self = setmetatable({ overlay = true, sel = 1, t = 0 }, Pause)
  self.rows = { "volume", "resume" }
  if opts.teacher then table.insert(self.rows, 2, "class") end
  if not opts.home then self.rows[#self.rows + 1] = "home" end
  return self
end

function Pause:enter()
  audio.stop()
end

function Pause:leave()
  store.save_progress()
end

function Pause:update(dt) self.t = self.t + dt end

function Pause:input(b)
  local row = self.rows[self.sel]
  local set = store.progress.settings
  if b == "up" then self.sel = math.max(1, self.sel - 1) sfx.play("move")
  elseif b == "down" then self.sel = math.min(#self.rows, self.sel + 1) sfx.play("move")
  elseif b == "left" or b == "right" then
    local step = b == "left" and -1 or 1
    if row == "volume" then
      set.volume = math.max(0.1, math.min(1, set.volume + step * 0.1))
      audio.set_volume(set.volume)
      sfx.play("right")
    elseif row == "class" then
      set.class_size = math.max(1, math.min(80, set.class_size + step))
      sfx.play("move")
    end
  elseif b == "a" then
    if row == "home" then app.home() else app.pop() end
  elseif b == "b" or b == "start" then
    app.pop()
  end
end

function Pause:draw()
  ui.set(ui.c.ink, 0.55)
  g.rectangle("fill", 0, 0, ui.W, ui.H)
  local h = 70 + #self.rows * 74
  local y0 = (ui.H - h) / 2
  ui.card(130, y0, 380, h, { radius = 20 })
  local set = store.progress.settings
  for i, row in ipairs(self.rows) do
    local y = y0 + 34 + (i - 1) * 74
    local selected = i == self.sel
    ui.card(154, y, 332, 62, { fill = selected and ui.c.shade or ui.c.paper, selected = selected })
    if row == "volume" then
      ui.speaker(190, y + 31, 40, nil, ui.c.ink)
      for k = 1, 10 do
        local on = k <= math.floor(set.volume * 10 + 0.5)
        ui.set(on and ui.c.good or ui.c.line)
        g.rectangle("fill", 222 + k * 23, y + 44 - k * 3, 16, 6 + k * 3, 3, 3)
      end
    elseif row == "class" then
      for k = 0, 2 do
        ui.set(ui.c.teacher)
        g.circle("fill", 178 + k * 18, y + 24, 7)
        g.rectangle("fill", 170 + k * 18, y + 33, 16, 14, 4, 4)
      end
      ui.arrow("left", 300, y + 31, 9, ui.c.ink)
      ui.set(ui.c.ink)
      text.centered("bold", tostring(set.class_size), 316, y, 80, 62, 36)
      ui.arrow("right", 412, y + 31, 9, ui.c.ink)
    elseif row == "resume" then
      ui.set(ui.c.good)
      g.polygon("fill", 300, y + 14, 300, y + 48, 336, y + 31)
      ui.set(ui.c.ink)
      local s = packs.string("resume")
      if s.fa then text.fa(s.fa, 350, y + 6, 126, 24, "right", true) end
    elseif row == "home" then
      ui.set(ui.c.en)
      g.polygon("fill", 296, y + 30, 320, y + 10, 344, y + 30)
      g.rectangle("fill", 302, y + 30, 36, 22)
      ui.set(ui.c.ink)
      local s = packs.string("go_home")
      if s.fa then text.fa(s.fa, 350, y + 6, 126, 24, "right", true) end
    end
  end
end

return Pause
