-- Engine registry. One Lua module per mechanic (spec section 5), each built
-- once and reused across all four subjects with different content.
--
-- An engine module returns a table with new(round, ctx). The instance has:
--   :start()        called once the spoken introduction is over
--   :update(dt)  :draw()  :input(button)
--   :again(slow)    X button: say the question again, slowly
--   :help()         Y button: explain in Dari
--   .finished       true when the round is over
--   :stars()        1 to 3
--   :counts()       attempts, correct at first try (for the anonymous counts)
--
-- ctx gives the engine what it needs from the shell:
--   ctx.root        folder of the round's pack, for pictures
--   ctx.say(clips, opts)   speak clips of the pack
--   ctx.pair        two children share the device
--   ctx.player      whose turn it is (1 or 2); ctx.next_player() passes it on
--   ctx.top         y where the play area starts (below the progress dots)
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

-- Returns the engine module for an id, or nil plus a reason.
function M.get(id)
  local ok, mod = pcall(require, "engines." .. tostring(id))
  if ok then return mod end
  return nil, tostring(mod)
end

return M
