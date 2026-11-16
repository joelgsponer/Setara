-- Buttons on the glass, for phones and tablets. The app is the same as on
-- the handheld: eleven buttons. On a touch screen they are drawn beside the
-- picture (lying phone) or below it (standing phone) and pressed with the
-- thumbs. Several fingers at once work, so holding L and R opens teacher
-- mode as on the device.
local input = require("core.input")
local ui = require("core.ui")
local g = love.graphics

local M = { on = false, buttons = {}, fingers = {}, canvas = { x = 0, y = 0, s = 1 } }

function M.init()
  local os_name = love.system.getOS()
  M.on = os_name == "Android" or os_name == "iOS" or os.getenv("SETARA_TOUCH") ~= nil
end

local function add(name, x, y, r)
  M.buttons[#M.buttons + 1] = { name = name, x = x, y = y, r = r }
end

-- a cross of four and a diamond of four, each around a centre
local function cross(cx, cy, d, r)
  add("up", cx, cy - d, r) add("down", cx, cy + d, r) add("left", cx - d, cy, r) add("right", cx + d, cy, r)
end
local function diamond(cx, cy, d, r)
  add("x", cx, cy - d, r) add("b", cx, cy + d, r) add("y", cx - d, cy, r) add("a", cx + d, cy, r)
end

-- Works out where the picture and the buttons go for a window of w x h.
function M.layout(w, h)
  M.w, M.h = w, h
  M.buttons = {}
  local c = M.canvas
  if not M.on then
    c.s = math.min(w / ui.W, h / ui.H)
    c.x, c.y = (w - ui.W * c.s) / 2, (h - ui.H * c.s) / 2
    return
  end
  if w >= h then
    -- lying: the picture in the middle, a bar for each thumb
    local bar = math.max(w * 0.17, (w - h * ui.W / ui.H) / 2)
    c.s = math.min((w - 2 * bar) / ui.W, h / ui.H)
    bar = (w - ui.W * c.s) / 2
    c.x, c.y = bar, (h - ui.H * c.s) / 2
    local r = math.min(bar * 0.17, h * 0.085)
    local d = r * 1.75
    local cy = h * 0.6
    cross(bar / 2, cy, d, r)
    diamond(w - bar / 2, cy, d, r)
    local small = r * 0.8
    add("l", bar / 2, h * 0.12, small)
    add("r", w - bar / 2, h * 0.12, small)
    add("start", w - bar / 2, h * 0.93, small * 0.9)
  else
    -- standing: the picture on top, the buttons under it
    c.s = w / ui.W
    c.x, c.y = 0, math.min(h * 0.06, (h - ui.H * c.s) * 0.2)
    local top = c.y + ui.H * c.s
    local room = h - top
    local r = math.min(w * 0.085, room * 0.11)
    local d = r * 1.75
    local cy = top + room * 0.58
    cross(w * 0.25, cy, d, r)
    diamond(w * 0.75, cy, d, r)
    local small = r * 0.8
    add("l", w * 0.14, top + room * 0.14, small)
    add("r", w * 0.86, top + room * 0.14, small)
    add("start", w * 0.5, top + room * 0.14, small)
  end
end

local function hit(x, y)
  local best, best_d
  for _, b in ipairs(M.buttons) do
    local dx, dy = x - b.x, y - b.y
    local d = math.sqrt(dx * dx + dy * dy)
    if d <= b.r * 1.45 and (not best_d or d < best_d) then best, best_d = b, d end
  end
  return best
end

function M.pressed(id, x, y)
  if not M.on then M.on = true M.layout(g.getDimensions()) end   -- the first touch brings the buttons
  local b = hit(x, y)
  if b then
    M.fingers[id] = b.name
    input.fake(b.name, true)
  end
end

function M.released(id)
  local name = M.fingers[id]
  if not name then return end
  M.fingers[id] = nil
  for _, other in pairs(M.fingers) do
    if other == name then return end   -- another finger still holds it
  end
  input.fake_release(name)
end

-- a finger that slides off its button lets go; sliding on the cross moves on
function M.moved(id, x, y)
  local name = M.fingers[id]
  if not name then return end
  local b = hit(x, y)
  if not b or b.name ~= name then
    M.released(id)
    local dirs = { up = true, down = true, left = true, right = true }
    if b and dirs[name] and dirs[b.name] then M.pressed(id, x, y) end
  end
end

local ARROW = { up = true, down = true, left = true, right = true }

function M.draw()
  if not M.on then return end
  for _, b in ipairs(M.buttons) do
    local held = input.down[b.name] ~= nil
    if ARROW[b.name] then
      ui.set(held and ui.c.gold or ui.c.paper, held and 1 or 0.9)
      g.circle("fill", b.x, b.y, b.r)
      ui.set(ui.c.ink)
      g.setLineWidth(3)
      g.circle("line", b.x, b.y, b.r)
      g.setLineWidth(1)
      ui.arrow(b.name, b.x, b.y, b.r * 0.42, ui.c.ink)
    else
      ui.badge(b.name, b.x, b.y, b.r * (held and 1.12 or 1))
    end
  end
end

return M
