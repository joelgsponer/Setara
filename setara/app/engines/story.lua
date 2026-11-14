-- Story: an illustrated audio story with decisions. The items are the pages,
-- in order. A page is spoken and its caption is lit while it is spoken; A
-- turns the page (A during speech stops it), left goes back one page.
-- A page with choices is a decision: left/right move the gold border, A
-- chooses. The right choice continues the story; a wrong one shows what
-- happens, explains, and asks again with that card dimmed.
local ui = require("core.ui")
local text = require("core.text")
local sfx = require("core.sfx")
local audio = require("core.audio")
local Quiz = require("core.quiz")
local g = love.graphics

local E = {}
E.__index = E

local TOP, BOTTOM = 46, 472
local CARD_H = 150

local function has(list) return type(list) == "table" and #list > 0 end

local function is_decision(page)
  return has(page.choices) and #page.choices >= 2
end

function E.new(round, ctx)
  local self = setmetatable({}, E)
  self.ctx = ctx
  self.pages = round.items or {}
  self.decisions = 0
  for _, p in ipairs(self.pages) do if is_decision(p) then self.decisions = self.decisions + 1 end end
  self.i, self.seen = 0, 0
  self.solved = {}      -- pages whose decision is made
  self.wrongs, self.attempts, self.first_right = 0, 0, 0
  self.phase, self.t = "wait", 0
  return self
end

function E:start() self:show(1) end

local function right_index(page)
  for k, c in ipairs(page.choices) do
    if (type(c) == "table" and c.id or c) == page.answer then return k end
  end
end

-- Where the picture, the caption and the cards of this page go.
local function layout(page, decision)
  local cap_h = 0
  if has(page.fa) then
    cap_h = text.fa_height(page.fa, 30) + 22
  elseif page.text and page.text ~= "" then
    local f = text.font("bold", 24)
    local _, lines = f:getWrap(page.text, 580)
    cap_h = #lines * f:getHeight() + 14
  end
  -- A page without a picture is a reading page: the text has the screen,
  -- for children who can already read. It is still spoken and lit.
  if not page.img and cap_h > 0 then
    local room = BOTTOM - TOP - 40 - (decision and CARD_H + 8 or 0)
    local l = { reader = true, pw = 0, ph = 0, px = 0, cap_h = math.max(cap_h + 16, math.min(room, 120)) }
    l.cap_y = TOP + math.max(0, math.floor((room - l.cap_h) / 2))
    l.py = l.cap_y
    l.cards_y = l.cap_y + l.cap_h + 8
    return l
  end
  local free = BOTTOM - TOP - (cap_h > 0 and cap_h + 8 or 0) - (decision and CARD_H + 8 or 0)
  local ph = math.min(300, free)
  local pw = ph * 4 / 3
  local l = { pw = pw, ph = ph, px = (ui.W - pw) / 2, cap_h = cap_h }
  local used = ph + (cap_h > 0 and cap_h + 8 or 0) + (decision and CARD_H + 8 or 0)
  l.py = TOP + math.floor((BOTTOM - TOP - used) / 2)
  l.cap_y = l.py + ph + 8
  l.cards_y = l.cap_y + (cap_h > 0 and cap_h + 8 or 0)
  return l
end

function E:show(i)
  local page = self.pages[i]
  if not page then
    audio.stop()
    self.finished = true
    return
  end
  self.i, self.page = i, page
  self.seen = math.max(self.seen, i)
  self.decision = is_decision(page)
  -- The sheets list the right choice first more often than not: mix the cards,
  -- once per page, so that the place of a card says nothing.
  if self.decision and not page.mixed then
    Quiz.shuffle(page.choices)
    page.mixed = true
  end
  self.asking = self.decision and not self.solved[i]
  self.lay = layout(page, self.decision)
  self.dim, self.tried = {}, false
  self.right = self.decision and right_index(page) or nil
  self.sel = self.solved[i] and self.right or 1
  self.phase, self.t = "page", 0
  self.ctx.say(page.audio)
end

function E:again(slow)
  if not self.page or self.phase == "right" then return end
  if self.phase == "oops" then self.phase = "page" end
  self.t = 0
  self.ctx.say(self.page.audio, { slow = slow })
end

function E:help() self:again(true) end

local function step(self, d)
  local n = #self.page.choices
  local k = self.sel
  for _ = 1, n do
    k = k + d
    if k < 1 or k > n then return end
    if not self.dim[k] then
      self.sel = k
      sfx.play("move")
      return
    end
  end
end

function E:choose()
  local k = self.sel
  if self.dim[k] then return end
  self.attempts = self.attempts + 1
  -- a page whose answer is not among its choices must not trap the child
  if k == self.right or not self.right then
    if not self.tried then self.first_right = self.first_right + 1 end
    self.solved[self.i] = true
    self.right = k
    self.phase, self.t = "right", 0
    audio.stop()
    sfx.play("right")
    self.ctx.next_player()
  else
    self.tried = true
    self.wrongs = self.wrongs + 1
    self.dim[k] = true
    self.phase, self.t, self.oops = "oops", 0, k
    sfx.play("wrong")
    self.ctx.say(self.page.wrong_audio, { after = 0.3 })
  end
end

-- Back to the question after a wrong choice.
function E:ask_again()
  self.phase, self.t = "page", 0
  for k = 1, #self.page.choices do
    if not self.dim[k] then self.sel = k break end
  end
  self.ctx.say(self.page.audio)
end

function E:input(b)
  if not self.page then return end
  if self.phase == "oops" then
    if b == "a" and self.t > 0.3 then self:ask_again() end
  elseif self.phase ~= "page" then
    return
  elseif self.asking then
    if b == "left" then step(self, -1)
    elseif b == "right" then step(self, 1)
    elseif b == "a" then self:choose() end
  elseif b == "a" then
    if audio.busy() then
      audio.stop()
      self.t = 1 -- the page is ready at once
    elseif self.t > 0.2 then
      sfx.play("flip")
      self:show(self.i + 1)
    end
  elseif b == "left" and self.i > 1 then
    sfx.play("flip")
    self:show(self.i - 1)
  end
end

function E:update(dt)
  self.t = self.t + dt
  if self.phase == "right" and self.t > 0.9 then
    self:show(self.i + 1)
  elseif self.phase == "oops" and not audio.busy() and self.t > 1.5 then
    self:ask_again()
  end
end

function E:draw()
  local page, l = self.page, self.lay
  if not page then return end
  local t = self.t
  local speaking = audio.busy()
  local oops = self.phase == "oops"

  -- the picture; after a wrong choice, what that choice leads to
  local pic = page.img
  if oops and page.wrong_img then pic = page.wrong_img end
  if l.reader and oops and pic then
    -- a wrong choice on a reading page: show where it leads, over the text
    ui.card(170, TOP + 8, 300, 225, { fill = ui.c.shade, border = ui.c.bad, radius = 10 })
    ui.thing(pic, self.ctx.root, 172, TOP + 10, 296, 221)
  elseif not l.reader then
    ui.card(l.px, l.py, l.pw, l.ph, { fill = ui.c.shade, border = oops and ui.c.bad or ui.c.ink, radius = 10 })
    if pic then
      ui.thing(pic, self.ctx.root, l.px + 2, l.py + 2, l.pw - 4, l.ph - 4)
    else
      ui.speaker(l.px + l.pw / 2 - 6, l.py + l.ph / 2, math.min(96, l.ph * 0.6), speaking and t or nil, ui.c.ink)
    end
  end
  local side = l.reader and 40 or l.px / 2
  if side >= 40 and not l.reader then
    ui.speaker(side - 4, l.py + 36, 48, speaking and t or nil, speaking and ui.c.ink or ui.c.line)
  end

  -- the caption, lit while it is spoken
  if l.cap_h > 0 and not (l.reader and oops and pic) then
    local lit = speaking and not oops
    ui.card(16, l.cap_y, 608, l.cap_h, { fill = lit and ui.mix(ui.c.paper, ui.c.gold, 0.35) or ui.c.paper,
      border = lit and ui.c.gold or ui.c.line, radius = 10 })
    ui.set(ui.c.ink)
    if l.reader then
      if has(page.fa) then
        text.fa(page.fa, 30, l.cap_y + 12, 580, 30, text.locale == "en" and "left" or "right", true)
      else
        text.print(page.text, 30, l.cap_y + 12, 580, "left", 24, true)
      end
    elseif has(page.fa) then
      text.fa(page.fa, 30, l.cap_y + 6, 580, 30, "center", true)
    else
      text.print(page.text, 30, l.cap_y + 5, 580, "center", 24, true)
    end
  end

  if self.decision then
    local n = #page.choices
    local gap = 12
    local w = math.min(170, (608 - (n - 1) * gap) / n)
    local x0 = (ui.W - (n * w + (n - 1) * gap)) / 2
    for k, c in ipairs(page.choices) do
      local x, y, h = x0 + (k - 1) * (w + gap), l.cards_y, CARD_H
      local opts, alpha = {}, 1
      if (self.phase == "right" or not self.asking) and k == self.right then
        opts.fill, opts.border, opts.width = ui.mix(ui.c.paper, ui.c.good, 0.35), ui.c.good, 6
        if self.phase == "right" then
          local grow = math.sin(math.min(1, t * 3) * math.pi) * 6
          x, y, w, h = x - grow, y - grow, w + grow * 2, h + grow * 2
        end
      elseif self.dim[k] then
        opts.dim, alpha = true, 0.35
        if oops and k == self.oops and t < 0.4 then x = x + math.sin(t * 50) * 6 end
      elseif self.asking and self.phase == "page" and k == self.sel then
        opts.selected = true
      end
      ui.card(x, y, w, h, opts)
      ui.thing(c, self.ctx.root, x + 6, y + 6, w - 12, h - 12, { alpha = alpha })
      if opts.dim then
        ui.set(ui.c.bg, 0.6)
        g.rectangle("fill", x + 6, y + 6, w - 12, h - 12, 8, 8)
      end
      w = math.min(170, (608 - (n - 1) * gap) / n)
    end
  end

  -- which buttons do something now
  local by = l.reader and 456 or math.min(l.py + l.ph - 20, 440)
  if not self.asking and self.phase == "page" then
    local ready = not speaking and t > 0.2
    local r = ready and 17 + math.sin(t * 5) * 3 or 13
    if side >= 40 then
      ui.badge("a", ui.W - side, by, r)
      if ready then ui.arrow("right", ui.W - side, by - 34, 9, ui.c.ink) end
      if self.i > 1 then ui.arrow("left", side, by, 11, ui.c.soft) end
    else
      ui.badge("a", 608, by, r)
    end
  elseif oops and t > 0.3 and side >= 40 then
    ui.badge("a", ui.W - side, by, 13)
  end
end

function E:stars()
  if self.wrongs == 0 then return 3 end
  if self.wrongs <= math.ceil(self.decisions / 2) then return 2 end
  return 1
end

function E:counts() return self.attempts, self.first_right end

function E:progress()
  return self.finished and #self.pages or self.seen, #self.pages
end

return E
