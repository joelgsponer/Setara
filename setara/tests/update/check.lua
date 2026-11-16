-- Run by tests/update/run.sh after packs were dropped into update/.
local t = ...
-- Installing takes longer the more packs there are: wait until the update
-- folder has been dealt with and the packs are loaded, not a fixed time.
for _ = 1, 90 do
  t.wait(1)
  if #love.filesystem.getDirectoryItems("update") == 0 and require("core.packs").core then break end
end
t.wait(1)
local packs = require("core.packs")
local store = require("core.store")
print("EN1_VERSION=" .. tostring(packs.list["en-1"] and packs.list["en-1"].version))
print("CORE=" .. tostring(packs.core ~= nil))
local rejected = 0
for _, entry in ipairs(store.stats.log) do
  if tostring(entry.code):find("update rejected") then rejected = rejected + 1 end
end
print("REJECTED=" .. rejected)
print("LEFT_IN_UPDATE=" .. #love.filesystem.getDirectoryItems("update"))
