-- Plays one round: spoken introduction, warm-up five, the game, the stars.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local engines = require("engines")
local Quiz = require("core.quiz")
local g = love.graphics

local Play = {}
Play.__index = Play

local SHARE_AFTER = 600 -- seconds of play before the guide suggests passing the device on

-- opts: pack, game, round_id, pair, review (false to skip the warm-up)
function Play.new(opts)
  local self = setmetatable({}, Play)
  self.pack, self.game, self.round_id, self.pair = opts.pack, opts.game, opts.round_id, opts.pair
  self.want_review = opts.review ~= false
  self.t, self.elapsed = 0, 0
  self.player = 1
  return self
end

local function make_ctx(self, pack)
  local ctx = { root = pack.root, pack = pack, pair = self.pair, top = 40 }
  ctx.say = function(clips, opts) audio.say(packs.clips(pack, clips), opts) end
  ctx.next_player = function()
    if self.pair then self.player = 3 - self.player end
    ctx.player = self.player
  end
  ctx.player = self.player
  return ctx
end

-- Five quick review items from rounds this class has already played, in this
-- level or the level before.
function Play:make_warmup()
  if not self.want_review then return nil end
  local candidates = { self.pack }
  local below = packs.subjects[self.pack.subject] and packs.subjects[self.pack.subject][(self.pack.level or 1) - 1]
  if below then candidates[2] = below end
  for _, pack in ipairs(candidates) do
    local pool = {}
    for _, entry in ipairs(packs.review(pack)) do
      if entry.round ~= self.round_id and store.stars(entry.round) > 0 and #(entry.choices or {}) >= 2 then
        pool[#pool + 1] = entry
      end
    end
    if #pool >= 5 then
      Quiz.shuffle(pool)
      local items, seen = {}, {}
      for _, entry in ipairs(pool) do
        if entry.answer ~= nil and not seen[entry.answer] and #items < 5 then
          seen[entry.answer] = true
          items[#items + 1] = entry
        end
      end
      if #items >= 3 then
        local mod = engines.get("listen_pick")
        return mod.new({ items = items }, make_ctx(self, pack))
      end
    end
  end
  return nil
end

function Play:enter()
  local round, err = packs.round(self.pack, self.round_id)
  -- Two children on one device: picture-picking rounds become a duel.
  local id = round and round.engine
  if self.pair and (id == "listen_pick") then id = "duel" end
  local mod = round and (engines.get(id) or engines.get(round.engine))
  if not round or not mod then
    store.log("round " .. tostring(self.round_id) .. ": " .. tostring(err or "no engine"))
    self.failed = true
    return
  end
  self.round = round
  self.ctx = make_ctx(self, self.pack)
  self.engine = mod.new(round, self.ctx)
  self.warmup = self:make_warmup()
  self.state = "intro"
  audio.say(packs.clips(self.pack, round.intro_audio), { after = 0.3 })
end

function Play:leave()
  audio.stop()
  sfx.stop_loop()
  ui.clear_images()
  if self.elapsed > 5 then
    store.add_minutes(self.pack.subject or "other", self.elapsed)
    self.elapsed = 0
    store.save_stats()
  end
end

function Play:begin()
  if self.state ~= "intro" then return end
  if self.warmup then
    self.state = "warmup"
    self.warmup_waiting = true
    audio.say(packs.string("warmup").audio)
  else
    self.state = "main"
    self.engine:start()
  end
end

function Play:active()
  if self.state == "warmup" then return self.warmup end
  if self.state == "main" then return self.engine end
end

function Play:finish()
  local stars = math.max(1, math.min(3, self.engine:stars() or 1))
  local attempts, correct = 0, 0
  if self.engine.counts then attempts, correct = self.engine:counts() end
  self.stars = stars
  self.state, self.t = "result", 0
  self.shown = 0
  store.set_stars(self.round_id, stars)
  store.count_round(self.round_id, attempts or 0, correct or 0, self.elapsed, stars)
  store.add_minutes(self.pack.subject or "other", self.elapsed)
  self.elapsed = 0
  store.progress.last = { subject = self.pack.subject, level = self.pack.level }
  store.save()
  self.share = app.play_seconds > SHARE_AFTER
  if self.share then app.play_seconds = 0 end
  local praise = packs.string("praise_" .. stars)
  local clips = {}
  for _, c in ipairs(praise.audio or {}) do clips[#clips + 1] = c end
  if self.share then
    for _, c in ipairs(packs.string("pass_on").audio or {}) do clips[#clips + 1] = c end
  end
  audio.say(clips)
end

function Play:update(dt)
  self.t = self.t + dt
  if self.failed then
    app.pop()
    return
  end
  if self.state ~= "result" then
    self.elapsed = self.elapsed + dt
    app.play_seconds = app.play_seconds + dt
  end
  -- Steps that follow a spoken sentence wait by watching the speech, not by a
  -- callback: speech that is cut off must never leave the round standing.
  if self.state == "intro" and not audio.busy() then
    self:begin()
  elseif self.warmup_waiting and not audio.busy() then
    self.warmup_waiting = false
    self.warmup:start()
  end
  local e = self:active()
  if self.warmup_waiting then e = nil end
  if e then
    e:update(dt)
    if e.finished then
      if self.state == "warmup" then
        self.state = "main"
        self.engine:start()
      else
        self:finish()
      end
    end
  elseif self.state == "result" then
    local want = math.min(self.stars, math.floor(self.t / 0.45))
    if want > self.shown then
      self.shown = want
      sfx.play("star")
    end
  end
end

function Play:next_round()
  local rounds = self.game.rounds
  local at = 1
  for i, id in ipairs(rounds) do if id == self.round_id then at = i end end
  for step = 1, #rounds do
    local id = rounds[(at + step - 1) % #rounds + 1]
    if store.stars(id) < 3 then return id end
  end
  return rounds[at % #rounds + 1]
end

function Play:input(b)
  if self.failed then return end
  if self.state == "result" then
    if self.t < 0.8 then return end
    if b == "a" then
      app.replace(Play.new({ pack = self.pack, game = self.game, round_id = self:next_round(), pair = self.pair }))
    elseif b == "b" then
      app.pop()
    end
    return
  end
  local e = self:active()
  if b == "start" then
    app.push(require("scenes.pause").new())
  elseif e and e.uses and e.uses[b] then
    e:input(b)
  elseif b == "b" then
    app.pop()
  elseif self.state == "intro" then
    if b == "a" then
      audio.stop()
      self:begin()
    end
  elseif e then
    if b == "x" then e:again(true)
    elseif b == "y" then e:help()
    else e:input(b) end
  end
end

local function draw_hud(self, e)
  ui.set(ui.c.paper)
  g.rectangle("fill", 0, 0, ui.W, 36)
  ui.set(ui.c.line)
  g.rectangle("fill", 0, 36, ui.W, 2)
  if e and e.progress then
    local done, total = e:progress()
    ui.progress(done, total, 120, 18, 400)
  end
  if self.state == "warmup" then
    -- a small sun: this is the warm-up, it does not count
    ui.set(ui.c.gold)
    g.circle("fill", 24, 18, 9)
    g.setLineWidth(2)
    for i = 0, 7 do
      local a = i * math.pi / 4 + self.t
      g.line(24 + math.cos(a) * 12, 18 + math.sin(a) * 12, 24 + math.cos(a) * 16, 18 + math.sin(a) * 16)
    end
    g.setLineWidth(1)
  end
  if self.pair and not (e and e.uses) then
    for p = 1, 2 do
      local x = p == 1 and 566 or 606
      local on = self.player == p
      ui.set(on and ui.c[self.pack.subject or "en"] or ui.c.line)
      g.circle("fill", x, 18, on and 13 or 9)
      ui.set(ui.c.white)
      text.centered("bold", tostring(p), x - 12, 6, 24, 24, 20)
    end
  end
end

function Play:draw()
  ui.background()
  if self.failed then return end
  local color = ui.c[self.pack.subject or "en"] or ui.c.en
  if self.state == "intro" then
    ui.background(ui.mix(ui.c.bg, color, 0.15))
    ui.guide(320, 190, 2.4, "talk", self.t)
    if self.game.icon then
      ui.card(40, 300, 110, 110)
      ui.thing(self.game.icon, self.pack.root, 46, 306, 98, 98)
    end
    ui.set(ui.c.ink)
    text.print(self.game.title_en or "", 170, 318, 300, "left", 24, true)
    if self.game.title_fa and self.game.title_fa[1] and text.locale ~= "en" then
      text.fa(self.game.title_fa, 170, 348, 430, 30, "right", true)
    end
    ui.badge("a", 600, 440, 16)
  elseif self.state == "result" then
    ui.background(ui.mix(ui.c.bg, ui.c.gold, 0.18))
    for i = 1, 3 do
      local filled = i <= self.shown
      local pop = 0
      if filled then
        local age = self.t - i * 0.45
        pop = math.max(0, 1 - age * 3) * 14
      end
      ui.star(320 + (i - 2) * 120, 130, 44 + pop, filled)
    end
    ui.guide(320, 290, 2.2, "happy", self.t)
    if self.share then
      -- two children: time to pass the device on
      for i = 0, 1 do
        ui.set(i == 0 and ui.c.en or ui.c.fa)
        g.circle("fill", 500 + i * 46, 280, 16)
        g.rectangle("fill", 484 + i * 46, 298, 32, 36, 8, 8)
      end
      ui.arrow("right", 523, 316, 9, ui.c.ink)
    end
    ui.badge("a", 560, 430, 18)
    ui.arrow("right", 596, 430, 10, ui.c.ink)
    ui.badge("b", 80, 430, 18)
    ui.arrow("left", 44, 430, 10, ui.c.ink)
  else
    local e = self:active()
    if e then e:draw() end
    draw_hud(self, e)
  end
end

return Play
