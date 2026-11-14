-- Story Time: read Dari and English stories aloud to the whole class, with
-- the pictures on the screen (or on a TV over HDMI).
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local packs = require("core.packs")
local T = require("teacher.common")

local Story = {}
Story.__index = Story

function Story.new()
  local self = setmetatable({ t = 0, sel = 1, list = {} }, Story)
  for _, subject in ipairs({ "fa", "en", "garden" }) do
    for _, level in ipairs(packs.levels(subject)) do
      local pack = packs.subjects[subject][level]
      for _, game in ipairs(pack.games or {}) do
        if game.engine == "story" then
          for i, id in ipairs(game.rounds or {}) do
            self.list[#self.list + 1] = { pack = pack, game = game, id = id, n = i, subject = subject, level = level }
          end
        end
      end
    end
  end
  return self
end

function Story:update(dt) self.t = self.t + dt end

function Story:input(b)
  if b == "b" then app.pop()
  elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
  elseif b == "down" and self.sel < #self.list then self.sel = self.sel + 1 sfx.play("move")
  elseif b == "a" and self.list[self.sel] then
    local s = self.list[self.sel]
    app.push(require("scenes.play").new({ pack = s.pack, game = s.game, round_id = s.id, review = false }))
  end
end

function Story:draw()
  T.header("tool_story")
  local first = math.max(1, math.min(self.sel - 2, #self.list - 5))
  for i = first, math.min(#self.list, first + 5) do
    local s = self.list[i]
    local y = 54 + (i - first) * 64
    ui.card(14, y, 612, 58, { selected = i == self.sel, fill = i == self.sel and ui.c.shade or ui.c.paper })
    ui.set(ui.c[s.subject])
    love.graphics.circle("fill", 44, y + 29, 16)
    ui.set(ui.c.white)
    text.centered("bold", tostring(s.level), 28, y + 13, 32, 32, 24)
    ui.set(ui.c.ink)
    text.print((s.game.title_en or "") .. "  " .. s.n, 74, y + 14, 260, "left", 24, true)
    if s.game.title_fa and s.game.title_fa[1] then text.fa(s.game.title_fa, 330, y + 6, 280, 24, "right", true) end
  end
  T.hints({ { "a", "hint_start" } })
end

return Story
