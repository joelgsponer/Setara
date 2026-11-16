-- Fetching packs on a phone. Only the phone apps carry a catalogue
-- (catalogue.json); the handheld has none and never opens a connection.
--
-- What goes over the wire: one request for one file, named by a hash. Nothing
-- about the device or its user is sent. The file is accepted only if its
-- SHA-256 is the one written into the app when it was built, so a pack that
-- was changed on the way is thrown away. Then it goes through the same
-- checks as a pack from the card.
local store = require("core.store")

local M = { catalogue = nil, job = nil }

local THREAD = [[
local url, target, want = ...
local out = love.thread.getChannel("fetch_out")
local stop = love.thread.getChannel("fetch_stop")
local ok, err = pcall(function()
  require("love.filesystem") require("love.data")
  local http, ltn12
  local secure = pcall(function() http = require("https") end) and url:match("^https:")
  love.filesystem.createDirectory("update")
  local file = assert(love.filesystem.newFile(target, "w"))
  local got = 0
  if secure then
    -- a build with the https module: one call, the whole file
    local code, body = http.request(url)
    assert(code == 200 and type(body) == "string", "server answered " .. tostring(code))
    file:write(body) got = #body
  else
    http, ltn12 = require("socket.http"), require("ltn12")
    http.TIMEOUT = 30
    local sink = function(chunk)
      if stop:peek() then return nil, "stopped" end
      if chunk then
        file:write(chunk)
        got = got + #chunk
        out:push({ got = got })
      end
      return 1
    end
    local _, code = http.request({ url = url, sink = sink, redirect = true })
    assert(code == 200, "server answered " .. tostring(code))
  end
  file:close()
  local data = love.filesystem.read(target)
  local hash = love.data.encode("string", "hex", love.data.hash("sha256", data or ""))
  assert(hash == want, "the file is not the one expected")
end)
if not ok then love.filesystem.remove(target) end
out:push({ done = true, ok = ok, err = ok and nil or tostring(err) })
]]

function M.load()
  M.catalogue = nil
  if not love.filesystem.getInfo("catalogue.json", "file") then return end
  local ok, data = pcall(require("core.json").decode, love.filesystem.read("catalogue.json") or "")
  if ok and type(data) == "table" and type(data.base) == "string" and type(data.packs) == "table" then
    M.catalogue = data
  end
end

-- Catalogue entries that are not installed (or installed in an older version).
-- filter(entry) narrows the list.
function M.missing(filter)
  local out = {}
  if not M.catalogue then return out end
  local packs = require("core.packs")
  for _, e in ipairs(M.catalogue.packs) do
    local have = packs.list[e.pack]
    if (not have or (have.version or 0) < (e.version or 0)) and (not filter or filter(e)) then out[#out + 1] = e end
  end
  return out
end

function M.busy() return M.job ~= nil end

function M.start(entry)
  if M.job or not M.catalogue then return false end
  love.thread.getChannel("fetch_out"):clear()
  love.thread.getChannel("fetch_stop"):clear()
  local thread = love.thread.newThread(THREAD)
  M.job = { entry = entry, got = 0, thread = thread, target = "update/" .. entry.pack .. ".zip" }
  thread:start(M.catalogue.base .. entry.file, M.job.target, entry.sha256)
  return true
end

function M.stop()
  if M.job then love.thread.getChannel("fetch_stop"):push(true) end
end

-- Call every frame. Returns "done", "failed" or nil while it runs.
function M.update()
  local job = M.job
  if not job then return nil end
  local out = love.thread.getChannel("fetch_out")
  local msg = out:pop()
  while msg do
    if msg.got then job.got = msg.got end
    if msg.done then
      M.job = nil
      if not msg.ok then
        store.log("fetch failed: " .. tostring(msg.err):sub(1, 60))
        return "failed", job.entry
      end
      return "done", job.entry
    end
    msg = out:pop()
  end
  local err = job.thread:getError()
  if err then
    M.job = nil
    love.filesystem.remove(job.target)
    store.log("fetch error: " .. tostring(err):sub(1, 60))
    return "failed", job.entry
  end
  return nil
end

function M.progress()
  local job = M.job
  if not job then return 0 end
  return math.min(1, job.got / math.max(1, job.entry.size))
end

return M
