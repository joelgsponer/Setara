-- Duel: listen_pick rounds in pair mode. Both players score, a lock-out, both
-- locked out, the automatic repeat, and two rounds to the stars.
local t = ...
t.wait(2) t.skip_tutorial()

local P2 = { up = "x", down = "b", left = "y", right = "a" }
local function right_dir(e)
  for dir, slot in pairs(e.slots) do if slot.right then return dir end end
end
local function wrong_dirs(e)
  local list = {}
  for dir, slot in pairs(e.slots) do if not slot.right then list[#list + 1] = dir end end
  return list
end
local function ask(e)
  local guard = 0
  while e.phase ~= "ask" and not e.finished and guard < 40 do guard = guard + 1 t.wait(0.2) end
end

local play = t.start_round("en-1", "word_stall", 1, { pair = true })
t.press("a") t.wait(0.8)
local e = play.engine
assert(e.uses and e.uses.x, "pair mode did not start the duel engine")
assert(e.phase == "show")
t.shot("duel_1_who")
t.press("up") t.press("a") assert(e.phase == "show", "the picture must stay 2 s")
t.wait(1.8) assert(e.phase == "ask")
t.shot("duel_2_ask")
local n = 0
for _ in pairs(e.slots) do n = n + 1 end
assert(n == 4, "want four cards, got " .. n)

-- player 1 wrong (locked out), then player 2 right
t.press(wrong_dirs(e)[1]) t.wait(0.2) t.shot("duel_3_p1_out")
assert(e.locked[1] and e.phase == "ask")
t.press(right_dir(e)) assert(e.phase == "ask", "locked player could answer")
t.press(P2[right_dir(e)]) t.wait(0.3) t.shot("duel_4_p2_point")
assert(e.score[2] == 1 and e.score[1] == 0)
ask(e)

-- player 1 right
t.press(right_dir(e)) t.wait(0.3) t.shot("duel_5_p1_point")
assert(e.score[1] == 1)
ask(e)

-- both wrong: the answer is shown, no point, the item comes back
local w = wrong_dirs(e)
t.press(P2[w[1]]) t.press(w[2]) t.wait(0.4) t.shot("duel_6_both_out")
assert(e.phase == "none" and e.score[1] + e.score[2] == 2)
ask(e)

-- B and Start: B is an answer, it must not leave the round
assert(t.top() == play)
-- nobody answers: the question is said again by itself
local said = 0
local say = e.ctx.say
e.ctx.say = function(...) said = said + 1 return say(...) end
t.wait(14)
assert(said >= 1, "the question was not repeated")
t.shot("duel_7_waiting")

local guard = 0
while play.state ~= "result" and guard < 40 do
  guard = guard + 1
  ask(e)
  if e.phase == "ask" then
    if guard % 2 == 0 then t.press(right_dir(e)) else t.press(P2[right_dir(e)]) end
  end
  t.wait(0.3)
end
assert(play.state == "result", "round did not end")
assert(play.stars == 2, "stars " .. tostring(play.stars)) -- 4 of 5 right the first time
t.wait(2) t.shot("duel_8_result")
t.press("b") t.wait(0.5)

play = t.start_round("math-1", "count_the_flock", 1, { pair = true })
t.press("a") t.wait(3.2)
e = play.engine
t.shot("duel_9_math")
guard = 0
while play.state ~= "result" and guard < 40 do
  guard = guard + 1
  ask(e)
  if e.phase == "ask" then t.press(P2[right_dir(e)]) end
  t.wait(0.3)
  if guard == 1 then t.shot("duel_10_math_point") end
end
assert(play.state == "result" and play.stars == 3)
