-- Market: count goods or pay at a stall.
-- count: the customer asks for some goods ("Three apples, please"). Up puts
--   one more on the tray, down takes one away; the goods lie in rows of five
--   so they can be counted. A = done.
-- pay: the purse holds one coin or note of each value. Left/right choose
--   one, up puts one of it on the counter, down takes one of it back. The
--   total is only shown as a number after A. A = done.
-- A right amount moves on; a wrong one makes the person at the stall shake
-- the head, the counter is cleared and the request is said again.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local g = love.graphics

local E = {}
E.__index = E

local SKIN = { 0.87, 0.69, 0.52 }
local NOTE = { 0.66, 0.82, 0.62 }
local AREA = { x = 228, y = 96, w = 396 }  -- tray (count) or counter top (pay)
local PILE_MAX = 12

-- Fewest pieces that make the target, so the pile limit never blocks a
-- reachable answer.
local function fewest(target, units)
  local best = { [0] = 0 }
  for t = 1, target do
    for _, u in ipairs(units) do
      if u <= t and best[t - u] and (not best[t] or best[t - u] + 1 < best[t]) then best[t] = best[t - u] + 1 end
    end
  end
  return best[target]
end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.quiz = Quiz.new(round.items or {})
  self.phase = "wait"
  self.t, self.clock = 0, 0
  self.served = 0
  return self
end

function E:start() self:next() end

function E:clear()
  self.n = 0
  self.pile = {}
end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.served = self.served + 1
  self.target = math.max(0, math.floor(tonumber(item.target) or 0))
  self.pay = item.mode == "pay"
  self.goods = (type(item.goods) == "table" or type(item.goods) == "string") and item.goods or nil
  self.units = {}
  if self.pay then
    for _, u in ipairs(type(item.units) == "table" and item.units or {}) do
      u = tonumber(u)
      if u and u > 0 and #self.units < 6 then self.units[#self.units + 1] = math.floor(u) end
    end
    if #self.units == 0 then self.units[1] = 1 end
    self.sel = 1
    self.cap = math.max(PILE_MAX, math.min(24, fewest(math.min(self.target, 2000), self.units) or 0))
  else
    self.cap = math.max(20, math.min(30, self.target))
  end
  self:clear()
  self.phase, self.t = "play", 0
  self:again(false)
end

function E:again(slow)
  if self.item then self.ctx.say(self.item.prompt_audio, { slow = slow }) end
end

function E:help()
  if not self.item then return end
  if self.item.help_audio and #self.item.help_audio > 0 then
    self.ctx.say(self.item.help_audio)
  else
    self:again(true)
  end
end

function E:sum()
  if not self.pay then return self.n end
  local s = 0
  for _, v in ipairs(self.pile) do s = s + v end
  return s
end

function E:add()
  local count = self.pay and #self.pile or self.n
  if count >= self.cap then
    self.bump = 0.3 -- full: a small shake, nothing more
    return
  end
  if self.pay then self.pile[#self.pile + 1] = self.units[self.sel] else self.n = self.n + 1 end
  sfx.play("tick")
end

function E:take()
  if not self.pay then
    if self.n > 0 then
      self.n = self.n - 1
      sfx.play("flip")
    end
    return
  end
  for i = #self.pile, 1, -1 do
    if self.pile[i] == self.units[self.sel] then
      table.remove(self.pile, i)
      sfx.play("flip")
      return
    end
  end
end

function E:input(b)
  if self.phase ~= "play" then return end
  if b == "up" then self:add()
  elseif b == "down" then self:take()
  elseif self.pay and (b == "left" or b == "right") then
    local to = self.sel + (b == "left" and -1 or 1)
    if to >= 1 and to <= #self.units then
      self.sel = to
      sfx.play("move")
    end
  elseif b == "a" then
    local sum = self:sum()
    if sum == 0 then return self:again(false) end -- nothing placed yet: just say it again
    self.t = 0
    if sum == self.target then
      self.phase = "right"
      sfx.play("right")
      audio.stop()
      self.quiz:right()
      self.ctx.next_player()
    else
      self.phase = "no"
      sfx.play("wrong")
      audio.stop()
      self.quiz:wrong()
    end
  end
end

function E:update(dt)
  self.t = self.t + dt
  self.clock = self.clock + dt
  if self.bump then
    self.bump = self.bump - dt
    if self.bump <= 0 then self.bump = nil end
  end
  if self.phase == "right" and self.t > 0.9 then
    self:next()
  elseif self.phase == "no" and self.t > 1.1 then
    self:clear()
    self.phase, self.t = "play", 0
    self:again(false)
  end
end

-- Drawing -------------------------------------------------------------------

local function awning()
  for i = 0, 15 do
    ui.set(i % 2 == 0 and ui.c.en or ui.c.paper)
    g.rectangle("fill", i * 40, 38, 40, 40)
    g.circle("fill", i * 40 + 20, 78, 20)
  end
  ui.set(ui.c.ink, 0.25)
  g.rectangle("fill", 0, 38, ui.W, 3)
end

-- The person at the stall; girls and boys take turns. mood: idle, talk, happy, no
local function person(cx, cy, girl, mood, t)
  local hx = cx + (mood == "no" and math.sin(t * 18) * 8 or 0)
  local hy = cy - (mood == "happy" and math.abs(math.sin(t * 9)) * 7 or 0)
  ui.set(girl and ui.c.math or ui.c.teacher)
  g.rectangle("fill", cx - 46, cy + 28, 92, 120, 28, 28)
  if girl then
    ui.set(ui.c.fa)
    g.circle("fill", hx, hy - 2, 37)
    g.rectangle("fill", hx - 30, hy + 4, 60, 40, 14, 14)
  end
  ui.set(SKIN)
  g.circle("fill", hx, hy + (girl and 3 or 0), girl and 27 or 31)
  if not girl then
    ui.set(ui.c.wood)
    g.arc("fill", "closed", hx, hy - 9, 32, math.pi, 2 * math.pi)
  end
  local fy = hy + (girl and 3 or 2)
  ui.set(ui.c.ink)
  g.circle("fill", hx - 10, fy - 3, 3.5)
  g.circle("fill", hx + 10, fy - 3, 3.5)
  g.setLineWidth(3)
  if mood == "happy" then
    g.arc("line", "open", hx, fy + 6, 10, 0.15, math.pi - 0.15)
  elseif mood == "no" then
    g.arc("line", "open", hx, fy + 18, 8, math.pi + 0.3, 2 * math.pi - 0.3)
  elseif mood == "talk" and math.sin(t * 16) > 0 then
    g.ellipse("fill", hx, fy + 11, 6, 5)
  else
    g.arc("line", "open", hx, fy + 7, 7, 0.3, math.pi - 0.3)
  end
  g.setLineWidth(1)
end

local function piece(v, cx, cy, r)
  local label = tostring(v)
  if v < 10 then
    ui.set(ui.c.gold)
    g.circle("fill", cx, cy, r)
    ui.set(ui.c.ink)
    g.setLineWidth(2)
    g.circle("line", cx, cy, r)
    ui.set(ui.c.ink, 0.35)
    g.circle("line", cx, cy, r - 5)
    g.setLineWidth(1)
    ui.set(ui.c.ink)
    text.centered("bold", label, cx - r, cy - r, r * 2, r * 2, 44, 24)
  else
    local w, h = r * 2.1, r * 1.35
    ui.set(NOTE)
    g.rectangle("fill", cx - w / 2, cy - h / 2, w, h, 5, 5)
    ui.set(ui.c.ink)
    g.setLineWidth(2)
    g.rectangle("line", cx - w / 2, cy - h / 2, w, h, 5, 5)
    g.setLineWidth(1)
    text.centered("bold", label, cx - w / 2, cy - h / 2, w, h, 36, 24)
  end
end

local function sign(kind, cx, cy, s)
  ui.set(ui.c.ink)
  g.setLineWidth(5)
  if kind == "check" then
    ui.set(ui.c.good)
    g.line(cx - s, cy, cx - s * 0.3, cy + s * 0.7, cx + s, cy - s * 0.7)
  else
    g.line(cx - s, cy, cx + s, cy)
    if kind == "plus" then g.line(cx, cy - s, cx, cy + s) end
  end
  g.setLineWidth(1)
end

-- Which button does what, without words.
local function hints(self)
  local x = self.pay and 250 or 290
  if self.pay then
    ui.arrow("left", x, 442, 11)
    ui.arrow("right", x + 30, 442, 11)
    x = x + 90
  end
  ui.arrow("up", x, 442, 12)
  sign("plus", x + 30, 442, 9)
  ui.arrow("down", x + 90, 442, 12)
  sign("minus", x + 120, 442, 9)
  ui.badge("a", x + 190, 442, 16)
  sign("check", x + 224, 442, 10)
end

local function draw_goods(self, ox)
  local rows = math.ceil(self.cap / 5)
  local h = 304
  local cell = math.min(72, (h - 16) / rows)
  ui.card(ox, AREA.y, AREA.w, h, { fill = ui.c.shade, border = ui.c.wood, width = 4 })
  local x0 = ox + (AREA.w - cell * 5) / 2
  local y0 = AREA.y + h - 8 - cell
  for i = 0, self.n - 1 do
    local x, y = x0 + (i % 5) * cell, y0 - math.floor(i / 5) * cell
    if self.phase == "right" then y = y - math.abs(math.sin(self.t * 9 + i * 0.7)) * 5 end
    if self.goods then
      ui.thing(self.goods, self.ctx.root, x + 1, y + 1, cell - 2, cell - 2)
    else
      ui.set(ui.c.en)
      g.circle("fill", x + cell / 2, y + cell / 2, cell * 0.36)
    end
  end
end

local function draw_pay(self, ox)
  ui.card(ox, AREA.y, AREA.w, 186, { fill = ui.c.shade, border = ui.c.wood, width = 4 })
  local per = self.cap > PILE_MAX and 8 or 6
  local cell = self.cap > PILE_MAX and 47 or 62
  local x0 = ox + (AREA.w - cell * per) / 2 + cell / 2
  for i, v in ipairs(self.pile) do
    local x = x0 + ((i - 1) % per) * cell
    local y = AREA.y + 12 + cell / 2 + math.floor((i - 1) / per) * cell
    if self.phase == "right" then y = y - math.abs(math.sin(self.t * 9 + i * 0.7)) * 4 end
    piece(v, x, y, cell / 2 - 4)
  end
  if self.phase ~= "play" then
    ui.set(self.phase == "right" and ui.c.good or ui.c.bad)
    text.centered("bold", "= " .. self:sum(), AREA.x, AREA.y + 146, AREA.w, 36, 24, 24)
  end
  -- the purse: one of each value
  local n = #self.units
  local cw = math.min(96, (AREA.w - (n - 1) * 8) / n)
  local px = AREA.x + (AREA.w - (cw * n + (n - 1) * 8)) / 2
  for i, v in ipairs(self.units) do
    local x = px + (i - 1) * (cw + 8)
    local on = i == self.sel
    ui.card(x, 294 - (on and 4 or 0), cw, 106, { selected = on })
    piece(v, x + cw / 2, 347 - (on and 4 or 0), math.min(34, cw / 2 - 8))
  end
end

function E:draw()
  awning()
  if not self.item then return end
  local mood = audio.busy() and "talk" or "idle"
  if self.phase == "right" then mood = "happy" elseif self.phase == "no" then mood = "no" end
  -- speech bubble: the request is spoken
  ui.card(126, 104, 88, 60, { radius = 18, width = 2 })
  ui.set(ui.c.paper)
  g.polygon("fill", 128, 140, 112, 158, 140, 150)
  ui.speaker(170, 134, 44, audio.busy() and self.clock or nil, ui.c.ink)
  person(74, 166, self.served % 2 == 1, mood, self.t)
  -- the stall with what is asked for
  ui.set(ui.c.wood)
  g.rectangle("fill", 10, 268, 206, 136, 8, 8)
  ui.set(ui.c.earth)
  g.rectangle("fill", 6, 262, 214, 16, 6, 6)
  if self.goods then
    ui.card(60, 290, 104, 104)
    ui.thing(self.goods, self.ctx.root, 64, 294, 96, 96)
  end
  local ox = AREA.x + (self.bump and math.sin(self.bump * 60) * 5 or 0)
  if self.pay then draw_pay(self, ox) else draw_goods(self, ox) end
  if self.phase == "right" then
    local pop = math.sin(math.min(1, self.t * 2.5) * math.pi)
    ui.star(600, 112, 14 + pop * 14, true)
  end
  hints(self)
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
