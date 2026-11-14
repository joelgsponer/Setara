-- Shared pieces of teacher mode: the current lesson, headers, hint bars.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local store = require("core.store")
local packs = require("core.packs")
local g = love.graphics

local M = {}
local cache = {} -- lesson id -> loaded lesson

M.STEPS = { "hello", "listen", "say", "do", "play", "goodbye" }
M.MINUTES = { hello = 3, listen = 5, say = 8, ["do"] = 8, play = 8, goodbye = 3 }

function M.S(key) return packs.string(key) end

-- The teacher pack in use: the one the teacher last worked in, else the
-- lowest level installed. Packs follow each other: after the last lesson of
-- English 1 comes the first of English 2.
local function pack_index()
  local want = store.progress.teacher_pack
  for i, p in ipairs(packs.teacher) do
    if p.pack == want then return i end
  end
  return 1
end

function M.pack() return packs.teacher[pack_index()] end
function M.pack_count() return #packs.teacher end

local function lessons_of(pack)
  return pack and type(pack.lessons) == "table" and #pack.lessons or 0
end

local function remembered(pack)
  local per = store.progress.teacher_lessons
  local n = type(per) == "table" and tonumber(per[pack.pack])
  -- before there could be two packs, one number was kept for the only one
  if not n and pack == packs.teacher[1] then n = tonumber(store.progress.teacher_lesson) end
  return n or 1
end

-- The lesson number the teacher is on. Remembered on the device, per pack.
function M.lesson_number()
  local pack = M.pack()
  if lessons_of(pack) == 0 then return nil end
  return math.max(1, math.min(#pack.lessons, remembered(pack)))
end

function M.set_lesson(n)
  local i = pack_index()
  local pack = packs.teacher[i]
  if not pack then return end
  if n > lessons_of(pack) and lessons_of(packs.teacher[i + 1]) > 0 then
    pack, n = packs.teacher[i + 1], 1
  elseif n < 1 and lessons_of(packs.teacher[i - 1]) > 0 then
    pack = packs.teacher[i - 1]
    n = #pack.lessons
  end
  n = math.max(1, math.min(math.max(1, lessons_of(pack)), n))
  if type(store.progress.teacher_lessons) ~= "table" then store.progress.teacher_lessons = {} end
  store.progress.teacher_lessons[pack.pack] = n
  store.progress.teacher_pack = pack.pack
  if pack == packs.teacher[1] then store.progress.teacher_lesson = n end
end

-- How far the teacher has prepared in this pack (Tonight's Preview).
function M.course_reached()
  local pack = M.pack()
  if not pack then return 0 end
  local key = pack == packs.teacher[1] and "course_lesson" or ("course_lesson_" .. tostring(pack.pack))
  return store.stats.teacher[key] or 0, key
end

function M.lesson_info(n)
  local pack = M.pack()
  return pack and type(pack.lessons) == "table" and pack.lessons[n or M.lesson_number() or 1] or nil
end

-- Load a lesson file. Clip lists become full paths.
function M.load_lesson(n)
  local pack, info = M.pack(), M.lesson_info(n)
  if not pack or not info then return nil end
  if cache[info.id] then return cache[info.id] end
  local lesson = packs.read(pack, "lessons/" .. tostring(info.id) .. ".json")
  if type(lesson) ~= "table" or type(lesson.steps) ~= "table" then return nil end
  -- Keep only steps that can be shown: a known name and at least one line.
  local steps = {}
  for _, step in ipairs(lesson.steps) do
    if type(step) == "table" and M.MINUTES[step.step] and type(step.lines) == "table" and #step.lines > 0 then
      for _, line in ipairs(step.lines) do
        line.kind = line.kind or "line"
        line.teacher_fa = line.teacher_fa or {}
        line.audio = packs.clips(pack, line.audio)
        line.meaning_audio = packs.clips(pack, line.meaning_audio)
        line.answer_audio = packs.clips(pack, line.answer_audio)
      end
      steps[#steps + 1] = step
    end
  end
  if #steps == 0 then return nil end
  lesson.steps = steps
  lesson.n = lesson.n or info.n or 0
  cache[info.id] = lesson
  return lesson
end

-- All lines of a kind, in lesson order.
function M.lines(lesson, kind)
  local out = {}
  for _, step in ipairs(lesson.steps) do
    for _, line in ipairs(step.lines or {}) do
      if line.kind == kind then out[#out + 1] = line end
    end
  end
  return out
end

function M.header(title_key, extra)
  ui.background(ui.mix(ui.c.bg, ui.c.teacher, 0.1))
  local s = M.S(title_key)
  ui.header(ui.c.teacher, extra or s.en, s.fa)
end

-- Bottom bar: a list of { button, string key } pairs, right to left.
function M.hints(list)
  ui.set(ui.c.paper)
  g.rectangle("fill", 0, 444, ui.W, 36)
  ui.set(ui.c.line)
  g.rectangle("fill", 0, 443, ui.W, 2)
  local x = ui.W - 10
  for _, h in ipairs(list) do
    local s = M.S(h[2])
    local label = s.fa and s.fa[1] or s.en or ""
    local english = text.locale == "en" and s.en
    local w = english and text.font("latin", 16):getWidth(s.en) or text.font("fa", 20):getWidth(label)
    ui.set(ui.c.ink)
    if english then text.print(s.en, x - w, 452, w + 4, "left", 16) else text.fa(label, x - w, 444, w, 20, "left") end
    x = x - w - 8
    if h[1] == "arrows" then
      ui.arrow("left", x - 26, 462, 7, ui.c.ink)
      ui.arrow("right", x - 8, 462, 7, ui.c.ink)
      x = x - 46
    elseif h[1] == "updown" then
      ui.arrow("up", x - 10, 455, 6, ui.c.ink)
      ui.arrow("down", x - 10, 469, 6, ui.c.ink)
      x = x - 30
    else
      ui.badge(h[1], x - 14, 462, 13)
      x = x - 40
    end
  end
end

-- A Dari paragraph inside a card. Returns the card's height.
function M.dari_card(lines, x, y, w, size, fill)
  local h = text.fa_height(lines, size or 30, w - 24) + 16
  ui.card(x, y, w, h, { fill = fill or ui.c.paper, border = ui.c.line })
  ui.set(ui.c.ink)
  text.fa(lines, x + 12, y + 6, w - 24, size or 30)
  return h
end

-- The English line: big, with a speaker that moves while it plays.
function M.english(str, x, y, w, t, playing)
  ui.speaker(x + 26, y + 26, 40, playing and t or nil, ui.c.teacher)
  ui.set(ui.c.ink)
  local size = #str > 60 and 24 or 30
  return math.max(52, text.print(str, x + 60, y + 4, w - 60, "left", size, true))
end

function M.timer(seconds)
  return string.format("%d:%02d", math.floor(seconds / 60), math.floor(seconds % 60))
end

function M.stop()
  audio.stop()
  require("core.sfx").stop_loop()
end

return M
