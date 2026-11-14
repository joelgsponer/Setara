-- Catch: catch only the things that fit the spoken rule.
--
-- Things drift slowly down three lanes, one at a time. Left and right move
-- the basket between the lanes. A thing that fits the rule fills one of the
-- dots at the bottom; a thing that does not fit bounces off the basket.
-- Letting a thing fall past is never punished. When all dots are full the
-- next rule is spoken. Nothing falls while a new rule is being spoken.
-- The fall speed follows the quiz level: slower after mistakes.
local ui = require("core.ui")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local g = love.graphics

local E = {}
E.__index = E

local LANES = { 140, 320, 500 }
local TOP, CATCH_Y, R = 0, 380, 42
-- seconds from the top to the basket, by quiz level
local FALL = { [2] = 5.5, [3] = 4.0, [4] = 3.2 }
local SPACING = 144 -- px between two things: 1.6 s apart at normal speed

local function has(list) return type(list) == "table" and #list > 0 end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  local items = {}
  for _, it in ipairs(round.items or {}) do
    if has(it.targets) then items[#items + 1] = it end
  end
  self.quiz = Quiz.new(items)
  self.phase = "wait"
  self.t = 0
  self.lane, self.x = 2, LANES[2]
  self.things = {}
  return self
end

function E:start() self:next() end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.need = math.max(1, math.min(tonumber(item.need) or 5, 10))
  self.got = 0
  self.things = {}
  self.others_run = 0
  self.spawn_in = 0.3
  self.t = 0
  -- an item that comes back is already known: do not make the child wait
  self.phase = self.quiz:is_repeat() and "play" or "rule"
  self.ctx.say(item.prompt_audio)
end

function E:again(slow)
  if self.item then self.ctx.say(self.item.prompt_audio, { slow = slow }) end
end

function E:help()
  if not self.item then return end
  if has(self.item.help_audio) then
    self.ctx.say(self.item.help_audio)
  else
    self:again(true)
  end
end

function E:input(b)
  if not self.item or self.phase == "won" then return end
  if b == "left" or b == "right" then
    local lane = math.max(1, math.min(3, self.lane + (b == "left" and -1 or 1)))
    if lane ~= self.lane then
      self.lane = lane
      sfx.play("move")
    end
  elseif b == "a" and self.phase == "rule" then
    audio.stop() -- heard it: start
  end
end

function E:spawn()
  local item = self.item
  local others = has(item.others) and item.others or nil
  -- about half fit the rule, and never a long wait for one that does
  local target = not others or self.others_run >= 2 or love.math.random() < 0.5
  self.others_run = target and 0 or self.others_run + 1
  local list = target and item.targets or others
  self.things[#self.things + 1] = {
    thing = list[love.math.random(#list)], target = target,
    lane = love.math.random(3), y = TOP, state = "fall", t = 0,
  }
end

function E:caught(th)
  th.t = 0
  if th.target then
    th.state = "in"
    self.got = self.got + 1
    self.pop = 0
    sfx.play("right")
    if self.got >= self.need then
      self.phase, self.t = "won", 0
      self.quiz:right()
      self.ctx.next_player()
    end
  else
    th.state = "bounce"
    -- away from the basket, towards the nearer screen edge's opposite side
    th.vx = (th.lane == 1 and 1 or th.lane == 3 and -1 or (love.math.random(2) * 2 - 3)) * 110
    th.vy = -260
    th.x = LANES[th.lane]
    self.bump = 0.3
    sfx.play("wrong")
    self.quiz:wrong()
  end
end

function E:update(dt)
  self.t = self.t + dt
  self.x = self.x + (LANES[self.lane] - self.x) * math.min(1, dt * 14)
  if self.pop then
    self.pop = self.pop + dt
    if self.pop > 0.4 then self.pop = nil end
  end
  if self.bump then
    self.bump = self.bump - dt
    if self.bump <= 0 then self.bump = nil end
  end
  if not self.item then return end

  if self.phase == "rule" then
    if not audio.busy() and self.t > 0.3 then self.phase = "play" end
    return
  end
  if self.phase == "won" then
    if self.t > 0.9 then self:next() end
    return
  end

  local speed = (CATCH_Y - TOP) / (FALL[self.quiz.level] or FALL[3])
  self.spawn_in = self.spawn_in - dt
  if self.spawn_in <= 0 then
    self:spawn()
    self.spawn_in = SPACING / speed
  end
  for i = #self.things, 1, -1 do
    local th = self.things[i]
    th.t = th.t + dt
    if th.state == "fall" then
      th.y = th.y + speed * dt
      if th.y >= CATCH_Y then
        if th.lane == self.lane then self:caught(th) else th.state = "past" end
      end
    elseif th.state == "past" then
      th.y = th.y + speed * dt
      if th.y > ui.H + R then table.remove(self.things, i) end
    elseif th.state == "in" then
      if th.t > 0.25 then table.remove(self.things, i) end
    elseif th.state == "bounce" then
      th.vy = th.vy + 700 * dt
      th.x, th.y = th.x + th.vx * dt, th.y + th.vy * dt
      if th.y > ui.H + R or th.t > 1.5 then table.remove(self.things, i) end
    end
    if self.phase ~= "play" then break end -- the item was won: the list is new
  end
end

local function draw_thing(root, th)
  local x, y, r = th.x or LANES[th.lane], th.y, R
  local border, alpha = ui.c.ink, 1
  if th.state == "in" then
    r = R * (1 - th.t / 0.25 * 0.6)
    y = y + th.t / 0.25 * 26
    border = ui.c.good
  elseif th.state == "bounce" then
    border = ui.c.bad
  elseif th.state == "past" then
    alpha = 0.5
  end
  ui.set(ui.c.ink, 0.12)
  g.circle("fill", x + 2, y + 4, r)
  ui.set(ui.c.paper)
  g.circle("fill", x, y, r)
  g.setLineWidth(th.state == "fall" and 3 or 5)
  ui.set(border, alpha)
  g.circle("line", x, y, r)
  g.setLineWidth(1)
  -- the Dari font's line box is much taller than its letters: a tall box
  -- keeps the letters at 44 px inside the round card
  local bw = r * 1.5
  ui.thing(th.thing, root, x - bw / 2, y - r, bw, r * 2, { max_size = 56, alpha = alpha })
end

local function draw_catcher(self)
  local x, y = self.x, CATCH_Y + 22
  if self.phase == "won" then y = y - math.abs(math.sin(self.t * 10)) * 10 end
  if self.bump then x = x + math.sin(self.bump * 60) * 5 end
  if self.pop then y = y + math.sin(self.pop / 0.4 * math.pi) * 5 end
  -- a woven basket, open at the top
  local pts = { x - 62, y, x + 62, y, x + 46, y + 46, x - 46, y + 46 }
  ui.set(ui.c.earth)
  g.polygon("fill", pts)
  ui.set(ui.c.wood)
  g.setLineWidth(2)
  for i = 1, 3 do
    local yy = y + i * 11
    local half = 62 - 16 * (i * 11 / 46)
    g.line(x - half, yy, x + half, yy)
  end
  g.setLineWidth(4)
  ui.set(ui.c.ink)
  g.polygon("line", pts)
  ui.set(ui.c.wood)
  g.rectangle("fill", x - 68, y - 6, 136, 12, 6, 6)
  ui.set(ui.c.ink)
  g.setLineWidth(3)
  g.rectangle("line", x - 68, y - 6, 136, 12, 6, 6)
  g.setLineWidth(1)
end

function E:draw()
  if not self.item then return end
  -- the three lanes
  for i, x in ipairs(LANES) do
    ui.set(i == self.lane and ui.c.shade or ui.c.paper, 0.7)
    g.rectangle("fill", x - 70, 40, 140, 440, 16, 16)
  end
  for _, th in ipairs(self.things) do
    if th.state ~= "in" then draw_thing(self.ctx.root, th) end
  end
  draw_catcher(self)
  for _, th in ipairs(self.things) do
    if th.state == "in" then draw_thing(self.ctx.root, th) end
  end
  if self.phase == "rule" then
    ui.card(250, 150, 140, 130, { fill = ui.c.paper })
    ui.speaker(314, 215, 84, self.t, ui.c.ink)
    ui.arrow("left", 30, CATCH_Y + 44, 10, ui.c.soft)
    ui.arrow("right", 610, CATCH_Y + 44, 10, ui.c.soft)
  end
  -- one dot per thing still to catch
  local n = self.need
  local gap = math.min(26, 300 / n)
  local x0 = 320 - gap * (n - 1) / 2
  ui.set(ui.c.paper)
  g.rectangle("fill", x0 - 18, 456, gap * (n - 1) + 36, 22, 11, 11)
  for i = 1, n do
    local r = 7
    if i == self.got and self.pop then r = 7 + math.sin(self.pop / 0.4 * math.pi) * 4 end
    ui.set(i <= self.got and ui.c.good or ui.c.line)
    g.circle("fill", x0 + (i - 1) * gap, 467, r)
    ui.set(ui.c.ink, 0.6)
    g.circle("line", x0 + (i - 1) * gap, 467, r)
  end
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
