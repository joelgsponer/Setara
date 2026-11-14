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
  -- ask first: in the browser build a failed read cannot be caught
  local raw = love.filesystem.getInfo(path, "file") and love.filesystem.read(path)
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

-- Is this manifest one the app can use? A pack must name itself sanely and
-- carry what its kind needs; an empty shell must never replace a good pack.
local function usable(manifest, root)
  if type(manifest) ~= "table" or manifest.format ~= M.FORMAT then return false, "format" end
  local id, ver = manifest.pack, manifest.version
  if type(id) ~= "string" or not id:match("^[a-z0-9][a-z0-9%-]*$") or #id > 40 then return false, "pack id" end
  if type(ver) ~= "number" or ver ~= math.floor(ver) or ver < 1 or ver > 999999 then return false, "version" end
  local function has(path) return type(path) == "string" and love.filesystem.getInfo(root .. path, "file") ~= nil end
  if manifest.kind == "core" then
    if not has(manifest.strings or "strings.json") then return false, "no strings" end
  elseif manifest.kind == "teacher" then
    if type(manifest.lessons) ~= "table" then return false, "no lessons" end
    for _, lesson in ipairs(manifest.lessons) do
      if type(lesson) ~= "table" or not has("lessons/" .. tostring(lesson.id) .. ".json") then return false, "lesson file" end
    end
  else
    if type(manifest.subject) ~= "string" or type(manifest.level) ~= "number" then return false, "subject or level" end
    if type(manifest.games) ~= "table" then return false, "no games" end
    for _, game in ipairs(manifest.games) do
      if type(game) ~= "table" or type(game.id) ~= "string" or type(game.rounds) ~= "table" then return false, "game" end
      for _, rid in ipairs(game.rounds) do
        if not has("levels/" .. tostring(rid) .. ".json") then return false, "level file" end
      end
    end
  end
  return true
end

-- Check every file of a mounted pack. Yields now and then so the screen can
-- show progress. Returns the manifest or nil and a reason.
local function verify(root, tick)
  local manifest, err = read_json(root .. "manifest.json")
  if type(manifest) ~= "table" then return nil, "manifest: " .. tostring(err) end
  if manifest.format ~= M.FORMAT then return nil, "format " .. tostring(manifest.format) end
  if type(manifest.files) ~= "table" or next(manifest.files) == nil then return nil, "no file list" end
  local ok, why = usable(manifest, root)
  if not ok then return nil, why end
  local n = 0
  for path, want in pairs(manifest.files) do
    local data = love.filesystem.getInfo(root .. path, "file") and love.filesystem.read(root .. path)
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
    -- One bad file must not stop the others, or the start of the app.
    local ok, why = pcall(function()
      local manifest, err
      if love.filesystem.mount(src, "upd/") then
        manifest, err = verify("upd/", tick)
        love.filesystem.unmount(src)
      else
        err = "not a zip"
      end
      if not manifest then
        failed = failed + 1
        store.log("update rejected: " .. tostring(err))
        return
      end
      local id, ver = manifest.pack, manifest.version
      local current = have[id] and have[id][1]
      if current and ver <= current.version then return end -- not newer: nothing to do
      -- Always a new file name: the installed pack is never written over.
      local data = love.filesystem.read(src)
      local target = string.format("packs/%s.v%d.zip", id, ver)
      local written = data and love.filesystem.write(target, data)
      -- Read the copy back: a full card or a bad sector must not leave a broken pack.
      if written and love.filesystem.read(target) == data then
        done = done + 1
        have[id] = have[id] or {}
        table.insert(have[id], 1, { version = ver, name = target:sub(7) })
      else
        love.filesystem.remove(target)
        failed = failed + 1
        store.log("update copy failed: " .. id)
      end
    end)
    if not ok then
      failed = failed + 1
      love.filesystem.unmount(src)
      store.log("update error: " .. tostring(why):sub(1, 60))
    end
    love.filesystem.remove(src)
    if tick then tick() end
  end
  return done, failed
end

-- Mount the newest readable version of every installed pack.
function M.load()
  M.list, M.subjects, M.teacher, M.core = {}, {}, {}, nil
  M.captions = {} -- clip path -> English caption, for English mode
  local text = require("core.text")
  text.dict = {}
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
          if type(manifest) == "table" and manifest.pack == id and usable(manifest, root) then
            manifest.root = root
            M.list[id] = manifest
            loaded = true
          else
            love.filesystem.unmount(path)
            store.log("pack unusable: " .. id)
          end
        else
          store.log("pack not a zip: " .. id)
        end
      end
    end
  end
  -- The browser build carries its packs unpacked inside the app itself.
  for _, id in ipairs(love.filesystem.getDirectoryItems("webpacks")) do
    local root = "webpacks/" .. id .. "/"
    local manifest = read_json(root .. "manifest.json")
    if not M.list[id] and type(manifest) == "table" and manifest.pack == id and usable(manifest, root) then
      manifest.root = root
      M.list[id] = manifest
    end
  end
  for _, p in pairs(M.list) do
    local en = read_json(p.root .. "en.json")
    if type(en) == "table" then
      for k, v in pairs(type(en.texts) == "table" and en.texts or {}) do text.dict[k] = v end
      for k, v in pairs(type(en.clips) == "table" and en.clips or {}) do M.captions[p.root .. k] = v end
    end
    if p.kind == "core" then
      M.core = p
      local strings = read_json(p.root .. (type(p.strings) == "string" and p.strings or "strings.json"))
      p.strings = type(strings) == "table" and strings or {}
    elseif p.kind == "teacher" then
      M.teacher[#M.teacher + 1] = p
    end
  end
  -- A level's own pack first, then optional packs that add games to it.
  local learners = {}
  for _, p in pairs(M.list) do
    if p.kind ~= "core" and p.kind ~= "teacher" and p.subject and p.level then learners[#learners + 1] = p end
  end
  table.sort(learners, function(a, b)
    if (a.optional and 1 or 0) ~= (b.optional and 1 or 0) then return not a.optional end
    return a.pack < b.pack
  end)
  for _, p in ipairs(learners) do
    for _, game in ipairs(p.games or {}) do game.pack = p end
    M.subjects[p.subject] = M.subjects[p.subject] or {}
    local first = M.subjects[p.subject][p.level]
    if not first then
      -- the place works on a copy of the list, so that added games never
      -- change what the pack itself says it holds
      p.all_games = {}
      for i, game in ipairs(p.games or {}) do p.all_games[i] = game end
      M.subjects[p.subject][p.level] = p
    else
      for _, game in ipairs(p.games or {}) do first.all_games[#first.all_games + 1] = game end
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
  local r, err = read_json(pack.root .. "levels/" .. tostring(id) .. ".json")
  if type(r) ~= "table" or type(r.items) ~= "table" then return nil, err or "bad level file" end
  r.pack = pack
  return r
end

function M.review(pack)
  if pack._review == nil then
    local review = read_json(pack.root .. (type(pack.review) == "string" and pack.review or "review.json"))
    pack._review = type(review) == "table" and review or false
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
