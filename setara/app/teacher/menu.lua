-- Teacher mode. Opened by holding L and R for two seconds on the home screen.
-- Top row: today's lesson (left and right change it). Below: the nine tools.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local store = require("core.store")
local T = require("teacher.common")
local g = love.graphics

local Menu = {}
Menu.__index = Menu

local TOOLS = {
  { id = "lesson", key = "tool_lesson", needs_lesson = true },
  { id = "preview", key = "tool_preview", needs_lesson = true },
  { id = "phrases", key = "tool_phrases" },
  { id = "drill", key = "tool_drill", needs_lesson = true },
  { id = "games", key = "tool_games" },
  { id = "story", key = "tool_story" },
  { id = "stations", key = "tool_stations" },
  { id = "check", key = "tool_check", needs_lesson = true },
  { id = "course", key = "tool_course" },
}

function Menu.new()
  return setmetatable({ t = 0, row = 1, col = 1, entered = 0 }, Menu)
end

function Menu:enter()
  self.started = app.time
end

function Menu:leave()
  T.stop()
  store.add_minutes("teacher", app.time - (self.started or app.time))
  store.save()
end

function Menu:update(dt) self.t = self.t + dt end

function Menu:input(b)
  if b == "b" then
    app.pop()
  elseif b == "start" then
    app.push(require("scenes.pause").new({ teacher = true }))
  elseif self.row == 0 then
    local n = T.lesson_number()
    if not n then self.row = 1 return end
    if b == "left" then T.set_lesson(n - 1) sfx.play("move")
    elseif b == "right" then T.set_lesson(n + 1) sfx.play("move")
    elseif b == "down" or b == "a" then self.row = 1 sfx.play("move") end
  elseif b == "a" then
    local tool = TOOLS[(self.row - 1) * 3 + self.col]
    if tool.needs_lesson and not T.lesson_number() then
      sfx.play("wrong")
      return
    end
    sfx.play("right")
    store.count_teacher("open_" .. tool.id)
    app.push(require("teacher." .. tool.id).new())
  else
    local row, col = self.row, self.col
    if b == "left" then col = col - 1 elseif b == "right" then col = col + 1
    elseif b == "up" then row = row - 1 elseif b == "down" then row = row + 1 else return end
    if row >= 0 and row <= 3 and col >= 1 and col <= 3 then
      self.row, self.col = row, col
      sfx.play("move")
    end
  end
end

-- Small pictograms for the nine tools, drawn in a 60 px box centred on cx, cy.
local function icon(id, cx, cy)
  ui.set(ui.c.teacher)
  g.setLineWidth(4)
  if id == "lesson" then
    g.polygon("fill", cx - 14, cy - 20, cx - 14, cy + 20, cx + 20, cy)
  elseif id == "preview" then
    g.circle("fill", cx - 4, cy - 2, 18)
    ui.set(ui.c.paper)
    g.circle("fill", cx + 6, cy - 8, 16)
    ui.star(cx + 16, cy + 14, 7, true)
  elseif id == "phrases" then
    g.rectangle("fill", cx - 24, cy - 18, 48, 30, 8, 8)
    g.polygon("fill", cx - 12, cy + 10, cx - 12, cy + 24, cx + 2, cy + 10)
  elseif id == "drill" then
    g.arc("line", "open", cx, cy, 18, -2.6, 1.2)
    g.polygon("fill", cx + 6, cy + 10, cx + 22, cy + 14, cx + 12, cy + 26)
    g.circle("fill", cx, cy, 5)
  elseif id == "games" then
    g.rectangle("fill", cx - 22, cy - 22, 20, 20, 4, 4)
    g.rectangle("fill", cx + 2, cy + 2, 20, 20, 4, 4)
    ui.set(ui.c.gold)
    g.circle("fill", cx + 12, cy - 12, 10)
    g.circle("fill", cx - 12, cy + 12, 10)
  elseif id == "story" then
    g.polygon("fill", cx - 26, cy - 14, cx, cy - 6, cx, cy + 20, cx - 26, cy + 12)
    g.polygon("fill", cx + 26, cy - 14, cx, cy - 6, cx, cy + 20, cx + 26, cy + 12)
  elseif id == "stations" then
    g.circle("line", cx, cy, 20)
    g.line(cx, cy, cx, cy - 13)
    g.line(cx, cy, cx + 9, cy + 5)
  elseif id == "check" then
    g.setLineWidth(7)
    g.line(cx - 18, cy + 2, cx - 6, cy + 14, cx + 20, cy - 16)
  elseif id == "course" then
    g.polygon("fill", cx - 28, cy - 6, cx, cy - 20, cx + 28, cy - 6, cx, cy + 8)
    g.rectangle("fill", cx - 14, cy + 4, 28, 12, 4, 4)
  end
  g.setLineWidth(1)
end

function Menu:draw()
  T.header("t_title")
  local pack = T.pack()
  if not pack then
    local s = T.S("t_no_pack")
    T.dari_card(s.fa or {}, 60, 180, 520)
    return
  end
  -- today's lesson
  local n = T.lesson_number()
  local info = T.lesson_info()
  ui.card(14, 52, 612, 56, { selected = self.row == 0, fill = ui.c.paper })
  if info then
    ui.arrow("left", 32, 80, 9, ui.c.ink)
    ui.arrow("right", 608, 80, 9, ui.c.ink)
    ui.set(ui.c.teacher)
    if T.pack_count() > 1 then
      -- which book: English 1, English 2 ...
      text.print(tostring(pack.level or ""), 48, 54, 20, "left", 18, true)
      text.print(tostring(n), 60, 60, 44, "left", 32, true)
    else
      text.print(tostring(n), 50, 56, 60, "left", 36, true)
    end
    ui.set(ui.c.ink)
    text.print(info.title_en or "", 100, 66, 250, "left", 20, true)
    if info.title_fa and info.title_fa[1] and text.locale ~= "en" then
      text.fa(info.title_fa, 340, 58, 250, 24, "right", true)
    end
    if (store.stats.teacher["done_" .. info.id] or 0) > 0 then
      ui.set(ui.c.good)
      g.setLineWidth(5)
      g.line(56, 98, 62, 104, 74, 92)
      g.setLineWidth(1)
    end
  end
  for i, tool in ipairs(TOOLS) do
    local row, col = math.floor((i - 1) / 3), (i - 1) % 3
    local x, y = 14 + col * 206, 116 + row * 108
    local dim = tool.needs_lesson and not n
    ui.card(x, y, 200, 100, { selected = self.row == row + 1 and self.col == col + 1, dim = dim })
    icon(tool.id, x + 100, y + 34)
    ui.set(ui.c.ink)
    local s = T.S(tool.key)
    if s.fa and s.fa[1] then text.centered("fabold", s.fa[1], x + 4, y + 60, 192, 40, 24) end
  end
end

return Menu
