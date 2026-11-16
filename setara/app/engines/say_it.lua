-- Say It: speaking practice without a microphone.
--   1 listen   the device says the phrase (picture and caption shown)
--   2 turn     the guide bird invites the child to say it aloud while a bar fills
--   3 compare  the device says it again
--   4 judge    A = "I said it well" (thumbs up), X = once more from step 1
-- A during steps 1 to 3 skips ahead. With two children the partner judges.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local packs = require("core.packs")
local Quiz = require("core.quiz")
local g = love.graphics

local E = {}
E.__index = E

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.quiz = Quiz.new(round.items or {}, { ordered = true })
  self.phase = "wait"
  self.t = 0
  return self
end

function E:start() self:next() end

-- The builder joins the two halves of a dialogue with two spaces: one line each.
local function split(str)
  local lines = {}
  for part in (tostring(str) .. "  "):gmatch("(.-)%s%s+") do
    if part ~= "" then lines[#lines + 1] = part end
  end
  return lines
end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.lines = item.text and split(item.text) or nil
  self:listen(false)
end

function E:listen(slow)
  local item = self.item
  self.phase, self.t = "listen", 0
  local clips = self.ctx.pack and packs.clips(self.ctx.pack, item.prompt_audio) or {}
  local dur = audio.duration(clips, slow)
  self.wait = (dur > 0 and dur or 1.5) * 1.3 + 1
  self.ctx.say(item.prompt_audio, { slow = slow, after = 0.3 })
end

function E:turn()
  self.phase, self.t, self.bar = "turn", 0, nil
  audio.say(packs.string("your_turn").audio or {})
end

function E:compare()
  self.phase, self.t = "compare", 0
  self.ctx.say(self.item.prompt_audio, { after = 0.2 })
end

function E:judge()
  audio.stop()
  self.phase, self.t = "judge", 0
end

-- X. While judging it means "not yet, once more" and the item counts as not
-- right at the first try.
function E:again(slow)
  if not self.item or self.phase == "right" then return end
  if self.phase == "judge" then
    sfx.play("move")
    self.quiz:wrong()
    return self:listen(false)
  end
  self:listen(slow)
end

function E:help()
  if not self.item or self.phase == "right" then return end
  local help = self.item.help_audio
  if self.phase == "judge" then
    if help and #help > 0 then self.ctx.say(help) else self.ctx.say(self.item.prompt_audio, { slow = true }) end
  elseif help and #help > 0 then
    -- the meaning in Dari, then the phrase again from the start
    self.phase, self.t = "meaning", 0
    self.ctx.say(help, { after = 0.3 })
  else
    self:listen(true)
  end
end

function E:input(b)
  if b ~= "a" then return end
  if self.phase == "listen" or self.phase == "meaning" then self:turn()
  elseif self.phase == "turn" then self:compare()
  elseif self.phase == "compare" then self:judge()
  elseif self.phase == "judge" then
    self.phase, self.t = "right", 0
    sfx.play("right")
    audio.stop()
    self.quiz:right()
    self.ctx.next_player()
  end
end

function E:update(dt)
  self.t = self.t + dt
  local quiet = not audio.busy() and self.t > 0.15
  if self.phase == "listen" then
    if quiet then self:turn() end
  elseif self.phase == "meaning" then
    if quiet then self:listen(false) end
  elseif self.phase == "turn" then
    if self.bar then
      self.bar = self.bar + dt
      if self.bar >= self.wait then self:compare() end
    elseif quiet then
      self.bar = 0
    end
  elseif self.phase == "compare" then
    if quiet then self:judge() end
  elseif self.phase == "right" and self.t > 0.9 then
    self:next()
  end
end

-- Drawing ---------------------------------------------------------------------

local function thumbs_up(cx, cy, s)
  local skin = ui.mix(ui.c.good, ui.c.white, 0.25)
  g.setLineWidth(3)
  ui.set(skin)
  g.polygon("fill", cx - s * 0.3, cy - s * 0.1, cx - s * 0.08, cy - s * 0.85, cx + s * 0.22, cy - s * 0.8,
    cx + s * 0.2, cy - s * 0.1)
  g.rectangle("fill", cx - s * 0.35, cy - s * 0.15, s * 1.0, s * 0.8, s * 0.15, s * 0.15)
  ui.set(ui.c.ink)
  g.line(cx - s * 0.3, cy - s * 0.12, cx - s * 0.08, cy - s * 0.85, cx + s * 0.22, cy - s * 0.8, cx + s * 0.2, cy - s * 0.15)
  g.rectangle("line", cx - s * 0.35, cy - s * 0.15, s * 1.0, s * 0.8, s * 0.15, s * 0.15)
  for i = 1, 3 do
    g.line(cx + s * 0.25, cy - s * 0.15 + i * s * 0.2, cx + s * 0.65, cy - s * 0.15 + i * s * 0.2)
  end
  ui.set(ui.c.good)
  g.rectangle("fill", cx - s * 0.75, cy - s * 0.1, s * 0.3, s * 0.75, 4, 4)
  ui.set(ui.c.ink)
  g.rectangle("line", cx - s * 0.75, cy - s * 0.1, s * 0.3, s * 0.75, 4, 4)
  g.setLineWidth(1)
end

-- A round arrow: once more.
local function once_more(cx, cy, r)
  ui.set(ui.c.fa)
  g.setLineWidth(6)
  g.arc("line", "open", cx, cy, r, -math.pi * 0.35, math.pi * 1.25)
  g.setLineWidth(1)
  local a = -math.pi * 0.35
  local x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
  g.polygon("fill", x - 13, y - 9, x + 11, y - 5, x - 3, y + 13)
end

local function player_dot(n, cx, cy, color)
  ui.set(color)
  g.circle("fill", cx, cy, 17)
  ui.set(ui.c.ink)
  g.setLineWidth(2)
  g.circle("line", cx, cy, 17)
  g.setLineWidth(1)
  ui.set(ui.c.white)
  text.centered("bold", tostring(n), cx - 16, cy - 16, 32, 32, 24)
end

function E:draw()
  local item = self.item
  if not item then return end
  local phase, t = self.phase, self.t
  local talking = (phase == "listen" or phase == "compare") and audio.busy()

  -- what is being said: picture with a speaker, or a large speaker alone
  local cap_y = 232
  if item.show then
    local fill = talking and ui.mix(ui.c.paper, ui.c.gold, 0.2) or ui.c.paper
    ui.card(235, 48, 170, 170, { fill = fill })
    ui.thing(item.show, self.ctx.root, 241, 54, 158, 158)
    ui.speaker(462, 133, 64, talking and t or nil, talking and ui.c.ink or ui.c.soft)
  else
    ui.speaker(314, 120, 110, talking and t or nil, talking and ui.c.ink or ui.c.soft)
    cap_y = 196
  end

  ui.set(ui.c.ink)
  if self.lines and #self.lines > 0 then
    local h = math.min(62, (310 - cap_y) / #self.lines)
    for i, line in ipairs(self.lines) do
      text.centered("bold", line, 16, cap_y + (i - 1) * h, 608, h, 44, 24)
    end
  elseif item.fa then
    text.fa(item.fa, 20, cap_y, 600, 36, "center", true)
  end

  -- the bottom band belongs to the step
  local mood = "idle"
  if phase == "turn" then mood = audio.busy() and "talk" or "think"
  elseif phase == "right" then mood = "happy"
  elseif phase == "meaning" then mood = "talk" end
  ui.guide(84, 396, 1.5, mood, t)

  if phase == "turn" then
    -- a bar that fills while the child speaks; nothing happens if they are slower
    local x, y, w, h = 192, 378, 380, 34
    ui.card(x, y, w, h, { radius = 17, fill = ui.c.shade })
    local f = math.min(1, (self.bar or 0) / self.wait)
    if f > 0 then
      ui.set(ui.c.gold)
      g.rectangle("fill", x + 4, y + 4, math.max(26, (w - 8) * f), h - 8, 13, 13)
    end
    -- sound leaving the bird's beak: now you
    ui.set(ui.c.en, 0.5 + 0.5 * math.sin(t * 6))
    g.setLineWidth(4)
    for i = 1, 3 do g.arc("line", "open", 140, 392, 8 + i * 9, -0.6, 0.6) end
    g.setLineWidth(1)
    ui.badge("a", 600, 395, 13)
  elseif phase == "judge" or phase == "right" then
    local pulse = phase == "judge" and math.sin(t * 5) * 2 or 0
    local grow = phase == "right" and math.sin(math.min(1, t * 3) * math.pi) * 8 or 0
    if self.ctx.pair and phase == "judge" then
      -- the partner decides
      player_dot(3 - (self.ctx.player or 1), 266, 334, ui.c[self.ctx.pack and self.ctx.pack.subject or "en"] or ui.c.en)
    end
    ui.card(176 - grow, 356 - grow, 180 + grow * 2, 100 + grow * 2,
      { fill = phase == "right" and ui.mix(ui.c.paper, ui.c.good, 0.35) or ui.c.paper,
        border = phase == "right" and ui.c.good or ui.c.ink, width = phase == "right" and 6 or 3 })
    ui.badge("a", 218, 406, 20 + pulse)
    thumbs_up(300, 414, 50)
    if phase == "judge" then
      ui.card(400, 356, 180, 100)
      ui.badge("x", 442, 406, 20)
      once_more(522, 408, 24)
    end
  else
    ui.badge("a", 600, 440, 13)
    ui.arrow("right", 624, 440, 7, ui.c.soft)
  end
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
