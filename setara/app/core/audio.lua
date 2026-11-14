-- Speech playback. A "clip list" is a list of file paths played one after the
-- other. Starting new speech stops the old one; a stopped speech never calls
-- its on_done.
local M = {}

local current
local pending = {}
local volume = 1
local paused = false
local lengths = {}

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

-- Stopped speech never calls its on_done, not even one that ended this frame.
function M.stop()
  if current and current.source then current.source:stop() end
  current = nil
  pending = {}
  paused = false
end

-- The pause menu holds the speech and lets it carry on afterwards, so a
-- screen that waits for the end of a sentence is never left waiting.
function M.pause()
  if current and not paused then
    paused = true
    if current.source then current.source:pause() end
  end
end

function M.resume()
  if paused then
    paused = false
    if current and current.source then current.source:play() end
  end
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
    if not lengths[p] then
      -- a stream source knows its length without decoding the whole clip
      local ok, src = pcall(love.audio.newSource, p, "stream")
      lengths[p] = ok and math.max(0, src:getDuration()) or 0
      if ok then src:release() end
    end
    total = total + lengths[p]
  end
  return total
end

function M.update(dt)
  for i = 1, #pending do pending[i]() end
  pending = {}
  local c = current
  if not c or paused then return end
  c.t = c.t + dt
  if c.t < c.dur then return end
  c.i = c.i + 1
  local path = c.list[c.i]
  if path then
    if c.source then c.source:release() end
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
