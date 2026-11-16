-- Walks through teacher mode: every tool is opened and exercised.
local t = ...
t.wait(2) t.skip_tutorial() t.wait(3)
t.hold("l") t.hold("r") t.wait(2.4) t.release("l") t.release("r") t.wait(0.5)
t.shot("t01_menu")
t.press("a") t.wait(1) t.shot("t02_lesson")
t.press("a") t.wait(2) t.press("y") t.wait(1) t.shot("t03_lesson_meaning")
t.press("right") t.wait(0.3) t.press("down") t.press("down") t.press("down") t.wait(0.3) t.shot("t04_lesson_listen")
for _ = 1, 4 do t.press("right") end
t.wait(0.5) t.shot("t05_goodbye")
t.press("a") t.wait(2) t.shot("t06_check")
for _ = 1, 5 do t.press("up") t.press("right") t.press("a") t.wait(1.5) end
t.shot("t07_check_done")
t.press("a") t.wait(0.5) t.shot("t08_after_check")
t.press("down") t.wait(0.5) t.press("down") t.wait(2) t.shot("t09_lesson_done")
t.press("a") t.wait(0.5)
-- preview
t.press("right") t.press("a") t.wait(9) t.shot("t10_preview")
t.press("b") t.wait(0.3)
-- phrases
t.press("right") t.press("a") t.wait(0.5) t.press("down") t.press("a") t.wait(0.4) t.shot("t11_phrases")
t.press("r") t.wait(0.3) t.press("b") t.wait(0.3)
-- drill
t.press("down") t.press("left") t.press("left") t.press("a") t.wait(0.5) t.shot("t12_drill_list")
t.press("a") t.wait(5) t.shot("t13_drill_run") t.wait(25) t.shot("t14_drill_halves")
if t.top().running then t.press("b") end
t.press("b") t.wait(0.3)
-- games
t.press("right") t.press("a") t.wait(0.3) t.shot("t15_games")
t.press("a") t.wait(1) t.press("up") t.press("right") t.press("up") t.press("up") t.shot("t16_quiz")
t.press("b") t.press("down") t.press("a") t.wait(1) t.press("y") t.wait(0.5) t.shot("t17_do")
t.press("b") t.press("down") t.press("a") t.wait(1) t.press("a") t.wait(1) t.press("a") t.wait(1) t.shot("t18_bingo")
t.press("b") t.press("down") t.press("a") t.wait(1) t.shot("t19_numbers")
t.press("b") t.press("down") t.press("a") t.wait(2) t.press("a") t.wait(1) t.shot("t20_math")
t.press("b") t.press("b") t.wait(0.3)
-- story
t.press("right") t.press("a") t.wait(0.4) t.shot("t21_story")
t.press("b") t.wait(0.3)
-- stations
t.press("down") t.press("left") t.press("left") t.press("a") t.wait(0.3) t.press("left") t.shot("t22_stations")
t.press("a") t.wait(3) t.shot("t23_stations_run") t.press("b") t.wait(0.3)
-- course
t.press("right") t.press("right") t.press("a") t.wait(0.4) t.shot("t24_course")
t.press("right") t.press("a") t.wait(2) t.shot("t25_tip")
t.press("b") t.wait(0.3)
-- the teacher's guide: third tab, first chapter, a few pages
if #require("core.packs").guides > 0 then
  t.press("left") t.wait(0.3) t.shot("t25b_guide_list")
  t.press("a") t.wait(0.8) t.shot("t25c_guide_page")
  t.press("right") t.press("right") t.press("a") t.wait(0.5) t.press("b") t.wait(0.3)
end
t.press("b") t.wait(0.3)
t.press("start") t.wait(0.3) t.shot("t26_pause")

-- Two lesson packs follow each other: past the last lesson of the first comes
-- lesson 1 of the next, and back again.
do
  local T = require("teacher.common")
  local packs = require("core.packs")
  if #packs.teacher > 1 then
    T.set_lesson(1)
    local first = T.pack()
    T.set_lesson(#first.lessons)
    T.set_lesson(#first.lessons + 1)
    assert(T.pack() ~= first and T.lesson_number() == 1, "the next lesson pack did not follow")
    assert(T.load_lesson(), "the first lesson of the next pack does not load")
    t.wait(0.3) t.shot("teacher_second_pack")
    T.set_lesson(0)
    assert(T.pack() == first and T.lesson_number() == #first.lessons, "going back did not return to the first pack")
    T.set_lesson(1)
  end
end
