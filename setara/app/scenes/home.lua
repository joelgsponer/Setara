-- Home: the valley with its four places.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local input = require("core.input")
local valley = require("core.valley")
local g = love.graphics

local Home = {}
Home.__index = Home

local PLACES = {
  { subject = "en", x = 28, y = 96, col = 1, row = 1 },
  { subject = "fa", x = 384, y = 96, col = 2, row = 1 },
  { subject = "math", x = 18, y = 290, col = 1, row = 2 },
  { subject = "garden", x = 384, y = 292, col = 2, row = 2 },
}
local TEACHER_HOLD = 2

function Home.new()
  local self = setmetatable({ t = 0, sel = 1, hold = 0 }, Home)
  local last = store.progress.last
  for i, p in ipairs(PLACES) do
    if last and last.subject == p.subject then self.sel = i end
  end
  return self
end

function Home:enter()
  self:count()
  audio.say(packs.string("home_welcome").audio)
end

function Home:resume()
  self:count()
end

-- Stars earned and stars available, per subject.
function Home:count()
  self.stage, self.stars = {}, {}
  for _, p in ipairs(PLACES) do
    local have, max = 0, 0
    for _, pack in pairs(packs.subjects[p.subject] or {}) do
      for _, game in ipairs(pack.games or {}) do
        for _, id in ipairs(game.rounds or {}) do
          max = max + 3
          have = have + store.stars(id)
        end
      end
    end
    self.stars[p.subject] = have
    self.stage[p.subject] = valley.stage(have, max)
  end
end

function Home:update(dt)
  self.t = self.t + dt
  self.hold = input.held("l", "r")
  if self.hold >= TEACHER_HOLD then
    input.down.l, input.down.r = nil, nil
    self.hold = 0
    sfx.play("chime")
    app.push(require("teacher.menu").new())
  end
end

function Home:input(b)
  local p = PLACES[self.sel]
  local col, row = p.col, p.row
  if b == "left" or b == "right" then col = 3 - col
  elseif b == "up" or b == "down" then row = 3 - row
  elseif b == "a" then
    if next(packs.subjects[p.subject] or {}) then
      sfx.play("right")
      app.push(require("scenes.place").new(p.subject))
    else
      sfx.play("wrong")
    end
    return
  elseif b == "start" then
    app.push(require("scenes.pause").new({ home = true }))
    return
  else
    return
  end
  for i, q in ipairs(PLACES) do
    if q.col == col and q.row == row then self.sel = i end
  end
  sfx.play("move")
  audio.say(packs.string("place_" .. PLACES[self.sel].subject).audio)
end

function Home:draw()
  valley.background(self.t)
  for i, p in ipairs(PLACES) do
    local selected = i == self.sel
    if selected then
      local pulse = 3 + math.sin(self.t * 5) * 2
      ui.set(ui.c.gold, 0.22)
      g.rectangle("fill", p.x - 10 - pulse, p.y - 22 - pulse, 240 + pulse * 2, 170 + pulse * 2, 18, 18)
      ui.set(ui.c.gold)
      g.setLineWidth(5)
      g.rectangle("line", p.x - 10 - pulse, p.y - 22 - pulse, 240 + pulse * 2, 170 + pulse * 2, 18, 18)
      g.setLineWidth(1)
    end
    valley.draw[p.subject](p.x, p.y, self.stage[p.subject] or 0, self.t)
    -- name plate with the star count
    local s = packs.string("place_" .. p.subject)
    local px, py = p.x + 30, p.y + 122
    ui.card(px, py, 160, 30, { fill = ui.c.paper, border = ui.c[p.subject], width = 3, radius = 10 })
    ui.set(ui.c.ink)
    if text.locale == "en" then
      text.print(s.en or "", px + 66, py + 5, 90, "left", 16, true)
    elseif s.fa then
      text.fa(s.fa, px + 60, py - 6, 92, 24, "right", true)
    end
    ui.star(px + 16, py + 15, 9, true)
    ui.set(ui.c.ink)
    text.print(tostring(self.stars[p.subject] or 0), px + 28, py + 3, 40, "left", 20, true)
  end
  ui.guide(320, 60, 1.1, audio.busy() and "talk" or "idle", self.t)
  ui.set(ui.c.ink, 0.6)
  text.print(app.version, 6, 456, 200, "left", 16)
  -- the ring that fills while L and R are held: the way into teacher mode
  if self.hold > 0.15 then
    ui.set(ui.c.teacher)
    g.setLineWidth(8)
    g.arc("line", "open", 320, 240, 40, -math.pi / 2, -math.pi / 2 + (self.hold / TEACHER_HOLD) * math.pi * 2)
    g.setLineWidth(1)
  end
end

return Home
