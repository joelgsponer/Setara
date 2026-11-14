-- Catch: Latin letters and Dari letters. Catches by moving the basket under
-- targets and away from the others; also catches one wrong thing on purpose.
local t = ...
t.wait(2) t.skip_tutorial()

-- The thing that reaches the basket next.
local function lowest(e)
  local best
  for _, th in ipairs(e.things) do
    if th.state == "fall" and (not best or th.y > best.y) then best = th end
  end
  return best
end

local function go(e, lane)
  for _ = 1, 3 do
    if e.lane == lane then return end
    t.press(lane > e.lane and "right" or "left")
  end
end

-- One step of good play: stand under a target, step aside for the others.
local function step(e, catch_wrong)
  local th = lowest(e)
  if th then
    if th.target or catch_wrong then go(e, th.lane)
    elseif th.lane == e.lane then go(e, th.lane == 2 and 1 or 2) end
  end
  t.wait(0.1)
end

local function finish(play)
  local e = play.engine
  for _ = 1, 4000 do
    if play.state == "result" then return end
    if e.phase == "rule" then t.press("a") end
    step(e)
  end
  error("catch round did not finish")
end

local function leave(play)
  assert(play.state == "result", "not at the stars")
  t.wait(1.5) t.press("b") t.wait(0.3)
end

-- 1. English first sounds
local play = t.start_round("en-1", "sound_catcher", 1)
t.press("a") t.wait(0.5)
local e = play.engine
assert(e.phase == "rule" and #e.things == 0, "nothing falls while the rule is spoken")
t.shot("catch_1_rule")
t.press("x") t.wait(0.4)
assert(e.phase == "rule")
t.press("left") t.press("left") t.press("left")
assert(e.lane == 1)
t.press("a") t.wait(0.5)
assert(e.phase == "play")
t.press("y")
t.wait(3) t.shot("catch_2_falling")
-- time from the top to the basket at the normal level
local th = e.things[#e.things]
local y0, t0 = th.y, t.app.time
t.wait(1)
if th.state == "fall" then
  local secs = 380 / ((th.y - y0) / (t.app.time - t0))
  assert(secs > 3.5 and secs < 4.5, "about four seconds to fall, got " .. secs)
end
-- catch a wrong one on purpose
for _ = 1, 400 do
  if e.quiz.tried then break end
  local low = lowest(e)
  if low and not low.target then go(e, low.lane) elseif low and low.lane == e.lane then go(e, low.lane == 2 and 1 or 2) end
  t.wait(0.1)
end
assert(e.quiz.tried, "a wrong thing was caught")
local got = e.got
t.wait(0.15) t.shot("catch_3_bounce")
assert(e.got == got, "earlier catches are kept")
for _ = 1, 600 do
  if e.got >= 2 then break end
  step(e)
end
t.shot("catch_4_two_caught")
finish(play)
t.wait(2) t.shot("catch_5_stars")
leave(play)

-- 2. Dari letters, two children
play = t.start_round("fa-1", "syllable_catch", 1, { pair = true })
t.press("a") t.wait(0.5)
e = play.engine
t.press("a") t.wait(4.2)
t.shot("catch_6_dari")
local item = e.item
for _ = 1, 900 do
  if e.item ~= item then break end
  step(e)
end
assert(play.player == 2, "the turn passes on")
t.wait(0.3) t.shot("catch_7_next_rule")
finish(play)
assert(e.quiz.first_right == e.quiz.total)
leave(play)

-- odd data must not crash
local C = require("engines.catch")
local ctx = { root = "", say = function() end, next_player = function() end }
local odd = C.new({ items = { { targets = {} }, { targets = { { t = "a" } }, need = "x" } } }, ctx)
odd:start() odd:help() odd:again(true)
for _ = 1, 3000 do
  odd:update(0.05) odd:draw()
  local low = lowest(odd)
  if low then odd.lane = low.lane end
  if odd.finished then break end
end
assert(odd.finished)
print("catch ok")
