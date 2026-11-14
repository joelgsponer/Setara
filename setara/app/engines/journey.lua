-- Journey: cross the stream by answering. The question is a Listen and Pick
-- question (press the direction of the right picture). Along the bottom runs
-- a stream with stepping stones; the guide bird hops one stone forward for
-- each question solved and stands on the far bank when the round is over.
-- A sum with `hop` ("3+2", "7-3") is shown on a number line after the right
-- answer: the bird starts at the first number and makes the hops one by one.
-- A skips the number line.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local common = require("engines.common")
local g = love.graphics

local E = {}
E.__index = E

local WATER_Y, STONE_Y = 428, 460 -- the stream runs behind the bottom card
local BIRD = 0.55
local JUMP = 0.45                 -- seconds for one hop on the path
local LINE_X, LINE_STEP, LINE_Y = 50, 27, 282

-- "3+2" -> start, number of hops, direction, result; nil unless all within 0..20.
local function parse_hop(s)
  if type(s) ~= "string" then return nil end
  local a, op, b = s:match("^%s*(%d+)%s*([+-])%s*(%d+)%s*$")
  a, b = tonumber(a), tonumber(b)
  if not a or not b then return nil end
  local r = op == "+" and a + b or a - b
  if a > 20 or b > 20 or r < 0 or r > 20 then return nil end
  local step = math.min(0.4, 1.2 / math.max(1, b))
  return { a = a, b = b, r = r, dir = op == "+" and 1 or -1, op = op == "+" and "+" or "−",
    step = step, len = 0.5 + b * step + 0.8 }
end

-- x of every place on the path: 0 is the near bank, total the far bank. The
-- stones keep clear of the bottom card, the bird jumps over it.
local function make_path(total)
  local xs = { [0] = 24 }
  local n = math.max(0, total - 1)
  local nl = math.ceil(n / 2)
  local function spread(from, to, count, first)
    for i = 1, count do
      xs[first + i - 1] = count == 1 and (from + to) / 2 or from + (to - from) * (i - 1) / (count - 1)
    end
    return count > 1 and math.min(20, (to - from) / (count - 1) * 0.45) or 20
  end
  local r = math.min(spread(70, 222, nl, 1), spread(418, 570, n - nl, nl + 1))
  xs[math.max(1, total)] = 616
  return xs, r
end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.quiz = Quiz.new(round.items or {})
  self.xs, self.stone_r = make_path(self.quiz.total)
  self.pos = 0
  self.phase = "wait"
  self.t, self.clock = 0, 0
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
  self.slots = common.deal(item, self.quiz.level)
  self.wrong = {}
  self.phase = "ask"
  self.t = 0
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

-- Where the bird should stand: one place per question solved; the far bank
-- is kept for the very end of the round.
function E:place()
  local q = self.quiz
  if q:finished() then return math.max(1, q.total) end
  return math.min(q.done, math.max(0, q.total - 1))
end

function E:input(b)
  if self.phase == "hop" then
    if b == "a" then self:next() end
    return
  end
  if self.phase ~= "ask" then return end
  if b == "a" then return self:again(false) end
  local slot = self.slots[b]
  if not slot or self.wrong[b] then return end
  if slot.right then
    self.phase, self.t, self.picked = "right", 0, b
    sfx.play("right")
    audio.stop()
    self.quiz:right()
    self.ctx.next_player()
    local to = self:place()
    if to > self.pos then self.jump = { from = self.pos, to = to, t = -0.3 } end
  else
    self.wrong[b] = true
    self.shake, self.shake_t = b, 0.4
    sfx.play("wrong")
    self.quiz:wrong()
    self:again(false)
  end
end

function E:update(dt)
  self.t = self.t + dt
  self.clock = self.clock + dt
  if self.shake_t then
    self.shake_t = self.shake_t - dt
    if self.shake_t <= 0 then self.shake, self.shake_t = nil, nil end
  end
  local j = self.jump
  if j then
    local before = j.t
    j.t = j.t + dt
    if before < 0 and j.t >= 0 then sfx.play("hop") end
    if j.t >= JUMP then self.pos, self.jump = j.to, nil end
  end
  if self.phase == "right" and self.t > 0.9 then
    self.hop = parse_hop(self.item.hop)
    if self.hop then
      self.phase, self.t, self.ticks = "hop", 0, 0
    else
      self:next()
    end
  elseif self.phase == "hop" then
    local h = self.hop
    local made = math.max(0, math.min(h.b, math.floor((self.t - 0.5) / h.step)))
    if made > self.ticks then
      self.ticks = made
      sfx.play("tick")
    end
    if self.t > h.len then self:next() end
  end
end

local function draw_path(self)
  ui.set(ui.c.water)
  g.rectangle("fill", 0, WATER_Y, ui.W, ui.H - WATER_Y)
  ui.set(ui.c.white, 0.35)
  g.setLineWidth(2)
  for i = 0, 7 do
    local x = (i * 90 + self.clock * 12) % 720 - 40
    g.line(x, WATER_Y + 12 + (i % 3) * 14, x + 26, WATER_Y + 12 + (i % 3) * 14)
  end
  g.setLineWidth(1)
  ui.set(ui.c.grass)
  g.rectangle("fill", 0, WATER_Y - 4, 48, ui.H - WATER_Y + 4, 0, 0)
  g.rectangle("fill", ui.W - 48, WATER_Y - 4, 48, ui.H - WATER_Y + 4)
  ui.set(ui.c.hill)
  g.rectangle("fill", 0, WATER_Y - 4, 48, 5)
  g.rectangle("fill", ui.W - 48, WATER_Y - 4, 48, 5)
  local r = self.stone_r
  for i = 1, self.quiz.total - 1 do
    local x = self.xs[i]
    ui.set(i <= self.pos and ui.c.earth or ui.c.shade)
    g.ellipse("fill", x, STONE_Y, r, r * 0.55)
    ui.set(ui.c.ink, 0.6)
    g.setLineWidth(2)
    g.ellipse("line", x, STONE_Y, r, r * 0.55)
    g.setLineWidth(1)
  end
end

local function draw_bird(self)
  local x, y = self.xs[self.pos] or 24, STONE_Y - 29 * BIRD
  local mood = "idle"
  local j = self.jump
  if j and j.t > 0 then
    local u = math.min(1, j.t / JUMP)
    local from, to = self.xs[j.from] or 24, self.xs[j.to] or 616
    x = from + (to - from) * u
    y = y - math.sin(u * math.pi) * (22 + math.abs(to - from) * 0.12)
  elseif self.phase == "right" or self.phase == "hop" then
    if self.pos >= self.quiz.total then mood = "happy" end
  end
  ui.guide(x, y, BIRD, mood, self.clock)
end

local function line_x(n) return LINE_X + n * LINE_STEP end

-- The number line 0..20 with the bird making the hops of the sum.
local function draw_hops(self)
  local h, t = self.hop, self.t
  ui.set(ui.c.bg, 0.6)
  g.rectangle("fill", 0, 38, ui.W, WATER_Y - 42)
  ui.card(16, 112, 608, 226, { border = ui.c.math })
  local u = (t - 0.5) / h.step        -- hops made so far, with fraction
  u = math.max(0, math.min(h.b, u))
  local made = math.floor(u)
  local frac = u - made
  local done = made >= h.b

  -- the sum; its answer appears when the bird has arrived
  local sum = h.a .. " " .. h.op .. " " .. h.b .. " ="
  local f = text.font("bold", 44)
  local w = f:getWidth(sum .. " 00")
  g.setFont(f)
  ui.set(ui.c.ink)
  g.print(sum, 320 - w / 2, 120)
  if done then
    ui.set(ui.c.good)
    g.print(" " .. h.r, 320 - w / 2 + f:getWidth(sum), 120)
  end

  ui.set(ui.c.ink)
  g.setLineWidth(3)
  g.line(line_x(0) - 12, LINE_Y, line_x(20) + 12, LINE_Y)
  for n = 0, 20 do
    local big = n % 5 == 0
    g.line(line_x(n), LINE_Y - (big and 9 or 5), line_x(n), LINE_Y + (big and 9 or 5))
    if big then text.centered("bold", tostring(n), line_x(n) - 24, LINE_Y + 10, 48, 34, 24, 24) end
  end
  -- the hops already made
  ui.set(ui.c.math)
  for k = 1, made do
    local mid = line_x(h.a + h.dir * (k - 0.5))
    g.arc("line", "open", mid, LINE_Y, LINE_STEP / 2, math.pi, 2 * math.pi)
  end
  g.setLineWidth(1)
  ui.set(ui.c.soft)
  g.circle("fill", line_x(h.a), LINE_Y, 6)
  if done then
    ui.set(ui.c.good)
    g.circle("fill", line_x(h.r), LINE_Y, 7)
  end

  local at = h.a + h.dir * u
  local bx = line_x(at)
  local by = LINE_Y - 14 - math.sin(frac * math.pi) * 14
  ui.guide(bx, by, 0.42, done and "happy" or "idle", done and t or 0)
  ui.set(done and ui.c.good or ui.c.ink)
  text.centered("bold", tostring(h.a + h.dir * made), bx - 30, LINE_Y - 82, 60, 40, 30, 30)
  ui.badge("a", 598, 136, 13)
end

function E:draw()
  draw_path(self)
  if not self.item then
    draw_bird(self)
    return
  end
  common.draw_center(self.ctx.root, self.item, audio.busy(), self.t)
  for dir, slot in pairs(self.slots) do
    local state
    if self.phase ~= "ask" and dir == self.picked then state = "right"
    elseif self.shake == dir then state = "shake"
    elseif self.wrong[dir] then state = "wrong" end
    common.draw_slot(self.ctx.root, slot, state, self.phase == "hop" and 1 or self.t)
  end
  if self.phase == "hop" then draw_hops(self) end
  draw_bird(self)
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
