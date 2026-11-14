-- Sorter: drop each thing into the right basket.
--
-- Two to four baskets sit left, right, up and down of the centre. The thing
-- to sort lies on a card in the middle; one press of the D-pad drops it into
-- the basket on that side. Right: the basket bounces and says its name.
-- Wrong: the thing slides back and that basket is dimmed for this thing.
-- Many children cannot read the labels, so the round starts by saying every
-- basket in turn while it pulses (A skips), and Y says them all again.
local ui = require("core.ui")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local common = require("engines.common")
local g = love.graphics

local E = {}
E.__index = E

local ORDER = { { "left" }, { "left", "right" }, { "left", "up", "right" }, { "up", "left", "right", "down" } }
local RIMS = { "fa", "en", "garden", "math" }
local CENTER = { x = 225, y = 184, w = 190, h = 150 }
local DROP, BACK = 0.3, 0.25

local function has(list) return type(list) == "table" and #list > 0 end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.baskets, self.by_id, self.by_dir = {}, {}, {}
  local list = round.baskets or {}
  local n = math.min(#list, 4)
  for i = 1, n do
    local dir = ORDER[n][i]
    local s = common.SLOTS[dir]
    local b = { thing = list[i], audio = list[i].audio, dir = dir, rim = ui.c[RIMS[i]],
      x = s.x, y = s.y, w = s.w, h = s.h }
    -- the side baskets have room to be wider, so two-word labels stay large
    if dir == "left" then b.x, b.w = 24, 166 elseif dir == "right" then b.x, b.w = 450, 166 end
    self.baskets[i] = b
    self.by_dir[dir] = b
    if list[i].id ~= nil then self.by_id[list[i].id] = b end
  end
  -- A thing whose basket does not exist could never be solved: leave it out.
  local items = {}
  for _, it in ipairs(round.items or {}) do
    if it.thing and self.by_id[it.basket] then items[#items + 1] = it end
  end
  self.quiz = Quiz.new(items)
  self.phase = "wait"
  self.t = 0
  return self
end

function E:start()
  self.phase = "intro"
  self:speak_baskets(1)
end

-- Say the baskets one after the other from number i; the one being said pulses.
function E:speak_baskets(i)
  local b = self.baskets[i]
  if not b then
    self.speaking, self.speak_wait = nil, nil
    if self.phase == "intro" then self:next() end
    return
  end
  self.speaking, self.speak_wait = i, nil
  if has(b.audio) then
    self.ctx.say(b.audio, { after = 0.25, on_done = function()
      if self.speaking == i then self:speak_baskets(i + 1) end
    end })
  else
    self.speak_wait = 0.7 -- no clip: still show which basket is meant
  end
end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.target = self.by_id[item.basket]
  self.wrong = {}
  self.into = nil
  self.phase, self.t = "ask", 0
  self:again(false)
end

function E:again(slow)
  if self.phase == "intro" or not self.item then return end
  if has(self.item.prompt_audio) then
    self.speaking, self.speak_wait = nil, nil
    self.ctx.say(self.item.prompt_audio, { slow = slow })
  end
end

function E:help()
  if self.phase == "intro" or self.phase == "ask" then self:speak_baskets(1) end
end

function E:input(b)
  if self.phase == "intro" then
    if b == "a" then
      audio.stop()
      self.speaking, self.speak_wait = nil, nil
      self:next()
    end
    return
  end
  if self.phase ~= "ask" then return end
  if b == "a" then return self:again(false) end
  local basket = self.by_dir[b]
  if not basket or self.wrong[basket] then return end
  self.speaking, self.speak_wait = nil, nil
  self.into = basket
  self.phase, self.t = "drop", 0
  sfx.play("move")
end

function E:landed()
  local basket = self.into
  if basket == self.target then
    self.phase, self.t = "right", 0
    sfx.play("right")
    self.quiz:right()
    self.ctx.next_player()
    if not audio.busy() and has(basket.audio) then self.ctx.say(basket.audio) end
  else
    self.wrong[basket] = true
    self.phase, self.t = "back", 0
    sfx.play("wrong")
    self.quiz:wrong()
  end
end

function E:update(dt)
  self.t = self.t + dt
  if self.speak_wait then
    self.speak_wait = self.speak_wait - dt
    if self.speak_wait <= 0 then self:speak_baskets(self.speaking + 1) end
  end
  if self.phase == "drop" and self.t >= DROP then
    self:landed()
  elseif self.phase == "back" and self.t >= BACK then
    self.phase, self.t, self.into = "ask", 0, nil
    self:again(false)
  elseif self.phase == "right" and self.t > 0.8 and (not audio.busy() or self.t > 2.5) then
    self:next()
  end
end

local function draw_basket(self, b, i)
  local x, y, w, h = b.x, b.y, b.w, b.h
  local grow = 0
  local fill, rim = ui.c.paper, b.rim
  if self.phase == "right" and b == self.into then
    grow = math.abs(math.sin(math.min(1, self.t / 0.6) * math.pi * 2)) * 7
    fill, rim = ui.mix(ui.c.paper, ui.c.good, 0.35), ui.c.good
  elseif self.speaking == i then
    grow = (math.sin(self.t * 8) + 1) * 4
    fill = ui.mix(ui.c.paper, ui.c.gold, 0.3)
  end
  x, y, w, h = x - grow, y - grow, w + grow * 2, h + grow * 2
  local dim = self.wrong and self.wrong[b]
  ui.card(x, y, w, h, { fill = fill, border = rim, width = 7, dim = dim })
  -- the basket's lip
  ui.set(rim, dim and 0.3 or 1)
  g.rectangle("fill", x + 14, y + 9, w - 28, 6, 3, 3)
  ui.thing(b.thing, self.ctx.root, x + 8, y + 18, w - 16, h - 26, { alpha = dim and 0.35 or 1, max_size = 56 })
end

-- Letter forms (big = true) are the whole point of their round: draw them as
-- large as the card allows. The Dari font has a very tall line box, so let
-- the box overlap the card edge; the letter itself stays inside.
local function draw_big(thing, root, x, y, w, h)
  if thing.big and thing.fa then
    ui.thing(thing, root, x, y - h * 0.4, w, h * 1.8, { max_size = 128 })
  else
    ui.thing(thing, root, x, y, w, h)
  end
end

function E:draw()
  for i, b in ipairs(self.baskets) do draw_basket(self, b, i) end
  if not self.item or self.phase == "intro" then
    if self.phase == "intro" then
      ui.speaker(314, 259, 84, self.t, ui.c.ink)
    end
    return
  end
  local c = CENTER
  for dir, b in pairs(self.by_dir) do
    local ax = dir == "left" and (b.x + b.w + c.x) / 2 or dir == "right" and (c.x + c.w + b.x) / 2 or 320
    local ay = dir == "up" and 180 or dir == "down" and 338 or c.y + c.h / 2
    if dir == "up" or dir == "down" then ax = c.x + c.w + 22 end
    ui.arrow(dir, ax, ay, 9, self.wrong[b] and ui.c.line or ui.c.soft)
  end
  if self.phase == "right" then return end -- the thing is in the basket now
  -- 0 = in the centre, 1 = in the basket
  local k = 0
  if self.phase == "drop" then k = math.min(1, self.t / DROP)
  elseif self.phase == "back" then k = 1 - math.min(1, self.t / BACK) end
  k = k * k * (3 - 2 * k)
  local x, y, w, h = c.x, c.y, c.w, c.h
  if self.into and k > 0 then
    local b = self.into
    local tw, th = w * 0.55, h * 0.55
    w, h = w + (tw - w) * k, h + (th - h) * k
    x = x + (b.x + b.w / 2 - tw / 2 - x) * k
    y = y + (b.y + b.h / 2 - th / 2 - y) * k
  end
  ui.card(x, y, w, h, { fill = ui.c.paper, border = ui.c.ink })
  if k < 0.05 then
    draw_big(self.item.thing, self.ctx.root, x + 6, y + 6, w - 12, h - 12)
  else
    ui.thing(self.item.thing, self.ctx.root, x + 4, y + 4, w - 8, h - 8)
  end
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
