-- Opens every round of every game in every installed pack and mashes
-- buttons for a moment. It checks nothing but one thing: no round, however
-- its data looks, may crash the app.
local t = ...
t.wait(2) t.skip_tutorial() t.wait(1)
local packs = require("core.packs")
local buttons = { "up", "down", "left", "right", "a", "a", "x", "y", "l", "r" }
local ids = {}
for id in pairs(packs.list) do ids[#ids + 1] = id end
table.sort(ids)
local count = 0
for _, id in ipairs(ids) do
  local pack = packs.list[id]
  for _, game in ipairs(pack.games or {}) do
    for index = 1, #game.rounds do
      for _, pair in ipairs({ false, index == 1 }) do
        if pair or _ == 1 then
          local play = t.start_round(id, game.id, index, { pair = pair, review = index % 5 == 0 })
          assert(not play.failed, "round failed to load: " .. game.rounds[index])
          t.press("a")
          for _ = 1, 28 do
            t.press(buttons[love.math.random(#buttons)])
            if t.top() ~= play then break end
          end
          while t.top() ~= play and #t.app.stack > 2 do t.app.pop() end
          if t.top() == play then t.app.pop() end
          count = count + 1
        end
      end
    end
  end
  print("fuzzed " .. id .. " (" .. count .. " rounds so far)")
end
print("fuzz ok: " .. count .. " rounds")
