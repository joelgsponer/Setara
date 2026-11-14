-- Fonts and text drawing. Latin text uses Andika, a typeface made for
-- beginning readers. Dari uses Noto Naskh Arabic: the builder has already
-- joined the letters and put them in drawing order, so the app only prints
-- the lines it is given.
local M = {}

local FILES = {
  latin = "assets/fonts/Andika-Regular.ttf",
  bold = "assets/fonts/Andika-Bold.ttf",
  fa = "assets/fonts/NotoNaskhArabic-Medium.ttf",
  fabold = "assets/fonts/NotoNaskhArabic-Bold.ttf",
}
local SIZES = { 16, 20, 24, 30, 36, 44, 56, 72, 96, 128 }
local cache = {}

function M.font(kind, size)
  local key = kind .. size
  local f = cache[key]
  if not f then
    f = love.graphics.newFont(FILES[kind], size)
    if kind == "fa" or kind == "fabold" then
      f:setFallbacks(M.font(kind == "fa" and "latin" or "bold", math.floor(size * 0.8)))
    end
    cache[key] = f
  end
  return f
end

-- Largest standard size at which str fits in w by h.
function M.fit(kind, str, w, h, max_size, min_size)
  for i = #SIZES, 1, -1 do
    local size = SIZES[i]
    if size <= (max_size or 128) then
      local f = M.font(kind, size)
      -- The Naskh line box is much taller than its letters: fit Dari by the
      -- height of the letters, or it comes out needlessly small.
      local tall = (kind == "fa" or kind == "fabold") and size * 1.3 or f:getHeight()
      if (f:getWidth(str) <= w and tall <= h) or size <= (min_size or 16) then
        return f, size
      end
    end
  end
  return M.font(kind, SIZES[1]), SIZES[1]
end

-- Latin text. align: left, center, right.
function M.print(str, x, y, w, align, size, bold)
  local f = M.font(bold and "bold" or "latin", size or 24)
  love.graphics.setFont(f)
  love.graphics.printf(str, x, y, w, align or "left")
  local _, lines = f:getWrap(str, w)
  return #lines * f:getHeight()
end

-- Dari text: a list of ready-to-draw lines (or one line). Right aligned by
-- default. Returns the height used.
function M.fa(lines, x, y, w, size, align, bold)
  if type(lines) == "string" then lines = { lines } end
  local f = M.font(bold and "fabold" or "fa", size or 30)
  love.graphics.setFont(f)
  local step = math.floor(f:getHeight() * 0.86)
  for i, line in ipairs(lines or {}) do
    love.graphics.printf(line, x, y + (i - 1) * step, w, align or "right")
  end
  return #(lines or {}) * step
end

function M.fa_height(lines, size)
  if type(lines) == "string" then lines = { lines } end
  return #(lines or {}) * math.floor(M.font("fa", size or 30):getHeight() * 0.86)
end

-- One line centred in a box, as large as fits. kind: latin, bold, fa, fabold.
function M.centered(kind, str, x, y, w, h, max_size, min_size)
  local f = M.fit(kind, str, w - 8, h - 4, max_size, min_size)
  love.graphics.setFont(f)
  love.graphics.printf(str, x, y + (h - f:getHeight()) / 2, w, "center")
end

return M
