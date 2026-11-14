-- Say It: one full round alone (with X = once more, Y = help), then pair mode.
local t = ...
t.wait(2) t.skip_tutorial()
local play = t.start_round("en-1", "echo", 1)
t.press("a")                       -- skip the spoken intro
t.wait(0.4) t.shot("say_1_listen")
local e = play.engine
assert(e.phase == "listen", e.phase)
local guard = 0
while e.phase ~= "turn" do t.wait(0.2) guard = guard + 1 assert(guard < 200, "stuck listening") end
while not e.bar do t.wait(0.1) end
t.wait(0.8) t.shot("say_2_turn")
while e.phase ~= "judge" do t.wait(0.2) guard = guard + 1 assert(guard < 400, "stuck before judge") end
t.shot("say_3_judge")
t.press("x") t.wait(0.3)           -- once more: not right at the first try
assert(e.phase == "listen" and e.quiz.tried)
t.press("y") t.wait(0.3) assert(e.phase == "meaning")
t.press("a") t.press("a") t.press("a") t.wait(0.2)
assert(e.phase == "judge", e.phase)
t.press("y") t.wait(0.5) assert(e.phase == "judge")
t.press("a") t.wait(0.3) t.shot("say_4_right")
t.wait(1)
-- the rest: skip through, slow repeat once in the middle
local n = 0
while play.state ~= "result" do
  n = n + 1
  assert(n < 200, "round does not end")
  if e.phase == "listen" and n == 3 then t.press("x") t.wait(0.3) assert(e.phase == "listen") end
  if e.item and not e.item.show and e.phase == "listen" and not e.shot then e.shot = true t.wait(0.3) t.shot("say_5_no_picture") end
  t.press("a") t.wait(0.3)
end
t.wait(2) t.shot("say_6_stars")
local attempts, first = e:counts()
assert(first == e.quiz.total - 1, "first " .. first)
assert(e:stars() == 3)
t.press("b") t.wait(0.5)

play = t.start_round("en-1", "echo", 2, { pair = true })
t.press("a") t.wait(0.3)
e = play.engine
t.press("a") t.press("a") t.press("a") t.wait(0.3)
assert(e.phase == "judge")
t.shot("say_7_pair_judge")
assert(play.player == 1)
t.press("a") t.wait(1.2)
assert(play.player == 2)
print("say_it ok", attempts, first)
