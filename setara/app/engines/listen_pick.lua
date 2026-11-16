-- Listen and Pick: hear a word or question, press the direction of the right
-- picture.
local ui = require("core.ui")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local common = require("engines.common")

local E = {}
E.__index = E

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.quiz = Quiz.new(round.items, { draw = round.draw })
  self.phase = "wait"
  self.t = 0
  return self
end

function E:start() self:next() end

function E:next()
  local item = self.quiz:current()
  if not item then
    self.finished = true
    return
  end
  self.item = item
  self.slots = common.deal(item, self.quiz.level)
  if not self.slots then
    -- a question that cannot be asked is passed over, never shown
    self.quiz:right()
    return self:next()
  end
  self.wrong = {}
  self.misses, self.show_right = 0, false
  self.phase = "ask"
  self.t = 0
  self:again(false)
end

function E:again(slow)
  if self.item then self.ctx.say(common.prompt_clips(self.item, self.slots), { slow = slow }) end
end

function E:help()
  if not self.item then return end
  if self.item.help_audio and #self.item.help_audio > 0 then
    self.ctx.say(self.item.help_audio)
  else
    self:again(true)
  end
end

function E:input(b)
  if self.phase ~= "ask" then return end
  if b == "a" then return self:again(false) end
  local slot = self.slots[b]
  if not slot or self.wrong[b] then return end
  if slot.right then
    self.phase, self.t, self.picked = "right", 0, b
    sfx.play("right")
    audio.stop()
    if not self.quiz.tried and self.ctx.solved then self.ctx.solved(self.item) end
    self.quiz:right()
    self.ctx.next_player()
  else
    self.wrong[b] = true
    self.shake, self.shake_t = b, 0.4
    sfx.play("wrong")
    self.quiz:wrong()
    if self.ctx.missed then self.ctx.missed(self.item) end
    self.misses = (self.misses or 0) + 1
    -- A wrong answer is answered: the first time the question is said again,
    -- the second time the explanation comes by itself and the right card is
    -- shown, so that nobody finishes a round by trying every card.
    if self.misses >= 2 and self.item.help_audio and #self.item.help_audio > 0 then
      self.show_right = true
      self.ctx.say(self.item.help_audio)
    else
      if self.misses >= 2 then self.show_right = true end
      self:again(false)
    end
  end
end

function E:update(dt)
  self.t = self.t + dt
  if self.shake_t then
    self.shake_t = self.shake_t - dt
    if self.shake_t <= 0 then self.shake, self.shake_t = nil, nil end
  end
  if self.phase == "right" and self.t > 0.9 then self:next() end
end

function E:draw()
  if not self.item then return end
  common.draw_center(self.ctx.root, self.item, audio.busy(), self.t)
  for dir, slot in pairs(self.slots) do
    local state
    if self.phase == "right" and dir == self.picked then state = "right"
    elseif self.shake == dir then state = "shake"
    elseif self.show_right and slot.right and self.phase == "ask" then state = "hint"
    elseif self.wrong[dir] then state = "wrong" end
    common.draw_slot(self.ctx.root, slot, state, self.t)
  end
end

function E:stars() return self.quiz:stars() end
function E:counts() return self.quiz.attempts, self.quiz.first_right end
function E:progress() return self.quiz.done, self.quiz.total end

return E
