-- Journey: number line round (math-1) with a wrong answer, X, Y and a skipped
-- number line; then a round without hops (garden-1). Both to the stars.
local t = ...
t.wait(2) t.skip_tutorial()

local function right_dir(e)
  for dir, slot in pairs(e.slots) do if slot.right then return dir end end
end
local function wrong_dir(e)
  for dir, slot in pairs(e.slots) do if not slot.right then return dir end end
end
local function finish(play, name)
  local e, guard = play.engine, 0
  while play.state ~= "result" and guard < 60 do
    guard = guard + 1
    if e.phase == "ask" then
      t.press(right_dir(e))
      if e.quiz:finished() then t.wait(0.8) t.shot(name .. "_far_bank") end
    else
      t.wait(0.3)
    end
  end
  assert(play.state == "result", name .. ": round did not end")
  assert(e.pos == e.quiz.total, name .. ": bird not on the far bank")
  t.wait(2) t.shot(name .. "_result")
end

local play = t.start_round("math-1", "number_hop", 1)
t.press("a") t.wait(1.5)
local e = play.engine
assert(e.phase == "ask")
t.shot("journey_1_ask")
t.press("x") t.wait(0.5) t.press("y") t.wait(0.5)
t.press(wrong_dir(e)) t.wait(0.2) t.shot("journey_2_wrong")
assert(e.quiz.attempts == 1 and e.phase == "ask")
t.wait(1)
t.press(right_dir(e)) t.wait(0.5) t.shot("journey_3_right")
t.wait(0.6) assert(e.phase == "hop", "no number line")
t.wait(0.9) t.shot("journey_4_line_mid")
t.wait(0.8) t.shot("journey_5_line_end")
t.wait(1.4) assert(e.phase == "ask")
t.press(right_dir(e)) t.wait(1.2) assert(e.phase == "hop")
t.press("a") t.wait(0.1) assert(e.phase == "ask", "A did not skip the number line")
assert(e.pos == 2, "bird at " .. e.pos)
t.press(right_dir(e)) t.wait(1.0) t.press("a") t.wait(0.3)
t.press(right_dir(e)) t.wait(1.0) t.press("a") t.wait(0.3)
t.press(right_dir(e)) t.wait(0.55) t.shot("journey_6_jump")
t.wait(0.6) t.press("a") t.wait(0.3)
t.shot("journey_7_other_side")
finish(play, "journey_8")
t.press("b") t.wait(0.5)

play = t.start_round("garden-1", "tree_keeper", 1, { pair = true })
t.press("a") t.wait(1.5)
e = play.engine
t.shot("journey_9_garden")
t.press(right_dir(e)) t.wait(0.5) t.shot("journey_10_garden_right")
t.wait(0.6) assert(e.phase == "ask", "garden round must not show a number line")
assert(play.player == 2, "pair: turn not passed on")
finish(play, "journey_11")
