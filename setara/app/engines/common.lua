-- Pieces shared by the choice games (listen_pick, journey, duel).
local ui = require("core.ui")
local Quiz = require("core.quiz")
local M = {}
local g = love.graphics

-- Where the choices sit: up, down, left and right of the centre, so that one
-- press of the D-pad answers.
local SLOTS = {
  up = { x = 250, y = 46, w = 140, h = 130 },
  left = { x = 44, y = 180, w = 140, h = 130 },
  right = { x = 456, y = 180, w = 140, h = 130 },
  down = { x = 250, y = 342, w = 140, h = 130 },
}
M.SLOTS = SLOTS
M.CENTER = { x = 250, y = 184, w = 140, h = 150 }
local ORDER = { [2] = { "left", "right" }, [3] = { "left", "up", "right" }, [4] = { "up", "left", "right", "down" } }

local function is_answer(thing, answer)
  return (type(thing) == "table" and thing.id or thing) == answer
end

-- Pick the answer plus (level - 1) wrong choices and deal them to slots.
-- Returns nil for a question that cannot be asked (no right choice, or
-- nothing to choose between); the engines skip such an item.
function M.deal(item, level)
  local right, wrong = nil, {}
  for _, c in ipairs(type(item.choices) == "table" and item.choices or {}) do
    if is_answer(c, item.answer) and not right then right = c
    elseif not is_answer(c, item.answer) then wrong[#wrong + 1] = c end
  end
  if not right or #wrong == 0 then return nil end
  Quiz.shuffle(wrong)
  local n = math.max(2, math.min(level, #wrong + 1, 4))
  local picked = { right }
  for i = 1, n - 1 do picked[#picked + 1] = wrong[i] end
  Quiz.shuffle(picked)
  local slots = {}
  for i, dir in ipairs(ORDER[#picked] or ORDER[2]) do
    local s = SLOTS[dir]
    slots[dir] = { dir = dir, thing = picked[i], x = s.x, y = s.y, w = s.w, h = s.h,
      right = is_answer(picked[i], item.answer) }
  end
  return slots
end

-- The question, then every choice that has a voice (written words), in the
-- order up, left, right, down. The choice being read is lit by draw_slot.
function M.prompt_clips(item, slots)
  local clips = {}
  for _, c in ipairs(item.prompt_audio or {}) do clips[#clips + 1] = c end
  for _, dir in ipairs({ "up", "left", "right", "down" }) do
    local slot = slots and slots[dir]
    local voice = slot and type(slot.thing) == "table" and slot.thing.audio
    for _, c in ipairs(type(voice) == "table" and voice or {}) do clips[#clips + 1] = c end
  end
  return clips
end

local function being_read(root, slot)
  local voice = type(slot.thing) == "table" and slot.thing.audio
  local playing = voice and voice[1] and require("core.audio").playing()
  return playing ~= nil and playing == root .. voice[1]
end

-- state: nil, "right", "wrong" (crossed out), "shake"
function M.draw_slot(root, slot, state, t)
  local x, y = slot.x, slot.y
  if not state and being_read(root, slot) then
    ui.card(x - 4, y - 4, slot.w + 8, slot.h + 8, { selected = true })
    ui.thing(slot.thing, root, x + 2, y + 2, slot.w - 4, slot.h - 4)
    return
  end
  if state == "shake" then x = x + math.sin(t * 50) * 6 end
  local opts = {}
  if state == "right" then
    opts.fill = ui.mix(ui.c.paper, ui.c.good, 0.35)
    opts.border = ui.c.good
    opts.width = 6
    local grow = math.sin(math.min(1, t * 3) * math.pi) * 6
    x, y = x - grow, y - grow
    ui.card(x, y, slot.w + grow * 2, slot.h + grow * 2, opts)
    ui.thing(slot.thing, root, x + 6, y + 6, slot.w + grow * 2 - 12, slot.h + grow * 2 - 12)
    return
  end
  if state == "wrong" then opts.dim = true end
  if state == "hint" then   -- "this one": a slow gold pulse around the right card
    local pulse = 3 + math.sin(t * 5) * 3
    ui.card(x - pulse, y - pulse, slot.w + pulse * 2, slot.h + pulse * 2, { border = ui.c.gold, width = 5, fill = ui.c.paper })
  end
  ui.card(x, y, slot.w, slot.h, opts)
  ui.thing(slot.thing, root, x + 6, y + 6, slot.w - 12, slot.h - 12, { alpha = state == "wrong" and 0.35 or 1 })
end

-- The question in the middle: the shown thing, or a speaker while it talks.
function M.draw_center(root, item, talking, t)
  local c = M.CENTER
  if item and item.show then
    ui.card(c.x, c.y, c.w, c.h, { fill = ui.c.shade, border = ui.c.line })
    ui.thing(item.show, root, c.x + 6, c.y + 6, c.w - 12, c.h - 12)
  else
    ui.speaker(c.x + c.w / 2 - 6, c.y + c.h / 2, 84, talking and t or nil, ui.c.ink)
  end
end

return M
