-- Duel: two players, one device, the fastest right answer wins the point.
-- The question is a Listen and Pick question with up to four cards.
-- Player 1 answers with the D-pad (the direction of the card). Player 2
-- answers with the face buttons by their place on the pad: X is the upper
-- card, B the lower, Y the left, A the right. A wrong answer locks that
-- player out of this question only; if both are out the right card is shown
-- and the question comes back once later. Nobody can press "again", so the
-- question is repeated by itself every few seconds.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local common = require("engines.common")
local g = love.graphics

local E = {}
E.__index = E

local P1 = { up = "up", down = "down", left = "left", right = "right" }
local P2 = { x = "up", b = "down", y = "left", a = "right" }
local REPEAT = 6   -- seconds of silence before the question is said again
local SHOW = 2     -- seconds of the "who uses which buttons" picture

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.uses = { a = true, b = true, x = true, y = true }
  self.quiz = Quiz.new(round.items or {})
  self.score = { 0, 0 }
  self.locked = {}
  self.attempts = 0
  self.phase = "wait"
  self.t, self.clock = 0, 0
  return self
end

function E:start()
  self.phase, self.t = "show", 0
end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.slots = common.deal(item, 4)
  if not self.slots then
    -- a question that cannot be asked is passed over, never shown
    self.quiz:right()
    return self:next()
  end
  self.wrong, self.locked = {}, {}
  self.picked, self.winner = nil, nil
  self.phase, self.t, self.quiet = "ask", 0, 0
  self:again(false)
end

function E:again(slow)
  if self.item then self.ctx.say(self.item.prompt_audio, { slow = slow }) end
  self.quiet = 0
end

-- Y is an answer button here; kept for the engine interface.
function E:help() self:again(true) end

function E:input(b)
  if self.phase ~= "ask" then return end
  local player, dir = 1, P1[b]
  if not dir then player, dir = 2, P2[b] end
  if not dir or self.locked[player] then return end
  local slot = self.slots[dir]
  if not slot or self.wrong[dir] then return end
  self.attempts = self.attempts + 1
  if slot.right then
    self.phase, self.t, self.picked, self.winner = "right", 0, dir, player
    self.score[player] = self.score[player] + 1
    sfx.play("right")
    audio.stop()
    self.quiz:right()
  else
    self.wrong[dir] = true
    self.locked[player] = true
    self.shake, self.shake_t = dir, 0.4
    sfx.play("wrong")
    if self.locked[1] and self.locked[2] then
      -- nobody got it: show the answer, the question comes back later
      self.phase, self.t = "none", 0
      audio.stop()
      self.quiz:wrong()
      self.quiz:right()
    end
  end
end

function E:update(dt)
  self.t = self.t + dt
  self.clock = self.clock + dt
  if self.shake_t then
    self.shake_t = self.shake_t - dt
    if self.shake_t <= 0 then self.shake, self.shake_t = nil, nil end
  end
  if self.phase == "show" then
    if self.t > SHOW then self:next() end
  elseif self.phase == "ask" then
    if not audio.busy() then
      self.quiet = self.quiet + dt
      if self.quiet >= REPEAT then self:again(false) end
    end
  elseif self.phase == "right" then
    if self.t > 0.9 then self:next() end
  elseif self.phase == "none" then
    if self.t > 1.0 then self:next() end
  end
end

-- Glyphs --------------------------------------------------------------------

local function dpad(cx, cy, s, color, alpha)
  local a = s * 0.34
  ui.set(ui.c.ink, alpha)
  g.rectangle("fill", cx - s - 3, cy - a - 3, s * 2 + 6, a * 2 + 6, 6, 6)
  g.rectangle("fill", cx - a - 3, cy - s - 3, a * 2 + 6, s * 2 + 6, 6, 6)
  ui.set(color, alpha)
  g.rectangle("fill", cx - s, cy - a, s * 2, a * 2, 4, 4)
  g.rectangle("fill", cx - a, cy - s, a * 2, s * 2, 4, 4)
  for _, d in ipairs({ "up", "down", "left", "right" }) do
    local dx = d == "left" and -1 or d == "right" and 1 or 0
    local dy = d == "up" and -1 or d == "down" and 1 or 0
    ui.arrow(d, cx + dx * s * 0.68, cy + dy * s * 0.68, s * 0.17, ui.c.white)
  end
end

local function diamond(cx, cy, s, color, alpha)
  local r, d = s * 0.36, s * 0.66
  for i = 1, 4 do
    local x = cx + (i == 3 and -d or i == 4 and d or 0)
    local y = cy + (i == 1 and -d or i == 2 and d or 0)
    ui.set(ui.c.ink, alpha)
    g.circle("fill", x, y, r + 3)
    ui.set(color, alpha)
    g.circle("fill", x, y, r)
  end
end

local function cross(cx, cy, r)
  ui.set(ui.c.bad)
  g.setLineWidth(6)
  g.line(cx - r, cy - r, cx + r, cy + r)
  g.line(cx - r, cy + r, cx + r, cy - r)
  g.setLineWidth(1)
end

local function child(cx, cy, color)
  ui.set(color)
  g.circle("fill", cx, cy, 20)
  g.rectangle("fill", cx - 22, cy + 24, 44, 40, 12, 12)
end

-- Drawing -------------------------------------------------------------------

local function draw_show(self)
  for p = 1, 2 do
    local color = p == 1 and ui.c.en or ui.c.fa
    local x = p == 1 and 40 or 340
    ui.card(x, 96, 260, 330, { fill = ui.mix(ui.c.paper, color, 0.22), border = color, width = 5 })
    child(x + 130, 136, color)
    local bob = math.sin(self.t * 6 + p) * 4
    if p == 1 then dpad(x + 130, 310 + bob, 78, color) else diamond(x + 130, 310 + bob, 78, color) end
  end
end

local function draw_scores(self)
  for p = 1, 2 do
    local color = p == 1 and ui.c.en or ui.c.fa
    local gx = p == 1 and 58 or 582
    local nx = p == 1 and 108 or 412
    local out = self.locked[p] and (self.phase == "ask" or self.phase == "none")
    local alpha = out and 0.3 or 1
    if p == 1 then dpad(gx, 100, 36, color, alpha) else diamond(gx, 100, 36, color, alpha) end
    local pop = 0
    if self.phase == "right" and self.winner == p then pop = math.sin(math.min(1, self.t * 2.5) * math.pi) * 10 end
    ui.set(color)
    text.centered("bold", tostring(self.score[p]), nx, 52 - pop, 120, 100, 72)
    if out then cross(gx, 158, 11) end
  end
end

-- The winning card flashes in the winner's colour.
local function draw_won(root, slot, color, t)
  local grow = math.sin(math.min(1, t * 3) * math.pi) * 6
  local x, y, w, h = slot.x - grow, slot.y - grow, slot.w + grow * 2, slot.h + grow * 2
  local on = math.floor(t * 9) % 2 == 0
  ui.card(x, y, w, h, { fill = ui.mix(ui.c.paper, color, on and 0.55 or 0.25), border = color, width = 7 })
  ui.thing(slot.thing, root, x + 6, y + 6, w - 12, h - 12)
end

function E:draw()
  if self.phase == "show" then return draw_show(self) end
  if not self.item then return end
  draw_scores(self)
  common.draw_center(self.ctx.root, self.item, audio.busy(), self.t)
  for dir, slot in pairs(self.slots) do
    if self.phase == "right" and dir == self.picked then
      draw_won(self.ctx.root, slot, self.winner == 1 and ui.c.en or ui.c.fa, self.t)
    else
      local state
      if self.phase == "none" and slot.right then state = "right"
      elseif self.shake == dir then state = "shake"
      elseif self.wrong[dir] then state = "wrong" end
      common.draw_slot(self.ctx.root, slot, state, self.t)
    end
  end
end

-- Cooperative: how many questions were answered right by either player the
-- first time they came up.
function E:stars() return self.quiz:stars() end
function E:counts() return self.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
