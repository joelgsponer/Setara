-- My class: what the teacher needs to see at a glance. First the games of
-- today's lesson (unit N of the learner pack belongs to lesson N), then the
-- rounds this device's children found hardest, then how the last Quick
-- Checks went. A starts a round on the loudspeaker for the whole class.
-- Only counts: nothing here is about a single child.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local T = require("teacher.common")
local g = love.graphics

local Class = {}
Class.__index = Class

local function unit_of(id)
  return tonumber(tostring(id):match("%-(%d+)%a*%-%a+$")) or 0
end

-- every round of every learner pack, with its game and pack
local function all_rounds()
  local out = {}
  for _, subject in pairs(packs.subjects) do
    for _, pack in pairs(subject) do
      for _, game in ipairs(pack.all_games or pack.games or {}) do
        for _, id in ipairs(game.rounds or {}) do
          out[id] = { id = id, game = game, pack = game.pack or pack, level_pack = pack }
        end
      end
    end
  end
  return out
end

function Class.new()
  local self = setmetatable({ t = 0, sel = 1, rows = {} }, Class)
  local rounds = all_rounds()
  -- 1. today's lesson
  local tp, n = T.pack(), T.lesson_number()
  local learner = tp and packs.subjects[tp.subject] and packs.subjects[tp.subject][tp.level]
  if learner and n then
    for _, game in ipairs(learner.games or {}) do
      for _, id in ipairs(game.rounds or {}) do
        if unit_of(id) == n then
          self.rows[#self.rows + 1] = { kind = "today", round = rounds[id] }
          break
        end
      end
    end
  end
  -- 2. the hardest rounds: fewest first-try answers, among rounds really played
  local hard = {}
  for id, r in pairs(store.stats.rounds or {}) do
    if rounds[id] and (r.attempts or 0) >= 8 then
      hard[#hard + 1] = { kind = "hard", round = rounds[id], pct = math.floor(100 * (r.correct or 0) / r.attempts + 0.5), plays = r.plays }
    end
  end
  table.sort(hard, function(a, b) return a.pct < b.pct end)
  for i = 1, math.min(8, #hard) do
    if hard[i].pct < 80 then self.rows[#self.rows + 1] = hard[i] end
  end
  -- 3. Quick Checks, the weakest first
  local checks = {}
  for lesson, c in pairs(store.stats.checks or {}) do
    if (c.size or 0) > 0 then
      checks[#checks + 1] = { kind = "check", lesson = tostring(lesson), pct = math.floor(100 * c.right / c.size + 0.5), times = c.times }
    end
  end
  table.sort(checks, function(a, b) return a.pct < b.pct end)
  for i = 1, math.min(6, #checks) do self.rows[#self.rows + 1] = checks[i] end
  return self
end

function Class:update(dt) self.t = self.t + dt end
function Class:leave() T.stop() end

function Class:input(b)
  local row = self.rows[self.sel]
  if b == "b" then app.pop()
  elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
  elseif b == "down" and self.sel < #self.rows then self.sel = self.sel + 1 sfx.play("move")
  elseif b == "a" and row and row.round then
    store.count_teacher("class_start")
    local r = row.round
    app.push(require("scenes.play").new({ pack = r.pack, game = r.game, round_id = r.id, level_pack = r.level_pack }))
  end
end

local function bar(x, y, w, pct)
  ui.set(ui.c.line)
  g.rectangle("fill", x, y, w, 12, 6, 6)
  ui.set(pct < 50 and ui.c.bad or pct < 80 and ui.c.gold or ui.c.good)
  g.rectangle("fill", x, y, math.max(6, w * pct / 100), 12, 6, 6)
end

function Class:draw()
  T.header("class_title")
  if #self.rows == 0 then
    local s = T.S("class_empty")
    T.dari_card(s.fa or {}, 60, 180, 520)
    return
  end
  local first = math.max(1, math.min(self.sel - 2, #self.rows - 5))
  local last_kind
  for i = first, math.min(#self.rows, first + 5) do
    local row = self.rows[i]
    local y = 50 + (i - first) * 65
    ui.card(14, y, 612, 60, { selected = i == self.sel, fill = i == self.sel and ui.c.shade or ui.c.paper })
    -- what kind of line: today's lesson, a hard round, a Quick Check
    local tag = T.S("class_" .. row.kind)
    ui.set(ui.c.soft)
    if text.locale == "en" then text.print(tag.en or "", 80, y + 4, 300, "left", 14, true)
    elseif tag.fa and tag.fa[1] then text.fa(tag.fa, 330, y - 2, 280, 18, "right") end
    if row.round then
      local r = row.round
      ui.set(ui.c[r.level_pack.subject or "en"] or ui.c.teacher)
      g.rectangle("fill", 22, y + 8, 44, 44, 8, 8)
      ui.set(ui.c.white)
      text.centered("bold", tostring(unit_of(r.id)), 22, y + 8, 44, 44, 24)
      ui.set(ui.c.ink)
      text.print(r.game.title_en or "", 80, y + 24, 260, "left", 20, true)
      if r.game.title_fa and r.game.title_fa[1] and text.locale ~= "en" then
        text.fa(r.game.title_fa, 300, y + 18, 220, 24, "right", true)
      end
      if row.pct then
        bar(530, y + 26, 80, row.pct)
      else
        ui.badge("a", 592, y + 32, 13)
      end
    else
      ui.set(ui.c.teacher)
      text.print(row.lesson:gsub("^teacher%-", ""), 28, y + 22, 300, "left", 20, true)
      bar(430, y + 26, 180, row.pct)
    end
    last_kind = row.kind
  end
  T.hints({ { "a", "hint_start" }, { "updown", "hint_next" } })
end

return Class
