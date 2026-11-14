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

-- English mode, for testers and partners who do not read Dari: wherever a
-- Dari text would be drawn, its English is drawn instead. M.dict maps a Dari
-- text exactly as it is drawn (lines joined by "\n") to English; the builder
-- fills it from content/i18n. A text with no English stays in Dari.
M.locale = "fa"
M.dict = {}

local function english(lines)
  if M.locale ~= "en" then return nil end
  if type(lines) == "table" then lines = table.concat(lines, "\n") end
  return M.dict[lines]
end
M.english = english

local function english_size(size) return math.max(16, math.floor((size or 30) * 0.72 + 0.5)) end

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
  local en = english(lines)
  if en then
    local f = M.font(bold and "bold" or "latin", english_size(size))
    love.graphics.setFont(f)
    love.graphics.printf(en, x, y + 6, w, align == "center" and "center" or "left")
    local _, wrapped = f:getWrap(en, w)
    return #wrapped * f:getHeight() + 8
  end
  if type(lines) == "string" then lines = { lines } end
  local f = M.font(bold and "fabold" or "fa", size or 30)
  love.graphics.setFont(f)
  local step = math.floor(f:getHeight() * 0.86)
  align = align or "right"
  for i, line in ipairs(lines or {}) do
    -- The line is already in drawing order: wrapping it again would move its
    -- first word below its last. A line that is too wide is narrowed instead.
    local lw = f:getWidth(line)
    local s = lw > w and w / lw or 1
    local lx = x
    if align == "right" then lx = x + w - lw * s elseif align == "center" then lx = x + (w - lw * s) / 2 end
    love.graphics.print(line, lx, y + (i - 1) * step, 0, s, 1)
  end
  return #(lines or {}) * step
end

function M.fa_height(lines, size, w)
  local en = english(lines)
  if en then
    local f = M.font("latin", english_size(size))
    local _, wrapped = f:getWrap(en, w or 588)
    return #wrapped * f:getHeight() + 8
  end
  if type(lines) == "string" then lines = { lines } end
  return #(lines or {}) * math.floor(M.font("fa", size or 30):getHeight() * 0.86)
end

-- One line centred in a box, as large as fits. kind: latin, bold, fa, fabold.
function M.centered(kind, str, x, y, w, h, max_size, min_size)
  if kind == "fa" or kind == "fabold" then
    local en = english(str)
    if en then
      kind, str = kind == "fabold" and "bold" or "latin", en
      max_size = math.max(16, math.floor((max_size or 96) * 0.8))
    end
  end
  local f = M.fit(kind, str, w - 8, h - 4, max_size, min_size)
  love.graphics.setFont(f)
  -- one line, never wrapped: narrowed if even the smallest size is too wide
  local lw = f:getWidth(str)
  local s = lw > w - 4 and (w - 4) / lw or 1
  love.graphics.print(str, x + (w - lw * s) / 2, y + (h - f:getHeight()) / 2, 0, s, 1)
end

return M
