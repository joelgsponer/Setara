-- Pausing while the guide is speaking must never leave a round standing
-- (found in review: the warm-up and the sorter's basket introduction did).
local t = ...
t.wait(2) t.skip_tutorial() t.wait(1)
local packs = require("core.packs")
local store = require("core.store")

-- stars on earlier rounds, so that a warm-up exists
local pack = packs.list["en-1"]
for _, game in ipairs(pack.games) do
  if game.id == "word_stall" then
    for i = 1, 6 do store.progress.stars[game.rounds[i]] = 2 end
  end
end

local play = t.start_round("en-1", "word_stall", 8, { review = true })
assert(play.warmup, "the round has a warm-up")
t.press("a")                      -- skip the game's introduction
assert(play.state == "warmup")
t.press("start") t.wait(1.5)      -- pause in the middle of "first a little practice"
t.press("a") t.wait(8)            -- carry on
assert(play.warmup.item, "the warm-up started after the pause")
t.shot("pause_1_warmup")
t.app.pop()

-- pause during the round introduction itself
play = t.start_round("en-1", "word_stall", 1)
t.wait(0.3) t.press("start") t.wait(1) t.press("a") t.wait(12)
assert(play.state == "main" and play.engine.item, "the round began after the pause")
t.app.pop()

-- the sorter introduces its baskets one by one
play = t.start_round("fa-1", "letter_shapes", 1)
t.press("a") t.wait(0.5)
assert(play.engine.phase == "intro")
t.press("start") t.wait(1) t.press("a") t.wait(25)
assert(play.engine.phase ~= "intro", "the baskets were introduced after the pause")
t.app.pop()

-- the first scene can never be popped away
local depth = #t.app.stack
for _ = 1, 5 do t.app.pop() end
assert(#t.app.stack == 1, "home stays")
print("pause ok (stack was " .. depth .. ")")
