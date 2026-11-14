-- Class Games: play for the whole class with one device. Row quiz, Listen
-- and Do, picture bingo caller, number caller, mental-math caller.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local packs = require("core.packs")
local Quiz = require("core.quiz")
local T = require("teacher.common")
local g = love.graphics

local Games = {}
Games.__index = Games

local LIST = { "game_quiz", "game_do", "game_bingo", "game_numbers", "game_math" }

function Games.new()
  return setmetatable({ t = 0, sel = 1, mode = nil }, Games)
end

function Games:leave() T.stop() end
function Games:update(dt) self.t = self.t + dt end

-- Lines of one kind from every lesson up to today's.
local function lines_so_far(kinds)
  local out, seen = {}, {}
  for n = 1, T.lesson_number() or 0 do
    local lesson = T.load_lesson(n)
    if lesson then
      for _, kind in ipairs(kinds) do
        for _, line in ipairs(T.lines(lesson, kind)) do
          if line.text and #line.audio > 0 and not seen[line.text] then
            seen[line.text] = true
            out[#out + 1] = line
          end
        end
      end
    end
  end
  return Quiz.shuffle(out)
end

local function number_clip(n) return packs.string("num_" .. n) end

function Games:start(mode)
  self.mode, self.i, self.item, self.reveal = mode, 0, nil, false
  if mode == "game_quiz" then
    self.pool = lines_so_far({ "check", "drill" })
    self.teams, self.team, self.score = 3, 1, { 0, 0, 0, 0 }
  elseif mode == "game_do" then
    self.pool = lines_so_far({ "command" })
  elseif mode == "game_bingo" then
    self.pool, self.called = {}, {}
    local tp = T.pack()
    local pack = tp and packs.subjects.en and packs.subjects.en[tp.level or 1]
    local seen = {}
    for _, e in ipairs(pack and packs.review(pack) or {}) do
      local thing = e.choices and e.choices[1]
      if thing and thing.img and not thing.n and not seen[e.answer] then
        seen[e.answer] = true
        self.pool[#self.pool + 1] = { thing = thing, audio = packs.clips(pack, e.prompt_audio), root = pack.root }
      end
    end
    Quiz.shuffle(self.pool)
  elseif mode == "game_numbers" or mode == "game_math" then
    self.max = 10
  end
  self:next()
end

function Games:next()
  local mode = self.mode
  self.reveal = false
  if mode == "game_numbers" then
    local n
    repeat n = love.math.random(1, self.max) until n ~= (self.item and self.item.n)
    self.item = { n = n }
    audio.say(number_clip(n).audio)
  elseif mode == "game_math" then
    local a, b, plus
    plus = love.math.random(2) == 1
    if plus then
      a = love.math.random(0, self.max - 1)
      b = love.math.random(1, self.max - a)
    else
      a = love.math.random(1, self.max)
      b = love.math.random(0, a)
    end
    self.item = { a = a, b = b, plus = plus, answer = plus and a + b or a - b }
    self:say_sum(false)
  else
    if #self.pool == 0 then self.item = nil return end
    self.i = self.i % #self.pool + 1
    self.item = self.pool[self.i]
    if mode == "game_bingo" then
      self.called[#self.called + 1] = self.item
      if #self.called > 8 then table.remove(self.called, 1) end
    end
    audio.say(self.item.audio)
  end
end

function Games:say_sum(slow)
  local it = self.item
  local clips = {}
  for _, key in ipairs({ "num_" .. it.a, it.plus and "math_plus" or "math_minus", "num_" .. it.b }) do
    for _, c in ipairs(packs.string(key).audio or {}) do clips[#clips + 1] = c end
  end
  audio.say(clips, { slow = slow, gap = 0.1 })
end

function Games:input(b)
  if not self.mode then
    if b == "b" then app.pop()
    elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
    elseif b == "down" and self.sel < #LIST then self.sel = self.sel + 1 sfx.play("move")
    elseif b == "a" then self:start(LIST[self.sel]) end
    return
  end
  local mode, it = self.mode, self.item
  if b == "b" then
    T.stop()
    self.mode = nil
    return
  end
  if not it then return end
  if mode == "game_quiz" then
    if b == "a" then self:next()
    elseif b == "x" then audio.say(it.audio, { slow = true })
    elseif b == "y" then self.reveal = true audio.say(it.meaning_audio)
    elseif b == "left" then self.team = (self.team - 2) % self.teams + 1 sfx.play("move")
    elseif b == "right" then self.team = self.team % self.teams + 1 sfx.play("move")
    elseif b == "up" then self.score[self.team] = self.score[self.team] + 1 sfx.play("star")
    elseif b == "down" then self.score[self.team] = math.max(0, self.score[self.team] - 1) sfx.play("move")
    elseif b == "l" then self.teams = math.max(2, self.teams - 1) self.team = math.min(self.team, self.teams)
    elseif b == "r" then self.teams = math.min(4, self.teams + 1) end
  elseif mode == "game_do" or mode == "game_bingo" then
    if b == "a" then self:next()
    elseif b == "x" then audio.say(it.audio, { slow = true })
    elseif b == "y" then self.reveal = true if it.meaning_audio then audio.say(it.meaning_audio) end end
  else
    if b == "left" or b == "right" then
      self.max = self.max == 10 and 20 or 10
      sfx.play("flip")
      self:next()
    elseif mode == "game_numbers" then
      if b == "a" then self:next()
      elseif b == "x" then audio.say(number_clip(it.n).audio, { slow = true }) end
    else
      if b == "a" then
        if self.reveal then self:next()
        else
          self.reveal = true
          sfx.play("right")
          audio.say(number_clip(it.answer).audio)
        end
      elseif b == "x" then self:say_sum(true) end
    end
  end
end

function Games:draw()
  T.header("tool_games")
  if not self.mode then
    for i, key in ipairs(LIST) do
      local y = 56 + (i - 1) * 74
      ui.card(60, y, 520, 66, { selected = i == self.sel, fill = i == self.sel and ui.c.shade or ui.c.paper })
      ui.set(ui.c.ink)
      local s = T.S(key)
      text.print(s.en or "", 80, y + 18, 240, "left", 24, true)
      if s.fa then text.fa(s.fa, 300, y + 6, 264, 30, "right", true) end
    end
    return
  end
  local mode, it = self.mode, self.item
  local title = T.S(mode)
  ui.set(ui.c.ink)
  if title.fa then text.fa(title.fa, 300, 46, 326, 24, "right", true) end
  if not it then return end
  if mode == "game_quiz" or mode == "game_do" then
    ui.card(14, 84, 612, 110, { fill = ui.c.shade, border = ui.c.line })
    T.english((it.text or ""):gsub("\n", " "), 22, 100, 596, self.t, audio.busy())
    if self.reveal and it.meaning_fa then T.dari_card(it.meaning_fa, 14, 202, 612, 24, ui.mix(ui.c.paper, ui.c.gold, 0.2)) end
    if mode == "game_quiz" then
      -- one column per row of the classroom; the teacher gives the points
      local w = 600 / self.teams
      for k = 1, self.teams do
        local x = 20 + (k - 1) * w
        ui.card(x, 262, w - 8, 170, { selected = k == self.team })
        ui.set(ui.c.soft)
        local s = T.S("game_team")
        if text.locale == "en" then
          text.print((s.en or "") .. " " .. k, x + 10, 268, w - 16, "left", 16)
        elseif s.fa then
          text.fa(s.fa[1] .. " " .. k, x, 264, w - 16, 24, "right")
        end
        ui.set(ui.c.teacher)
        text.centered("bold", tostring(self.score[k]), x, 300, w - 8, 120, 72)
      end
      T.hints({ { "a", "hint_next" }, { "updown", "hint_point" }, { "y", "hint_meaning" } })
    else
      ui.guide(320, 330, 2, audio.busy() and "talk" or "idle", self.t)
      T.hints({ { "a", "hint_next" }, { "x", "hint_slow" }, { "y", "hint_meaning" } })
    end
  elseif mode == "game_bingo" then
    ui.card(200, 76, 240, 240)
    ui.thing(it.thing, it.root, 210, 86, 220, 220)
    -- the pictures called so far, newest on the right
    for k, c in ipairs(self.called) do
      local x = 20 + (k - 1) * 76
      ui.card(x, 334, 70, 70, { border = ui.c.line, radius = 8 })
      ui.thing(c.thing, c.root, x + 3, 337, 64, 64)
    end
    T.hints({ { "a", "hint_next" }, { "x", "hint_slow" } })
  elseif mode == "game_numbers" then
    ui.card(190, 90, 260, 220, { border = ui.c.teacher, width = 4 })
    ui.set(ui.c.teacher)
    text.centered("bold", tostring(it.n), 190, 90, 260, 220, 128)
    ui.set(ui.c.soft)
    text.print("1 – " .. self.max, 0, 330, 640, "center", 24, true)
    T.hints({ { "a", "hint_next" }, { "x", "hint_slow" } })
  elseif mode == "game_math" then
    ui.card(60, 100, 520, 200, { border = ui.c.teacher, width = 4 })
    ui.set(ui.c.ink)
    local sum = it.a .. (it.plus and " + " or " − ") .. it.b .. " = " .. (self.reveal and it.answer or "?")
    text.centered("bold", sum, 60, 100, 520, 200, 96)
    ui.set(ui.c.soft)
    text.print("0 – " .. self.max, 0, 320, 640, "center", 24, true)
    T.hints({ { "a", "hint_next" }, { "x", "hint_slow" } })
  end
end

return Games
