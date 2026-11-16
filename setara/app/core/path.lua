-- The guided path through a level. Round ids carry the unit
-- ("en-1-03-a": unit 3, game a), and the games of a pack are listed in
-- teaching order (present, understand, practise, use). The next step is the
-- lowest unit that still has a round without a star, and in it the first
-- such game. Nothing is locked: the child may pick anything; this only says
-- where to go on.
local store = require("core.store")

local M = {}

local function unit_of(id)
  local n = tostring(id):match("%-(%d+)%a*%-%a+$")
  return tonumber(n) or 0
end

-- Returns game, round id; or nil when every round of the level has a star.
-- Add-on packs come after the level's own games.
function M.next_step(pack)
  if type(pack) ~= "table" then return nil end
  local best_game, best_id, best_unit, best_rank
  for rank, game in ipairs(pack.all_games or pack.games or {}) do
    local own = (game.pack == nil or game.pack == pack) and 0 or 1000
    for _, id in ipairs(game.rounds or {}) do
      if store.stars(id) == 0 then
        local unit = unit_of(id) + own
        if not best_unit or unit < best_unit or (unit == best_unit and rank < best_rank) then
          best_game, best_id, best_unit, best_rank = game, id, unit, rank
        end
        break   -- a game's rounds are in unit order: its first open round is enough
      end
    end
  end
  return best_game, best_id
end

return M
