-- Shared drawing: colours, cards, things, stars, the guide bird.
local text = require("core.text")
local M = {}
local g = love.graphics

M.W, M.H = 640, 480

local function hex(h)
  return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 }
end

M.c = {
  bg = hex("F6EEDC"), paper = hex("FFFBF0"), ink = hex("3B2F2F"), soft = hex("8A7B6A"),
  line = hex("D8CBB0"), gold = hex("F2B705"), good = hex("4E9A51"), bad = hex("C8553D"),
  sky = hex("BFE3F0"), grass = hex("9CCB7A"), hill = hex("7FB069"), earth = hex("C9A66B"),
  white = hex("FFFFFF"), shade = hex("E9DEC6"), water = hex("5DA9D6"), wood = hex("9A6B3F"),
  en = hex("E07A3F"), fa = hex("3F7FBF"), math = hex("8E5BB5"), garden = hex("4E9A51"),
  teacher = hex("2F6F73"),
}

function M.set(c, a)
  g.setColor(c[1], c[2], c[3], a or 1)
end

function M.mix(a, b, t)
  return { a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t }
end

-- A rounded card. opts: fill, border, width, selected, dim, radius
function M.card(x, y, w, h, opts)
  opts = opts or {}
  local r = opts.radius or 14
  M.set(M.c.ink, 0.12)
  g.rectangle("fill", x + 2, y + 4, w, h, r, r)
  M.set(opts.fill or M.c.paper)
  g.rectangle("fill", x, y, w, h, r, r)
  if opts.selected then
    g.setLineWidth(6)
    M.set(M.c.gold)
  else
    g.setLineWidth(opts.width or 3)
    M.set(opts.border or M.c.ink)
  end
  g.rectangle("line", x, y, w, h, r, r)
  if opts.dim then
    M.set(M.c.bg, 0.7)
    g.rectangle("fill", x, y, w, h, r, r)
  end
  g.setLineWidth(1)
end

-- Pictures ------------------------------------------------------------------

local images = {}

function M.image(path)
  local img = images[path]
  if img == nil then
    local ok, res = pcall(g.newImage, path)
    img = ok and res or false
    if img then img:setFilter("linear", "linear") end
    images[path] = img
  end
  return img or nil
end

function M.clear_images()
  images = {}
end

function M.draw_image(img, x, y, w, h)
  local s = math.min(w / img:getWidth(), h / img:getHeight())
  g.draw(img, x + (w - img:getWidth() * s) / 2, y + (h - img:getHeight() * s) / 2, 0, s, s)
end

-- A speaker with sound waves; t animates the waves while something plays.
function M.speaker(cx, cy, size, t, color)
  local s = size / 2
  M.set(color or M.c.ink)
  g.polygon("fill", cx - s * 0.7, cy - s * 0.25, cx - s * 0.3, cy - s * 0.25, cx + s * 0.1, cy - s * 0.6,
    cx + s * 0.1, cy + s * 0.6, cx - s * 0.3, cy + s * 0.25, cx - s * 0.7, cy + s * 0.25)
  g.setLineWidth(math.max(2, size / 14))
  for i = 1, 3 do
    local on = not t or (math.floor(t * 4) % 4) >= i
    M.set(color or M.c.ink, on and 1 or 0.25)
    g.arc("line", "open", cx + s * 0.1, cy, s * (0.3 + i * 0.22), -0.7, 0.7)
  end
  g.setLineWidth(1)
end

-- A "thing" from a level file: picture, counted pictures, Latin or Dari text,
-- or a sound card. root is the pack's folder. Drawn inside the box.
function M.thing(thing, root, x, y, w, h, opts)
  opts = opts or {}
  if type(thing) == "string" then thing = { id = thing, img = "img/" .. thing .. ".png" } end
  local color = opts.color or M.c.ink
  if thing.img then
    local img = M.image(root .. thing.img)
    if not img then
      M.set(M.c.soft)
      text.centered("latin", "?", x, y, w, h, 56)
      return
    end
    g.setColor(1, 1, 1, opts.alpha or 1)
    local n = thing.n or 1
    if n == 1 then
      M.draw_image(img, x + 4, y + 4, w - 8, h - 8)
    else
      -- Counted pictures in rows of at most five, so they can be counted.
      local cols = n <= 4 and 2 or n <= 9 and 3 or n <= 16 and 4 or 5
      if n <= 3 then cols = n end
      local rows = math.ceil(n / cols)
      local cell = math.min((w - 8) / cols, (h - 8) / rows)
      local ox = x + (w - cell * cols) / 2
      local oy = y + (h - cell * rows) / 2
      for i = 0, n - 1 do
        M.draw_image(img, ox + (i % cols) * cell + 1, oy + math.floor(i / cols) * cell + 1, cell - 2, cell - 2)
      end
    end
  elseif thing.fa then
    M.set(color, opts.alpha)
    text.centered("fabold", thing.fa, x, y, w, h, opts.max_size or 96, 24)
  elseif thing.t then
    M.set(color, opts.alpha)
    text.centered("bold", thing.t, x, y, w, h, opts.max_size or 72, 20)
  elseif thing.snd then
    M.speaker(x + w / 2, y + h / 2, math.min(w, h) * 0.6, opts.t, color)
  end
end

-- Stars -----------------------------------------------------------------------

function M.star(cx, cy, r, filled, alpha)
  local pts = {}
  for i = 0, 9 do
    local a = -math.pi / 2 + i * math.pi / 5
    local rr = (i % 2 == 0) and r or r * 0.45
    pts[#pts + 1] = cx + math.cos(a) * rr
    pts[#pts + 1] = cy + math.sin(a) * rr
  end
  local tris = love.math.triangulate(pts)
  if filled then M.set(M.c.gold, alpha) else M.set(M.c.shade, alpha) end
  for _, t in ipairs(tris) do g.polygon("fill", t) end
  M.set(M.c.ink, alpha)
  g.setLineWidth(math.max(1.5, r / 9))
  g.polygon("line", pts)
  g.setLineWidth(1)
end

function M.stars(cx, cy, r, count, of)
  of = of or 3
  local gap = r * 2.3
  for i = 1, of do
    M.star(cx + (i - (of + 1) / 2) * gap, cy, r, i <= count)
  end
end

-- The guide: a small round bird. mood: idle, happy, think, talk.
function M.guide(cx, cy, s, mood, t)
  t = t or 0
  local bob = math.sin(t * 3) * 2 * s
  if mood == "happy" then bob = -math.abs(math.sin(t * 9)) * 8 * s end
  cy = cy + bob
  g.setLineWidth(3 * s)
  -- tail
  M.set(M.c.wood)
  g.polygon("fill", cx - 22 * s, cy + 2 * s, cx - 40 * s, cy - 8 * s, cx - 36 * s, cy + 10 * s)
  -- body
  M.set(hex("E8B04A"))
  g.ellipse("fill", cx, cy, 26 * s, 23 * s)
  M.set(M.c.ink)
  g.ellipse("line", cx, cy, 26 * s, 23 * s)
  -- belly
  M.set(M.c.paper)
  g.ellipse("fill", cx + 4 * s, cy + 7 * s, 15 * s, 12 * s)
  -- wing
  M.set(M.c.wood)
  local flap = mood == "happy" and math.sin(t * 18) * 5 * s or 0
  g.ellipse("fill", cx - 8 * s, cy + 2 * s - flap, 11 * s, 8 * s)
  -- beak
  M.set(M.c.en)
  local open = (mood == "talk") and (math.sin(t * 16) > 0) and 4 * s or 0
  g.polygon("fill", cx + 22 * s, cy - 6 * s, cx + 36 * s, cy - 2 * s - open, cx + 22 * s, cy)
  g.polygon("fill", cx + 22 * s, cy, cx + 34 * s, cy + 1 * s + open, cx + 22 * s, cy + 4 * s)
  -- eye
  M.set(M.c.white)
  g.circle("fill", cx + 11 * s, cy - 8 * s, 6 * s)
  M.set(M.c.ink)
  local blink = (t % 3.5) > 3.35
  if blink then
    g.line(cx + 6 * s, cy - 8 * s, cx + 16 * s, cy - 8 * s)
  else
    g.circle("fill", cx + 12 * s, cy - 8 * s, 3 * s)
  end
  -- feet
  g.line(cx - 4 * s, cy + 22 * s, cx - 4 * s, cy + 29 * s)
  g.line(cx + 7 * s, cy + 22 * s, cx + 7 * s, cy + 29 * s)
  g.setLineWidth(1)
end

-- A round button badge, to show which button does what without words.
local badge_colors = { a = "4E9A51", b = "C8553D", x = "3F7FBF", y = "E0A82E", l = "8A7B6A", r = "8A7B6A", start = "8A7B6A" }
function M.badge(button, cx, cy, r)
  r = r or 13
  M.set(hex(badge_colors[button] or "8A7B6A"))
  g.circle("fill", cx, cy, r)
  M.set(M.c.ink)
  g.setLineWidth(2)
  g.circle("line", cx, cy, r)
  g.setLineWidth(1)
  M.set(M.c.white)
  local label = button == "start" and "≡" or button:upper()
  text.centered("bold", label, cx - r, cy - r - 1, r * 2, r * 2, 20)
end

-- Arrow head pointing up, down, left or right.
function M.arrow(dir, cx, cy, s, color)
  M.set(color or M.c.ink)
  local rot = ({ up = 0, right = math.pi / 2, down = math.pi, left = -math.pi / 2 })[dir] or 0
  g.push()
  g.translate(cx, cy)
  g.rotate(rot)
  g.polygon("fill", 0, -s, s * 0.9, s * 0.5, -s * 0.9, s * 0.5)
  g.pop()
end

-- Dots along the top: how far through the round we are.
function M.progress(done, total, x, y, w)
  if total <= 0 then return end
  local gap = math.min(22, w / total)
  local ox = x + (w - gap * (total - 1)) / 2
  for i = 1, total do
    if i <= done then M.set(M.c.gold) else M.set(M.c.line) end
    g.circle("fill", ox + (i - 1) * gap, y, 6)
    M.set(M.c.ink, 0.5)
    g.circle("line", ox + (i - 1) * gap, y, 6)
  end
end

function M.background(color)
  M.set(color or M.c.bg)
  g.rectangle("fill", 0, 0, M.W, M.H)
end

-- A title bar with a colour band. Dari title on the right, Latin on the left.
function M.header(color, title_en, title_fa)
  M.set(color)
  g.rectangle("fill", 0, 0, M.W, 44)
  M.set(M.c.white)
  if title_en then text.print(title_en, 14, 6, 400, "left", 24, true) end
  if title_fa then text.fa(title_fa, 240, 2, 386, 24, "right", true) end
end

return M
