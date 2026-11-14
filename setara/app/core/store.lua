-- Everything the device remembers: two small JSON files in data/.
--
--   progress.json  one shared record: stars per round, last place, settings
--   stats.json     anonymous counts. No names, nothing finer than the week.
--
-- Each file is written twice (file and .bak). A damaged file falls back to
-- its backup, then to empty: it resets only that file, never the device.
local json = require("core.json")
local M = {}

local DIR = "data"

-- Reads the file, or its backup. A file that reads well refreshes the
-- backup, so the backup is always an older state that was known to be good,
-- never written in the same instant as the file itself.
local function read(name)
  local path = DIR .. "/" .. name
  local raw = love.filesystem.read(path)
  local data = raw and json.decode(raw)
  if type(data) == "table" then
    if love.filesystem.read(path .. ".bak") ~= raw then love.filesystem.write(path .. ".bak", raw) end
    return data
  end
  raw = love.filesystem.read(path .. ".bak")
  data = raw and json.decode(raw)
  if type(data) == "table" then return data end
  return nil
end

-- Writes to a new file first and then swaps it in, so a power cut leaves
-- either the old state or the new one, not half of each.
local function write(name, data)
  local raw = json.encode(data)
  love.filesystem.createDirectory(DIR)
  local path = DIR .. "/" .. name
  if love.filesystem.write(path .. ".tmp", raw) then
    local real = love.filesystem.getSaveDirectory() .. "/" .. path
    if os.rename(real .. ".tmp", real) then return true end
    love.filesystem.remove(path .. ".tmp")
  end
  return love.filesystem.write(path, raw) -- where the swap is not possible
end

local function random_id()
  local t = {}
  for i = 1, 8 do t[i] = string.format("%x", love.math.random(0, 15)) end
  return table.concat(t)
end

function M.load()
  M.progress = read("progress.json") or {}
  local p = M.progress
  p.stars = type(p.stars) == "table" and p.stars or {}
  p.settings = type(p.settings) == "table" and p.settings or {}
  p.settings.volume = tonumber(p.settings.volume) or 0.9
  p.settings.class_size = tonumber(p.settings.class_size) or 30
  p.settings.brightness = tonumber(p.settings.brightness) or 1
  p.level = type(p.level) == "table" and p.level or {}

  M.stats = read("stats.json") or {}
  local s = M.stats
  s.device = type(s.device) == "string" and s.device or nil
  s.rounds = type(s.rounds) == "table" and s.rounds or {}
  s.weeks = type(s.weeks) == "table" and s.weeks or {}
  s.checks = type(s.checks) == "table" and s.checks or {}
  s.teacher = type(s.teacher) == "table" and s.teacher or {}
  s.log = type(s.log) == "table" and s.log or {}
end

-- Called once the random seed is set: gives a new device its random id.
function M.ensure_device()
  if not M.stats.device then
    M.stats.device = random_id()
    M.save_stats()
  end
end

function M.save_progress() return write("progress.json", M.progress) end
function M.save_stats() return write("stats.json", M.stats) end

function M.save()
  M.save_progress()
  M.save_stats()
end

-- Stars ------------------------------------------------------------------------

function M.stars(round_id) return M.progress.stars[round_id] or 0 end

function M.set_stars(round_id, stars)
  if stars > M.stars(round_id) then M.progress.stars[round_id] = stars end
end

function M.total_stars(prefix)
  local n = 0
  for id, s in pairs(M.progress.stars) do
    if not prefix or id:sub(1, #prefix) == prefix then n = n + s end
  end
  return n
end

-- Anonymous counts ---------------------------------------------------------------

local function week()
  return os.date("%G-W%V")
end

-- minutes of use, per week and per kind ("en", "fa", "math", "garden", "teacher")
function M.add_minutes(kind, seconds)
  local w = M.stats.weeks[week()] or {}
  M.stats.weeks[week()] = w
  w[kind] = (w[kind] or 0) + seconds / 60
end

function M.count_round(round_id, attempts, correct, seconds, stars)
  local r = M.stats.rounds[round_id] or { plays = 0, attempts = 0, correct = 0, minutes = 0, stars = 0 }
  M.stats.rounds[round_id] = r
  r.plays = r.plays + 1
  r.attempts = r.attempts + attempts
  r.correct = r.correct + correct
  r.minutes = r.minutes + seconds / 60
  r.stars = r.stars + stars
end

-- Quick Check: how many hands were right, out of the class size.
function M.count_check(lesson_id, right, size)
  local c = M.stats.checks[lesson_id] or { times = 0, right = 0, size = 0 }
  M.stats.checks[lesson_id] = c
  c.times = c.times + 1
  c.right = c.right + right
  c.size = c.size + size
end

function M.count_teacher(key, n)
  M.stats.teacher[key] = (M.stats.teacher[key] or 0) + (n or 1)
end

-- App version and a short code, for "what breaks?". Keeps the last 30.
function M.log(code)
  local l = M.stats.log
  l[#l + 1] = { v = require("version"), code = tostring(code):sub(1, 120), week = week() }
  while #l > 30 do table.remove(l, 1) end
end

return M
