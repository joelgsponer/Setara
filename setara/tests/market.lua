-- Market: count rounds (en-1, math-1) and a pay round (math-2), each to the
-- stars, with a wrong amount, X, Y, the full tray and pair mode.
local t = ...
t.wait(2) t.skip_tutorial()

-- Fewest pieces for the target, largest first (fine for 1-2-5 style units).
local function pay(e)
  local left = e.target
  for i = #e.units, 1, -1 do
    while e.sel > i do t.press("left") end
    while e.sel < i do t.press("right") end
    while left >= e.units[i] do t.press("up") left = left - e.units[i] end
  end
  assert(left == 0, "cannot pay " .. e.target)
end
local function solve(e)
  if e.pay then pay(e) else for _ = 1, e.target do t.press("up") end end
  t.press("a")
end
local function finish(play, name)
  local e, guard = play.engine, 0
  while play.state ~= "result" and guard < 60 do
    guard = guard + 1
    if e.phase == "play" then solve(e) else t.wait(0.3) end
  end
  assert(play.state == "result", name .. ": round did not end")
  t.wait(2) t.shot(name .. "_result")
  t.press("b") t.wait(0.5)
end

-- count, English requests
local play = t.start_round("en-1", "shopkeeper", 1, { pair = true })
t.press("a") t.wait(1.5)
local e = play.engine
assert(e.phase == "play" and not e.pay)
t.shot("market_1_count_empty")
t.press("x") t.wait(0.4) t.press("y") t.wait(0.4)
t.press("a") t.wait(0.2) assert(e.phase == "play", "A on an empty tray only repeats")
for _ = 1, e.target + 2 do t.press("up") end
t.press("down")
t.shot("market_2_count_some")
t.press("a") t.wait(0.4) t.shot("market_3_count_wrong")
assert(e.phase == "no" and e.quiz.attempts == 1)
t.wait(1.2) assert(e.phase == "play" and e.n == 0, "tray not cleared")
for _ = 1, 23 do t.press("up") end
assert(e.n == 20, "tray holds " .. e.n)
t.shot("market_4_count_full")
for _ = 1, 20 do t.press("down") end
t.press("down") assert(e.n == 0)
solve(e) t.wait(0.4) t.shot("market_5_count_right")
assert(e.phase == "right" and play.player == 2, "pair: turn not passed on")
finish(play, "market_6")

-- count, maths
play = t.start_round("math-1", "market_scales", 1)
t.press("a") t.wait(1.5)
e = play.engine
for _ = 1, e.target do t.press("up") end
t.shot("market_7_math_count")
finish(play, "market_8")

-- pay
play = t.start_round("math-2", "market_scales", 1)
t.press("a") t.wait(1.5)
e = play.engine
assert(e.pay and #e.units == 3)
t.shot("market_9_pay_empty")
t.press("up") t.press("right") t.press("up") t.press("up") t.press("right") t.press("up") t.press("up")
assert(e:sum() == 1 + 2 + 2 + 5 + 5)
t.shot("market_10_pay_pile")
t.press("left") t.press("down") assert(e:sum() == 13, "down takes one of the chosen value")
t.press("a") t.wait(0.4) t.shot("market_11_pay_wrong")
assert(e.phase == "no")
t.wait(1.2) assert(#e.pile == 0, "counter not cleared")
for _ = 1, 15 do t.press("up") end
assert(#e.pile == 12, "pile holds " .. #e.pile)
t.shot("market_12_pay_full")
for _ = 1, 12 do t.press("down") end
assert(#e.pile == 0)
solve(e) t.wait(0.4) t.shot("market_13_pay_right")
assert(e.phase == "right")
finish(play, "market_14")
