-- Speech playback. A "clip list" is a list of file paths played one after the
-- other. Starting new speech stops the old one; a stopped speech never calls
-- its on_done.
local M = {}

local current
local pending = {}
local volume = 1

local function exists(path)
  return love.filesystem.getInfo(path, "file") ~= nil
end

function M.set_volume(v)
  volume = math.max(0, math.min(1, v))
  love.audio.setVolume(volume)
end

function M.get_volume() return volume end

-- The slow variant of a clip sits next to it as <name>.slow.ogg.
local function resolve(clips, slow)
  local list = {}
  for _, c in ipairs(clips or {}) do
    local p = c
    if slow then
      local s = c:gsub("%.ogg$", ".slow.ogg")
      if exists(s) then p = s end
    end
    if exists(p) then list[#list + 1] = p end
  end
  return list
end

function M.stop()
  if current and current.source then current.source:stop() end
  current = nil
end

-- opts: slow, on_done, gap (seconds between clips), after (seconds of
-- silence before on_done).
function M.say(clips, opts)
  opts = opts or {}
  M.stop()
  current = {
    list = resolve(clips, opts.slow), i = 0, t = 0, dur = 0,
    on_done = opts.on_done, gap = opts.gap or 0.25, after = opts.after or 0,
  }
end

function M.busy() return current ~= nil end

-- Total length in seconds of a clip list (0 when nothing can be played).
function M.duration(clips, slow)
  local total = 0
  for _, p in ipairs(resolve(clips, slow)) do
    local ok, src = pcall(love.audio.newSource, p, "static")
    if ok then total = total + math.max(0, src:getDuration()) end
  end
  return total
end

function M.update(dt)
  for i = 1, #pending do pending[i]() end
  pending = {}
  local c = current
  if not c then return end
  c.t = c.t + dt
  if c.t < c.dur then return end
  c.i = c.i + 1
  local path = c.list[c.i]
  if path then
    local ok, src = pcall(love.audio.newSource, path, "static")
    if ok then
      c.source = src
      src:play()
      c.t = 0
      c.dur = math.max(0.1, src:getDuration()) + (c.i < #c.list and c.gap or c.after)
    else
      c.t, c.dur = 0, 0 -- a damaged clip is skipped
    end
  else
    current = nil
    if c.on_done then pending[#pending + 1] = c.on_done end
  end
end

return M
