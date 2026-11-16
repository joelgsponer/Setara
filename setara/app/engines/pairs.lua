-- Pairs: a memory game. Three to six pairs lie face down. The D-pad moves the
-- gold border, A turns a card. Every card says its pair's audio when turned.
-- Two cards of the same pair stay open; two others turn back after a moment,
-- with no punishment. Two children take turns: a match gives another go.
-- X and Y say the last heard audio again, slowly.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local g = love.graphics

local E = {}
E.__index = E

local GAP = 10

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.cards = {}
  self.total = 0
  -- With "draw" the round is a pool: each play lays out a different set.
  local pool = {}
  for _, item in ipairs(round.items or {}) do pool[#pool + 1] = item end
  if round.draw then Quiz.shuffle(pool) end
  local most = math.min(6, tonumber(round.draw) or 6)
  for p, item in ipairs(pool) do
    if p <= most and type(item.a) == "table" and type(item.b) == "table" then
      self.total = self.total + 1
      self.cards[#self.cards + 1] = { pair = p, thing = item.a, audio = item.audio, flip = 1 }
      self.cards[#self.cards + 1] = { pair = p, thing = item.b, audio = item.audio, flip = 1 }
    end
  end
  Quiz.shuffle(self.cards)
  self.found, self.tries, self.first = 0, 0, 0
  self.score = { 0, 0 }
  self.spoiled = {}     -- pairs missed although both cards had been seen
  self.open = {}        -- the cards turned in this try
  self.cur = 1
  self.phase, self.t = "wait", 0
  self:layout()
  return self
end

function E:layout()
  local n = #self.cards
  local cols = n <= 6 and 3 or 4
  local rows = math.max(1, math.ceil(n / cols))
  local width = self.ctx.pair and 500 or 600
  local cw = math.min(160, (width - (cols - 1) * GAP) / cols)
  local ch = math.min(180, (424 - (rows - 1) * GAP) / rows)
  local top = 46 + (428 - (rows * ch + (rows - 1) * GAP)) / 2
  for i, c in ipairs(self.cards) do
    local row = math.floor((i - 1) / cols)
    local in_row = math.min(cols, n - row * cols)
    local x0 = (ui.W - (in_row * cw + (in_row - 1) * GAP)) / 2
    c.row = row
    c.x, c.y, c.w, c.h = x0 + ((i - 1) % cols) * (cw + GAP), top + row * (ch + GAP), cw, ch
  end
end

function E:start()
  self.phase, self.t = "play", 0
  if self.total == 0 then self.finished = true end
end

function E:again(slow)
  if self.last then self.ctx.say(self.last, { slow = slow }) end
end

function E:help() self:again(true) end

local function move(self, b)
  local c = self.cards[self.cur]
  local to
  if b == "left" or b == "right" then
    local o = self.cards[self.cur + (b == "left" and -1 or 1)]
    if o and o.row == c.row then to = self.cur + (b == "left" and -1 or 1) end
  else
    -- the last row may be shorter: go to the nearest card of the next row
    local row, best = c.row + (b == "up" and -1 or 1), nil
    for i, o in ipairs(self.cards) do
      if o.row == row then
        local d = math.abs(o.x - c.x)
        if not best or d < best then best, to = d, i end
      end
    end
  end
  if to then
    self.cur = to
    sfx.play("move")
  end
end

function E:close()
  for _, c in ipairs(self.open) do c.up, c.flip = false, 0 end
  self.open = {}
  self.phase, self.t = "play", 0
  sfx.play("flip")
  self.ctx.next_player()
end

function E:turn(c)
  if c.up then return end
  local known = c.seen
  c.up, c.flip, c.seen = true, 0, true
  self.open[#self.open + 1] = c
  if c.audio and #c.audio > 0 then
    self.last = c.audio
    self.ctx.say(c.audio)
  end
  if #self.open < 2 then
    sfx.play("flip")
    return
  end
  local a = self.open[1]
  self.tries = self.tries + 1
  if a.pair == c.pair then
    a.matched, c.matched = self.t_all, self.t_all
    self.open = {}
    self.found = self.found + 1
    if not self.spoiled[c.pair] then self.first = self.first + 1 end
    local p = self.ctx.player or 1
    self.score[p] = (self.score[p] or 0) + 1
    sfx.play("right")
    if self.found >= self.total then self.phase, self.t = "done", 0 end
  else
    sfx.play("flip")
    -- the partner of a turned card was already known: this pair was not
    -- found at the first chance
    for _, o in ipairs(self.cards) do
      if o ~= a and o ~= c and o.seen and (o.pair == a.pair or (o.pair == c.pair and known)) then
        self.spoiled[o.pair] = true
      end
    end
    self.phase, self.t = "miss", 0
  end
end

function E:input(b)
  if self.phase == "miss" then
    if b == "a" and self.t > 0.2 then self:close() end
    if b == "a" then return end
  end
  if self.phase ~= "play" and self.phase ~= "miss" then return end
  if b == "a" then
    local c = self.cards[self.cur]
    if c then self:turn(c) end
  elseif b == "up" or b == "down" or b == "left" or b == "right" then
    move(self, b)
  end
end

E.t_all = 0

function E:update(dt)
  self.t = self.t + dt
  self.t_all = self.t_all + dt
  for _, c in ipairs(self.cards) do
    if c.flip < 1 then c.flip = math.min(1, c.flip + dt * 6) end
  end
  if self.phase == "miss" and self.t > 1.1 then
    self:close()
  elseif self.phase == "done" and self.t > 1.3 and not audio.busy() then
    self.finished = true
  elseif self.phase == "done" and self.t > 6 then
    self.finished = true
  end
end

-- Drawing ---------------------------------------------------------------------

local function draw_back(x, y, w, h, color)
  ui.card(x, y, w, h, { fill = ui.mix(color, ui.c.white, 0.25) })
  ui.set(ui.c.paper, 0.9)
  g.setLineWidth(3)
  g.rectangle("line", x + 9, y + 9, w - 18, h - 18, 8, 8)
  g.setLineWidth(1)
  local cx, cy, r = x + w / 2, y + h / 2, math.min(w, h) * 0.24
  g.polygon("fill", cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy)
  ui.set(color)
  g.circle("fill", cx, cy, r * 0.38)
  ui.set(ui.c.paper, 0.9)
  for i = 0, 3 do
    local dx, dy = (i % 2 == 0 and -1 or 1) * (w / 2 - 24), (i < 2 and -1 or 1) * (h / 2 - 24)
    g.circle("fill", cx + dx, cy + dy, 5)
  end
end

local function sparkle(cx, cy, age)
  if age > 0.8 then return end
  local r = 20 + age * 70
  ui.set(ui.c.gold, 1 - age / 0.8)
  for i = 0, 7 do
    local a = i * math.pi / 4 + age * 2
    g.circle("fill", cx + math.cos(a) * r, cy + math.sin(a) * r, 6 - age * 5)
  end
end

function E:draw()
  local color = ui.c[self.ctx.pack and self.ctx.pack.subject or "fa"] or ui.c.fa
  local talking = audio.busy()
  for i, c in ipairs(self.cards) do
    -- a turning card gets narrow, then wide again with its other side
    local s = math.abs(math.cos(c.flip * math.pi))
    local face = c.up
    if c.flip < 0.5 then face = not face end
    local w = math.max(4, c.w * s)
    local x = c.x + (c.w - w) / 2
    if not face then
      draw_back(x, c.y, w, c.h, color)
    else
      local opts = {}
      if c.matched then opts.fill, opts.border, opts.width = ui.mix(ui.c.paper, ui.c.good, 0.25), ui.c.good, 5 end
      ui.card(x, c.y, w, c.h, opts)
      if s > 0.6 then
        local live = talking and self.last == c.audio and not c.matched
        ui.thing(c.thing, self.ctx.root, x + 6, c.y + 6, w - 12, c.h - 12, { t = live and self.t_all or nil })
      end
    end
    if i == self.cur and self.phase ~= "done" then
      ui.set(ui.c.gold)
      g.setLineWidth(6)
      g.rectangle("line", c.x - 3, c.y - 3, c.w + 6, c.h + 6, 16, 16)
      g.setLineWidth(1)
    end
  end
  for _, c in ipairs(self.cards) do
    if c.matched then sparkle(c.x + c.w / 2, c.y + c.h / 2, self.t_all - c.matched) end
  end

  if self.ctx.pair then
    -- each child's pairs, as dots under their number
    for p = 1, 2 do
      local cx = p == 1 and 606 or 34
      local on = (self.ctx.player or 1) == p
      ui.set(on and color or ui.c.line)
      g.circle("fill", cx, 80, on and 22 or 17)
      ui.set(ui.c.white)
      text.centered("bold", tostring(p), cx - 16, 64, 32, 32, 24)
      for k = 1, self.score[p] or 0 do
        ui.star(cx, 96 + k * 34, 13, true)
      end
    end
  end
end

function E:stars()
  if self.tries <= self.total * 2 then return 3 end
  if self.tries <= self.total * 3 then return 2 end
  return 1
end

function E:counts() return self.tries, self.first end
function E:progress() return self.found, self.total end

return E
