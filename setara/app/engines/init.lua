-- Engine registry. One Lua module per mechanic (spec section 5), each built
-- once and reused across all four subjects with different content.
--
-- An engine module returns a table with:
--   engine.load(level, ctx)   level = decoded level file, ctx = shell services
--   engine.update(dt)
--   engine.draw()
--   engine.input(button)      button = one of shell/input.lua's names
--   engine.result()           nil while playing, then { stars = 1..3, ... }
--
-- The `engine` field of a level file selects the module by id.
local M = {}

M.ids = {
  "listen_pick", -- hear a word or question, press the direction of the right picture
  "pairs",       -- flip cards to match sound/word/sum to picture/answer
  "catch",       -- catch only the items that fit the spoken rule
  "builder",     -- put tiles in order: letters, words, steps
  "say_it",      -- hear, say aloud, hear again, self or partner judges
  "story",       -- illustrated audio story with choices
  "journey",     -- cross a map by answering
  "market",      -- count, weigh, pay and give change
  "duel",        -- two players, one device, fastest right answer
  "sorter",      -- drop each item into the right basket
}

-- Returns the engine module for an id, or nil plus a reason if it is not built yet.
function M.get(id)
  local ok, mod = pcall(require, "engines." .. id)
  if ok then return mod end
  return nil, "engine not implemented: " .. tostring(id)
end

return M
