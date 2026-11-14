-- The valley on the home screen. Four places, one per subject. Stars earned
-- in a subject repair and grow its place: stalls open, shelves fill, the
-- water wheel turns, trees grow. stage runs from 0 (start) to 4 (thriving).
local ui = require("core.ui")
local M = {}
local g = love.graphics

local function hex(h)
  return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 }
end

local INK = ui.c.ink
local WALL, WALL2 = hex("E8D2A6"), hex("D9BC86")
local ROOF = hex("B5653A")
local GOODS = { hex("E0483F"), hex("F2B705"), hex("4E9A51"), hex("E07A3F"), hex("8E5BB5"), hex("3F7FBF") }

local function outline(mode, ...)
  g.setLineWidth(3)
  ui.set(INK)
  if mode == "rect" then g.rectangle("line", ...)
  elseif mode == "poly" then g.polygon("line", ...)
  elseif mode == "circle" then g.circle("line", ...)
  elseif mode == "ellipse" then g.ellipse("line", ...) end
  g.setLineWidth(1)
end

local function box(c, x, y, w, h, r)
  ui.set(c)
  g.rectangle("fill", x, y, w, h, r or 0, r or 0)
  outline("rect", x, y, w, h, r or 0, r or 0)
end

local function poly(c, ...)
  ui.set(c)
  g.polygon("fill", ...)
  outline("poly", ...)
end

function M.background(t)
  ui.set(ui.c.sky)
  g.rectangle("fill", 0, 0, 640, 480)
  -- sun
  ui.set(hex("FBE28A"))
  g.circle("fill", 560, 58, 30)
  -- far mountains with snow
  ui.set(hex("A9B8C9"))
  g.polygon("fill", 0, 190, 90, 70, 170, 150, 260, 50, 360, 160, 450, 80, 540, 150, 640, 100, 640, 200, 0, 200)
  ui.set(ui.c.white)
  g.polygon("fill", 260, 50, 238, 78, 252, 72, 262, 84, 274, 70, 284, 80)
  g.polygon("fill", 90, 70, 72, 96, 86, 90, 96, 100, 108, 92)
  g.polygon("fill", 450, 80, 434, 102, 448, 96, 458, 106, 468, 98)
  -- hills and valley floor
  ui.set(ui.c.hill)
  g.ellipse("fill", 150, 250, 300, 90)
  g.ellipse("fill", 520, 250, 280, 80)
  ui.set(ui.c.grass)
  g.rectangle("fill", 0, 230, 640, 250)
  -- the river, from the snow down through the valley
  ui.set(ui.c.water)
  g.polygon("fill", 300, 200, 322, 200, 334, 260, 300, 330, 318, 400, 290, 480, 240, 480, 276, 400, 262, 330, 300, 260)
  ui.set(ui.c.white, 0.6)
  for i = 0, 4 do
    local y = 220 + ((t * 30 + i * 52) % 260)
    g.rectangle("fill", 296 - (y - 220) * 0.08, y, 14, 3, 2, 2)
  end
  -- little bridge
  ui.set(ui.c.wood)
  g.rectangle("fill", 246, 300, 84, 12, 3, 3)
  ui.set(INK)
  g.setLineWidth(2)
  g.rectangle("line", 246, 300, 84, 12, 3, 3)
  g.setLineWidth(1)
end

-- Bazaar: a row of three stalls. Each stage opens one more; then bunting.
function M.bazaar(x, y, stage, t)
  for i = 0, 2 do
    local sx = x + i * 78
    local open = stage > i or (i == 0 and stage > 0)
    if i == 0 then open = stage >= 1 elseif i == 1 then open = stage >= 2 else open = stage >= 3 end
    box(WALL, sx, y + 46, 70, 64)
    if open then
      box(hex("6B4A2B"), sx + 6, y + 56, 58, 30)
      for k = 0, 3 do
        ui.set(GOODS[(i * 2 + k) % #GOODS + 1])
        g.circle("fill", sx + 14 + k * 14, y + 78, 7)
        outline("circle", sx + 14 + k * 14, y + 78, 7)
      end
    else
      box(hex("B9AE9B"), sx + 6, y + 56, 58, 30)
      ui.set(INK, 0.4)
      g.setLineWidth(2)
      for k = 1, 3 do g.line(sx + 6, y + 56 + k * 7.5, sx + 64, y + 56 + k * 7.5) end
      g.setLineWidth(1)
    end
    -- striped awning
    local col = open and GOODS[i * 2 + 1] or hex("C9BEA8")
    poly(col, sx - 6, y + 46, sx + 76, y + 46, sx + 68, y + 24, sx + 2, y + 24)
    ui.set(ui.c.white, open and 0.85 or 0.4)
    for k = 0, 2 do
      g.polygon("fill", sx + 8 + k * 24, y + 26, sx + 20 + k * 24, y + 26, sx + 22 + k * 24, y + 44, sx + 6 + k * 24, y + 44)
    end
  end
  if stage >= 4 then
    for k = 0, 9 do
      ui.set(GOODS[k % #GOODS + 1])
      local fx = x + k * 23 + 4
      local fy = y + 8 + math.sin(k * 0.7) * 4 + math.sin(t * 3 + k) * 1.5
      g.polygon("fill", fx, fy, fx + 14, fy, fx + 7, fy + 12)
    end
    ui.set(INK)
    g.line(x, y + 8, x + 230, y + 8)
  end
end

-- Library: a house whose open front shows shelves that fill with books.
function M.library(x, y, stage, t)
  box(WALL, x + 10, y + 40, 200, 72)
  poly(hex("3F6FA8"), x, y + 42, x + 220, y + 42, x + 190, y + 10, x + 30, y + 10)
  -- door
  box(hex("7A5230"), x + 94, y + 68, 32, 44, 4)
  -- two shelf windows
  for side = 0, 1 do
    local wx = x + 24 + side * 116
    box(hex("FFF6DC"), wx, y + 52, 56, 50)
    ui.set(INK)
    g.setLineWidth(2)
    g.line(wx, y + 68, wx + 56, y + 68)
    g.line(wx, y + 85, wx + 56, y + 85)
    g.setLineWidth(1)
    -- three shelves of eight books; how many are filled depends on the stage
    local filled = ({ [0] = 2, 7, 13, 19, 24 })[stage] or 24
    for n = 0, 23 do
      if n < filled then
        local row, colm = math.floor(n / 8), n % 8
        ui.set(GOODS[(n * 5 + side * 3) % #GOODS + 1])
        g.rectangle("fill", wx + 3 + colm * 6.4, y + 55 + row * 17, 5, 12)
      end
    end
  end
  if stage >= 4 then
    ui.set(INK)
    g.setLineWidth(2)
    g.line(x + 110, y + 10, x + 110, y - 14)
    g.setLineWidth(1)
    ui.star(x + 110, y - 16, 10, true)
  end
end

-- Workshop: a house with a water wheel. Broken and still at first; it turns
-- faster as the stage rises, and smoke rises from the chimney.
function M.workshop(x, y, stage, t)
  box(WALL2, x + 60, y + 44, 140, 70)
  poly(hex("7E57A8"), x + 50, y + 46, x + 210, y + 46, x + 184, y + 14, x + 76, y + 14)
  box(hex("7A5230"), x + 150, y + 72, 30, 42, 4)
  box(hex("FFF6DC"), x + 100, y + 62, 30, 26)
  -- chimney and smoke
  box(ROOF, x + 160, y + 4, 16, 24)
  if stage >= 2 then
    for i = 0, 2 do
      local a = (t * 0.5 + i / 3) % 1
      ui.set(ui.c.white, 0.8 * (1 - a))
      g.circle("fill", x + 168 + math.sin(a * 6 + i) * 6, y - a * 34, 5 + a * 7)
    end
  end
  -- the wheel
  local cx, cy, r = x + 48, y + 84, 36
  local spin = stage >= 1 and t * (0.4 + stage * 0.35) or 0.5
  ui.set(ui.c.wood)
  g.circle("fill", cx, cy, r)
  ui.set(ui.c.grass)
  g.circle("fill", cx, cy, r - 8)
  outline("circle", cx, cy, r)
  outline("circle", cx, cy, r - 8)
  local spokes = stage >= 1 and 8 or 5
  g.setLineWidth(4)
  for i = 0, 7 do
    if i < spokes then
      local a = spin + i * math.pi / 4
      ui.set(ui.c.wood)
      g.line(cx, cy, cx + math.cos(a) * (r - 4), cy + math.sin(a) * (r - 4))
    end
  end
  g.setLineWidth(1)
  ui.set(INK)
  g.circle("fill", cx, cy, 5)
  if stage >= 3 then
    -- a gear on the wall
    local gx, gy = x + 115, y + 100
    ui.set(GOODS[2])
    for i = 0, 5 do
      local a = -spin + i * math.pi / 3
      g.circle("fill", gx + math.cos(a) * 9, gy + math.sin(a) * 9, 3.5)
    end
    g.circle("fill", gx, gy, 8)
    outline("circle", gx, gy, 8)
  end
  if stage >= 4 then ui.star(x + 130, y + 28, 9, true) end
end

local function tree(x, y, size, fruit, sway)
  ui.set(ui.c.wood)
  g.rectangle("fill", x - 3 - size * 0.04, y - size * 0.5, 6 + size * 0.08, size * 0.5)
  if size > 14 then
    ui.set(hex("3F8A4B"))
    g.circle("fill", x + sway, y - size * 0.75, size * 0.42)
    g.circle("fill", x - size * 0.28 + sway, y - size * 0.55, size * 0.3)
    g.circle("fill", x + size * 0.28 + sway, y - size * 0.55, size * 0.3)
    outline("circle", x + sway, y - size * 0.75, size * 0.42)
    if fruit then
      ui.set(GOODS[1])
      g.circle("fill", x - size * 0.2 + sway, y - size * 0.7, 4)
      g.circle("fill", x + size * 0.18 + sway, y - size * 0.85, 4)
      g.circle("fill", x + size * 0.25 + sway, y - size * 0.55, 4)
    end
  else
    ui.set(hex("3F8A4B"))
    g.ellipse("fill", x - 5, y - size * 0.6, 6, 3.5)
    g.ellipse("fill", x + 5, y - size * 0.75, 6, 3.5)
  end
end

-- Garden: a fenced plot. Sprouts become saplings, then fruit trees and flowers.
function M.garden(x, y, stage, t)
  ui.set(hex("B98A5A"))
  g.ellipse("fill", x + 110, y + 100, 108, 22)
  local sizes = ({ [0] = 8, 22, 40, 56, 66 })[stage] or 66
  local sway = math.sin(t * 1.5) * 2
  tree(x + 40, y + 100, sizes * 0.85, stage >= 4, sway)
  tree(x + 110, y + 104, sizes, stage >= 3, -sway)
  tree(x + 180, y + 100, sizes * 0.9, stage >= 4, sway)
  if stage >= 2 then
    for i = 0, (stage - 1) * 3 do
      local fx = x + 16 + (i * 37) % 196
      local fy = y + 108 + (i % 3) * 4
      ui.set(ui.c.good)
      g.line(fx, fy, fx, fy - 8)
      ui.set(GOODS[i % #GOODS + 1])
      g.circle("fill", fx, fy - 10, 4)
    end
  end
  -- fence
  ui.set(hex("E9DCC0"))
  for i = 0, 10 do
    g.rectangle("fill", x + 4 + i * 21, y + 104, 6, 20, 2, 2)
  end
  g.rectangle("fill", x + 4, y + 110, 216, 4)
  ui.set(INK, 0.5)
  g.rectangle("line", x + 4, y + 110, 216, 4)
end

M.draw = { en = M.bazaar, fa = M.library, math = M.workshop, garden = M.garden }

-- Stage 0 to 4 from the share of the available stars already earned.
function M.stage(stars, max)
  if stars <= 0 or max <= 0 then return 0 end
  local share = stars / max
  if share >= 0.8 then return 4 elseif share >= 0.5 then return 3 elseif share >= 0.2 then return 2 end
  return 1
end

return M
