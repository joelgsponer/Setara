-- Builder: put the tiles in the right order (letters of a word, words of a
-- sentence, steps of handwashing, numbers on a carpet).
--
-- Top: a row of empty places, one per tile of the answer; Dari answers fill
-- from the right. Bottom: the tray with all tiles, shuffled. The D-pad moves
-- the gold cursor over the tray, A puts the chosen tile into the next empty
-- place if it belongs there; a wrong tile shakes and stays. When the row is
-- full it waves, the answer is spoken and the next item comes.
local ui = require("core.ui")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")

local E = {}
E.__index = E

local GAP = 8
local FLY = 0.2

local function has(list) return type(list) == "table" and #list > 0 end
local function key(thing)
  if type(thing) ~= "table" then return thing end
  return thing.id or thing.t or thing.fa or thing.img
end
local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- Boxes for one row of n tiles, centred on the screen.
local function row(n, y, max_w, max_h)
  local w = math.min(max_w, math.floor((ui.W - 20 - (n - 1) * GAP) / n))
  local h = clamp(w, 70, max_h)
  local x0 = (ui.W - (n * w + (n - 1) * GAP)) / 2
  local boxes = {}
  for i = 1, n do boxes[i] = { x = x0 + (i - 1) * (w + GAP), y = y, w = w, h = h } end
  return boxes
end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  local items = {}
  for _, it in ipairs(round.items or {}) do
    if has(it.tiles) then items[#items + 1] = it end
  end
  self.quiz = Quiz.new(items, { draw = round.draw })
  self.phase = "wait"
  self.t = 0
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
  local n = math.min(#item.tiles, 8)
  self.n = n
  -- places: number 1 is the first of the answer; rtl puts it on the right
  local boxes = row(n, 58, 130, 110)
  self.slots = {}
  for i = 1, n do self.slots[i] = boxes[item.rtl and (n + 1 - i) or i] end

  local things = {}
  for i = 1, n do things[#things + 1] = item.tiles[i] end
  for _, x in ipairs(item.extra or {}) do
    if #things < 8 then things[#things + 1] = x end
  end
  -- a tray that already shows the answer would give it away
  for _ = 1, 5 do
    Quiz.shuffle(things)
    local same = true
    for i = 1, n do
      if key(things[i]) ~= key(item.tiles[item.rtl and (n + 1 - i) or i]) then same = false end
    end
    if not same then break end
  end
  local m = #things
  local per = m <= 4 and m or math.ceil(m / 2)
  self.per = per
  self.tray = {}
  if m <= 4 then
    local b = row(m, 292, 130, 110)
    for i = 1, m do self.tray[i] = b[i] end
  else
    local top, bottom = row(per, 222, 130, 104), row(m - per, 348, 130, 104)
    for i = 1, per do self.tray[i] = top[i] end
    for i = 1, m - per do self.tray[per + i] = bottom[i] end
  end
  for i, box in ipairs(self.tray) do box.thing = things[i] end
  self.filled = 0
  self.cursor = 1
  self.fly, self.shake = nil, nil
  self.phase, self.t = "ask", 0
  self:again(false)
end

function E:again(slow)
  if self.item and self.phase == "ask" then self.ctx.say(self.item.prompt_audio, { slow = slow }) end
end

function E:help()
  if not self.item or self.phase ~= "ask" then return end
  if has(self.item.help_audio) then
    self.ctx.say(self.item.help_audio)
  else
    self:again(true)
  end
end

-- Next tile still in the tray, going through it in reading order.
function E:seek(from, step)
  local i = from + step
  while self.tray[i] do
    if not self.tray[i].placed then return i end
    i = i + step
  end
end

function E:move(b)
  local at
  if b == "left" then at = self:seek(self.cursor, -1)
  elseif b == "right" then at = self:seek(self.cursor, 1)
  elseif #self.tray > self.per then
    -- the other row: the free tile nearest to this column
    local up = self.cursor <= self.per
    if (b == "down") == up then
      local lo, hi = up and self.per + 1 or 1, up and #self.tray or self.per
      local cx = self.tray[self.cursor].x
      local best
      for i = lo, hi do
        local d = math.abs(self.tray[i].x - cx)
        if not self.tray[i].placed and (not best or d < best) then at, best = i, d end
      end
    end
  end
  if at then
    self.cursor = at
    sfx.play("move")
  end
end

function E:input(b)
  if self.phase ~= "ask" or not self.item then return end
  if b ~= "a" then return self:move(b) end
  local tile = self.tray[self.cursor]
  if not tile or tile.placed or self.fly then return end
  local want = self.item.tiles[self.filled + 1]
  if key(tile.thing) == key(want) then
    tile.placed = true
    self.filled = self.filled + 1
    self.fly = { from = tile, to = self.slots[self.filled], thing = tile.thing, t = 0 }
    self.slots[self.filled].thing = tile.thing
    sfx.play("hop")
    self.cursor = self:seek(self.cursor, 1) or self:seek(self.cursor, -1) or self.cursor
    if self.filled >= self.n then
      self.phase, self.t = "done", 0
      sfx.play("right")
      self.ctx.say(self.item.done_audio)
      self.quiz:right()
      self.ctx.next_player()
    end
  else
    self.shake, self.shake_t = tile, 0.4
    sfx.play("wrong")
    self.quiz:wrong()
  end
end

function E:update(dt)
  self.t = self.t + dt
  if self.shake_t then
    self.shake_t = self.shake_t - dt
    if self.shake_t <= 0 then self.shake, self.shake_t = nil, nil end
  end
  if self.fly then
    self.fly.t = self.fly.t + dt
    if self.fly.t >= FLY then self.fly = nil end
  end
  -- wait for the spoken answer, but never long
  if self.phase == "done" and self.t > 1.0 and (not audio.busy() or self.t > 4) then
    audio.stop()
    self:next()
  end
end

local function draw_tile(root, thing, x, y, w, h, opts)
  ui.card(x, y, w, h, opts)
  if type(thing) == "table" and thing.fa then
    -- the Dari font's line box is far taller than its letters: a taller
    -- box lets the letters be as large as the tile really allows
    ui.thing(thing, root, x + 3, y - h * 0.2, w - 6, h * 1.4, { max_size = 72 })
  else
    ui.thing(thing, root, x + 3, y + 3, w - 6, h - 6, { max_size = 56 })
  end
end

function E:draw()
  if not self.item then return end
  local root = self.ctx.root
  local flying = self.fly and self.fly.to
  for i, s in ipairs(self.slots) do
    local y = s.y
    if self.phase == "done" then
      -- a little wave runs along the row in building order
      local k = self.t * 7 - i * 0.7
      if k > 0 and k < math.pi then y = y - math.sin(k) * 14 end
    end
    if s.thing and s ~= flying then
      local done = self.phase == "done"
      draw_tile(root, s.thing, s.x, y, s.w, s.h, done and
        { fill = ui.mix(ui.c.paper, ui.c.good, 0.3), border = ui.c.good, width = 5 } or nil)
    else
      local nxt = i == self.filled + 1
      ui.card(s.x, y, s.w, s.h, { fill = ui.c.shade, border = nxt and ui.c.soft or ui.c.line, width = nxt and 4 or 3 })
      if nxt then
        ui.set(ui.c.soft, 0.5 + 0.4 * math.sin(self.t * 5))
        love.graphics.circle("fill", s.x + s.w / 2, s.y + s.h / 2, 7)
      end
    end
  end
  -- which way the row is built
  local first, last = self.slots[1], self.slots[self.n]
  if first and last and self.phase == "ask" then
    local dir = self.item.rtl and "left" or "right"
    ui.arrow(dir, 320, 190, 9, ui.c.line)
  end

  for i, tile in ipairs(self.tray) do
    if not tile.placed then
      local x = tile.x
      if self.shake == tile then x = x + math.sin(self.t * 50) * 6 end
      local sel = i == self.cursor and self.phase == "ask"
      draw_tile(root, tile.thing, x, tile.y, tile.w, tile.h, { selected = sel })
      if sel then ui.badge("a", x + tile.w - 6, tile.y + tile.h - 4, 13) end
    end
  end

  if self.fly then
    local f = self.fly
    local k = math.min(1, f.t / FLY)
    k = k * k * (3 - 2 * k)
    local a, b = f.from, f.to
    draw_tile(root, f.thing, a.x + (b.x - a.x) * k, a.y + (b.y - a.y) * k,
      a.w + (b.w - a.w) * k, a.h + (b.h - a.h) * k)
  end
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
