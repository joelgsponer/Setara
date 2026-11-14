-- Content packs: finding, checking, installing and reading them.
--
-- In the save directory:
--   packs/<id>.v<version>.zip   installed packs
--   update/*.zip                new packs dropped onto the card
--
-- At start every zip in update/ is checked file by file against the
-- checksums in its manifest. A good pack is copied into packs/ under a new
-- name, so the old one is still there if power is cut half way. A damaged
-- pack is ignored and removed, and the old one stays.
local json = require("core.json")
local store = require("core.store")
local M = {}

M.FORMAT = 1
M.list = {}      -- id -> pack
M.subjects = {}  -- subject -> level -> pack
M.teacher = {}   -- list of teacher packs
M.core = nil

local function hexhash(data)
  return love.data.encode("string", "hex", love.data.hash("sha256", data))
end

local function read_json(path)
  local raw = love.filesystem.read(path)
  if not raw then return nil, "missing " .. path end
  return json.decode(raw)
end

local function zips(dir)
  local out = {}
  for _, name in ipairs(love.filesystem.getDirectoryItems(dir)) do
    if name:match("%.zip$") then out[#out + 1] = name end
  end
  table.sort(out)
  return out
end

-- Check every file of a mounted pack. Yields now and then so the screen can
-- show progress. Returns the manifest or nil and a reason.
local function verify(root, tick)
  local manifest, err = read_json(root .. "manifest.json")
  if type(manifest) ~= "table" then return nil, "manifest: " .. tostring(err) end
  if manifest.format ~= M.FORMAT then return nil, "format " .. tostring(manifest.format) end
  if type(manifest.pack) ~= "string" or type(manifest.files) ~= "table" then return nil, "manifest fields" end
  local n = 0
  for path, want in pairs(manifest.files) do
    local data = love.filesystem.read(root .. path)
    if not data then return nil, "missing file " .. path end
    if "sha256:" .. hexhash(data) ~= want then return nil, "checksum " .. path end
    n = n + 1
    if tick and n % 20 == 0 then tick() end
  end
  return manifest
end

local function installed()
  local found = {} -- id -> list of {version, name}
  for _, name in ipairs(zips("packs")) do
    local id, ver = name:match("^(.-)%.v(%d+)%.zip$")
    if id then
      found[id] = found[id] or {}
      table.insert(found[id], { version = tonumber(ver), name = name })
    end
  end
  for _, versions in pairs(found) do
    table.sort(versions, function(a, b) return a.version > b.version end)
  end
  return found
end

-- Install everything waiting in update/. tick(message) is called between
-- steps. Returns counts.
function M.install_updates(tick)
  love.filesystem.createDirectory("packs")
  love.filesystem.createDirectory("update")
  local have = installed()
  local done, failed = 0, 0
  for _, name in ipairs(zips("update")) do
    local src = "update/" .. name
    local mount = "upd/"
    local manifest, err
    if love.filesystem.mount(src, mount) then
      manifest, err = verify(mount, tick)
      love.filesystem.unmount(src)
    else
      err = "not a zip"
    end
    if manifest then
      local id, ver = manifest.pack, tonumber(manifest.version) or 1
      local current = have[id] and have[id][1]
      if not current or ver >= current.version then
        local data = love.filesystem.read(src)
        local target = string.format("packs/%s.v%d.zip", id, ver)
        local ok = data and love.filesystem.write(target, data)
        -- Read the copy back: a full card or a bad sector must not leave a broken pack.
        if ok and love.filesystem.read(target) == data then
          done = done + 1
          have[id] = have[id] or {}
          table.insert(have[id], 1, { version = ver, name = target:sub(7) })
        else
          love.filesystem.remove(target)
          failed = failed + 1
          store.log("update copy failed " .. name)
        end
      end
    else
      failed = failed + 1
      store.log("update rejected " .. name .. ": " .. tostring(err))
    end
    love.filesystem.remove(src)
    if tick then tick() end
  end
  return done, failed
end

-- Mount the newest readable version of every installed pack.
function M.load()
  M.list, M.subjects, M.teacher, M.core = {}, {}, {}, nil
  love.filesystem.createDirectory("packs")
  for id, versions in pairs(installed()) do
    local loaded = false
    for _, v in ipairs(versions) do
      local path = "packs/" .. v.name
      if loaded then
        love.filesystem.remove(path) -- an older version that is no longer needed
      else
        local root = "p/" .. id .. "/"
        if love.filesystem.mount(path, root) then
          local manifest = read_json(root .. "manifest.json")
          if type(manifest) == "table" and manifest.format == M.FORMAT and manifest.pack == id then
            manifest.root = root
            M.list[id] = manifest
            loaded = true
          else
            love.filesystem.unmount(path)
            store.log("pack unreadable " .. v.name)
          end
        else
          store.log("pack not a zip " .. v.name)
        end
      end
    end
  end
  for _, p in pairs(M.list) do
    if p.kind == "core" then
      M.core = p
      p.strings = read_json(p.root .. (p.strings or "strings.json")) or {}
    elseif p.kind == "teacher" then
      M.teacher[#M.teacher + 1] = p
    elseif p.subject and p.level then
      M.subjects[p.subject] = M.subjects[p.subject] or {}
      M.subjects[p.subject][p.level] = p
    end
  end
  table.sort(M.teacher, function(a, b) return (a.level or 0) < (b.level or 0) end)
end

function M.count()
  local n = 0
  for _ in pairs(M.list) do n = n + 1 end
  return n
end

-- Levels available for a subject, ascending.
function M.levels(subject)
  local out = {}
  for level in pairs(M.subjects[subject] or {}) do out[#out + 1] = level end
  table.sort(out)
  return out
end

-- Full paths for a clip list of a pack.
function M.clips(pack, clips)
  local out = {}
  for i, c in ipairs(clips or {}) do out[i] = pack.root .. c end
  return out
end

function M.read(pack, path)
  return read_json(pack.root .. path)
end

function M.round(pack, id)
  local r, err = read_json(pack.root .. "levels/" .. id .. ".json")
  if type(r) ~= "table" or type(r.items) ~= "table" then return nil, err or "bad level file" end
  r.pack = pack
  return r
end

function M.review(pack)
  if pack._review == nil then
    pack._review = read_json(pack.root .. (pack.review or "review.json")) or false
  end
  return pack._review or {}
end

-- App strings from the core pack: s.fa (lines), s.en, s.audio (full paths).
function M.string(key)
  local s = M.core and M.core.strings[key]
  if not s then return { en = key } end
  if not s._full then
    s.audio = M.clips(M.core, s.audio)
    s._full = true
  end
  return s
end

return M
