-- Sorter: four Dari letter-form baskets, a two-basket picture round in pair
-- mode, and a two-basket number round. Plays each to the stars.
local t = ...
t.wait(2) t.skip_tutorial()

local function other_dir(e)
  for dir, b in pairs(e.by_dir) do
    if b ~= e.target and not e.wrong[b] then return dir end
  end
end

local function finish(play)
  local e = play.engine
  for _ = 1, 600 do
    if play.state == "result" then return end
    if e.phase == "ask" then t.press(e.target.dir) else t.wait(0.1) end
  end
  error("sorter round did not finish")
end

local function leave(play)
  assert(play.state == "result", "not at the stars")
  t.wait(1.5) t.press("b") t.wait(0.3)
end

-- 1. letter shapes: spoken basket intro, wrong, X, Y, then the whole round
local play = t.start_round("fa-1", "letter_shapes", 1)
t.press("a") t.wait(0.6)
local e = play.engine
assert(e.phase == "intro", "baskets are introduced first")
t.shot("sorter_1_intro")
t.wait(1.2) t.shot("sorter_1_intro_b")
t.press("x")                       -- nothing to repeat yet: must not break
t.press("a") t.wait(0.5)
assert(e.phase == "ask")
t.shot("sorter_2_ask")
local wrong = other_dir(e)
t.press(wrong) t.wait(0.15) t.shot("sorter_3_sliding")
t.wait(0.8)
assert(e.phase == "ask" and e.wrong[e.by_dir[wrong]], "wrong basket is dimmed")
assert(e.quiz.attempts == 1)
t.shot("sorter_4_wrong_dimmed")
t.press(wrong) t.wait(0.2)
assert(e.phase == "ask", "a dimmed basket takes nothing")
t.press("x") t.wait(0.3)
t.press("y") t.wait(0.4)
assert(e.speaking == 1, "Y says the baskets again")
t.shot("sorter_5_help")
t.press(e.target.dir) t.wait(0.5)
assert(e.phase == "right")
t.shot("sorter_6_right")
finish(play)
assert(e.quiz.first_right == e.quiz.total - 1)
t.wait(2) t.shot("sorter_7_stars")
leave(play)

-- 2. pictures, two children
play = t.start_round("garden-1", "safe_water", 1, { pair = true })
t.press("a") t.wait(0.3) t.press("a") t.wait(0.6)
e = play.engine
assert(e.phase == "ask" and play.player == 1)
t.shot("sorter_8_pictures_pair")
t.press(e.target.dir) t.wait(0.4)
assert(play.player == 2, "the turn passes on")
finish(play)
leave(play)

-- 3. numbers into odd / even; three baskets come from fa-1 round 2 if present
play = t.start_round("math-2", "share_the_bread", 1)
t.press("a") t.wait(0.3) t.press("a") t.wait(0.6)
t.shot("sorter_9_numbers")
finish(play)
assert(play.engine.quiz.first_right == play.engine.quiz.total)
leave(play)

-- odd data must not crash
local S = require("engines.sorter")
local ctx = { root = "", say = function() end, next_player = function() end }
local odd = S.new({ items = { { thing = { t = "x" }, basket = "nowhere" } } }, ctx)
odd:start() odd:update(0.1) odd:draw() odd:help() odd:again(true)
assert(odd.finished)
odd = S.new({ baskets = { { id = "a", t = "A" }, { id = "b", t = "B" }, { id = "c", t = "C" } },
  items = { { thing = { id = "q", img = "img/none.png" }, basket = "c" } } }, ctx)
odd:start() for _ = 1, 40 do odd:update(0.1) end
odd:draw() odd:again(true) odd:help() odd:input(odd.target.dir)
for _ = 1, 40 do odd:update(0.1) end
assert(odd.finished)
print("sorter ok")
