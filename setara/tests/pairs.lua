-- Pairs: a round alone with misses, X and Y, then a perfect round in pair mode.
local t = ...
t.wait(2) t.skip_tutorial()

local function go(e, i)
  local n = 0
  while e.cards[e.cur].row ~= e.cards[i].row do
    t.press(e.cards[e.cur].row < e.cards[i].row and "down" or "up")
    n = n + 1 assert(n < 20, "cursor stuck")
  end
  while e.cur ~= i do
    t.press(e.cur < i and "right" or "left")
    n = n + 1 assert(n < 20, "cursor stuck")
  end
end

local function partner(e, i)
  for k, c in ipairs(e.cards) do
    if k ~= i and c.pair == e.cards[i].pair then return k end
  end
end

local function solve(e, play)
  local n = 0
  while play.state ~= "result" do
    n = n + 1 assert(n < 40, "round does not end")
    local i
    for k, c in ipairs(e.cards) do if not c.up then i = k break end end
    if i then
      go(e, i) t.press("a") t.wait(0.3)
      go(e, partner(e, i)) t.press("a") t.wait(0.5)
    else
      t.wait(0.5)
    end
  end
end

local play = t.start_round("fa-1", "verse_corner", 1)
t.press("a") t.wait(0.5)
local e = play.engine
t.shot("pairs_1_dealt")
-- a miss: two cards of different pairs
local other
for k, c in ipairs(e.cards) do if c.pair ~= e.cards[1].pair then other = k break end end
go(e, 1) t.press("a") t.wait(0.3)
t.press("x") t.wait(0.3) t.press("y") t.wait(0.3)
go(e, other) t.press("a") t.wait(0.4)
assert(e.phase == "miss")
t.shot("pairs_2_miss")
t.wait(1.5)
assert(e.phase == "play" and not e.cards[1].up and e.tries == 1)
-- a match
go(e, 1) t.press("a") t.wait(0.3)
go(e, partner(e, 1)) t.press("a") t.wait(0.25)
assert(e.found == 1)
t.shot("pairs_3_match")
t.press("a") t.wait(0.2)                 -- an open card cannot be turned again
assert(#e.open == 0)
solve(e, play)
t.wait(2) t.shot("pairs_4_stars")
local tries, first = e:counts()
assert(tries == e.total + 1 and first == e.total, tries .. " " .. first)
assert(e:stars() == 3)
t.press("b") t.wait(0.5)

play = t.start_round("fa-2", "verse_corner", 1, { pair = true })
t.press("a") t.wait(0.5)
e = play.engine
assert(#e.cards == 12)
go(e, 12) go(e, 1)
for k, c in ipairs(e.cards) do if c.pair ~= e.cards[1].pair then other = k break end end
t.press("a") t.wait(0.3) go(e, other) t.press("a") t.wait(0.4)
t.shot("pairs_5_pair_miss")
assert(play.player == 1)
t.wait(1.5)
assert(play.player == 2)                   -- a miss passes the turn
go(e, 1) t.press("a") t.wait(0.3) go(e, partner(e, 1)) t.press("a") t.wait(0.3)
assert(play.player == 2 and e.score[2] == 1)   -- a match keeps it
t.shot("pairs_6_pair_match")
solve(e, play)
assert(e.score[2] == 6)
print("pairs ok", e:counts())
