-- Story: a story with decisions (wrong and right choices, back, X, Y), a
-- read-along without decisions, and a story with wrong pictures in pair mode.
local t = ...
t.wait(2) t.skip_tutorial()

local function play_through(play, mistakes, name)
  local e = play.engine
  local n, shots = 0, 0
  while play.state ~= "result" do
    n = n + 1
    assert(n < 300, "story does not end")
    if e.asking and e.phase == "page" then
      if mistakes > 0 then
        mistakes = mistakes - 1
        local wrong = e.right == 1 and 2 or 1
        while e.sel < wrong do t.press("right") end
        while e.sel > wrong do t.press("left") end
        t.press("a") t.wait(0.5)
        assert(e.phase == "oops" and e.dim[wrong])
        t.shot(name .. "_wrong")
        local w = 0
        while e.phase ~= "page" do t.wait(0.5) w = w + 1 assert(w < 80, "did not ask again") end
        t.shot(name .. "_again")
      end
      while e.sel < e.right do t.press("right") end
      while e.sel > e.right do t.press("left") end
      if shots < 1 then shots = shots + 1 t.shot(name .. "_choose") end
      t.press("a") t.wait(0.4)
      assert(e.phase == "right")
      t.wait(1)
    else
      t.press("a") t.wait(0.3)
    end
  end
  return e
end

local play = t.start_round("en-1", "radio_stories", 1)
t.press("a") t.wait(0.5)
local e = play.engine
t.shot("story_1_speaking")
assert(e.i == 1)
t.press("left") assert(e.i == 1)          -- nothing before the first page
t.press("a") t.wait(0.5) t.shot("story_2_ready")
t.press("a") t.wait(0.3) assert(e.i == 2)
t.press("left") t.wait(0.3) assert(e.i == 1)
t.press("x") t.wait(0.3) t.press("y") t.wait(0.3) assert(e.i == 1)
e = play_through(play, 1, "story_en")
t.wait(2) t.shot("story_3_stars")
local attempts, first = e:counts()
assert(e.decisions == 2 and attempts == 3 and first == 1, attempts .. " " .. first)
assert(e:stars() == 2)
t.press("b") t.wait(0.5)

play = t.start_round("fa-1", "read_along", 1)
t.press("a") t.wait(0.5) t.shot("story_fa_page")
e = play_through(play, 0, "story_fa")
assert(e:stars() == 3 and e.decisions == 2 and select(2, e:counts()) == 2)
t.press("b") t.wait(0.5)

play = t.start_round("garden-2", "little_nurse", 1, { pair = true })
t.press("a") t.wait(0.5) t.shot("story_garden_page")
e = play_through(play, 3, "story_garden")
assert(e:stars() == 1, "stars " .. e:stars())
assert(play.player == 2)                   -- three decisions: the turn passed three times
print("story ok")
