-- Getting more lessons on a phone: the packs of the catalogue that are not on
-- this phone yet, for one place. A fetches the chosen pack, shows how far it
-- is, checks it and installs it like a pack from the card. B stops and goes
-- back. Nothing is sent but the request for the file.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local packs = require("core.packs")
local fetch = require("core.fetch")
local g = love.graphics

local Download = {}
Download.__index = Download

-- opts.subject: the place; opts.level: put that level first
function Download.new(opts)
  local self = setmetatable({ t = 0, sel = 1, subject = opts.subject, level = opts.level, state = "list" }, Download)
  self:fill()
  return self
end

function Download:fill()
  local rank = { learner = 1, teacher = 2, guide = 3 }
  self.list = fetch.missing(function(e) return e.subject == self.subject end)
  table.sort(self.list, function(a, b)
    local la, lb = a.level or 0, b.level or 0
    local fa, fb = la == self.level and 0 or 1, lb == self.level and 0 or 1
    if fa ~= fb then return fa < fb end
    if la ~= lb then return la < lb end
    local ra, rb = (rank[a.kind] or 9) + (a.optional and 0.5 or 0), (rank[b.kind] or 9) + (b.optional and 0.5 or 0)
    if ra ~= rb then return ra < rb end
    return a.pack < b.pack
  end)
  self.sel = math.max(1, math.min(self.sel, #self.list))
end

function Download:enter()
  audio.say(packs.string(#self.list > 0 and "get_intro" or "get_none").audio)
end

function Download:leave()
  fetch.stop()
  audio.stop()
end

function Download:update(dt)
  self.t = self.t + dt
  if self.state == "fetch" then
    local result = fetch.update()
    if result == "done" then
      self.state, self.t = "install", 0
    elseif result == "failed" then
      self.state, self.t = "failed", 0
      sfx.play("wrong")
      audio.say(packs.string("get_failed").audio)
    end
  elseif self.state == "install" and self.t > 0.1 then
    -- the same road as a pack from the card: checked file by file, then copied
    local done = packs.install_updates()
    packs.load()
    self.state, self.t = (done or 0) > 0 and "ready" or "failed", 0
    sfx.play(self.state == "ready" and "done" or "wrong")
    audio.say(packs.string(self.state == "ready" and "get_ready" or "get_failed").audio)
    self:fill()
  end
end

function Download:input(b)
  if self.state == "fetch" then
    if b == "b" then fetch.stop() end
    return
  elseif self.state == "install" then
    return
  elseif self.state == "ready" or self.state == "failed" then
    if b == "a" or b == "b" then
      self.state = "list"
      if #self.list == 0 then app.pop() end
    end
    return
  end
  if b == "b" then app.pop()
  elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
  elseif b == "down" and self.sel < #self.list then self.sel = self.sel + 1 sfx.play("move")
  elseif b == "a" and self.list[self.sel] then
    if fetch.start(self.list[self.sel]) then
      self.state, self.t = "fetch", 0
      self.entry = self.list[self.sel]
      sfx.play("right")
      audio.say(packs.string("get_wait").audio)
    end
  end
end

local KIND = { learner = "get_kind_learner", teacher = "get_kind_teacher", guide = "get_kind_guide" }

local function row(e, y, selected)
  ui.card(14, y, 612, 60, { selected = selected, fill = selected and ui.c.shade or ui.c.paper })
  ui.set(ui.c[e.subject or "en"] or ui.c.teacher)
  g.rectangle("fill", 22, y + 8, 44, 44, 8, 8)
  ui.set(ui.c.white)
  text.centered("bold", tostring(e.level or ""), 22, y + 8, 44, 44, 26)
  ui.set(ui.c.soft)
  local kind = packs.string(KIND[e.kind] or "get_kind_learner")
  if text.locale == "en" then text.print(kind.en or "", 80, y + 4, 300, "left", 14, true)
  elseif kind.fa and kind.fa[1] then text.fa(kind.fa, 300, y - 2, 240, 18, "right") end
  ui.set(ui.c.ink)
  if text.locale == "en" or not (e.title_fa and e.title_fa[1]) then
    text.print(e.title_en or e.pack, 80, y + 24, 440, "left", 20, true)
  else
    text.fa(e.title_fa, 80, y + 18, 440, 24, "right", true)
  end
  ui.set(ui.c.soft)
  text.print(string.format("%d MB", math.max(1, math.floor(e.size / 1e6 + 0.5))), 536, y + 22, 80, "right", 18, true)
end

function Download:draw()
  local color = ui.c[self.subject] or ui.c.teacher
  ui.background(ui.mix(ui.c.bg, color, 0.12))
  local s = packs.string("get_title")
  ui.header(color, s.en, s.fa)
  if self.state ~= "list" then
    local e = self.entry or {}
    row(e, 70, false)
    if self.state == "fetch" or self.state == "install" then
      local p = self.state == "install" and 1 or fetch.progress()
      ui.set(ui.c.line)
      g.rectangle("fill", 60, 220, 520, 26, 13, 13)
      ui.set(ui.c.gold)
      g.rectangle("fill", 60, 220, math.max(26, 520 * p), 26, 13, 13)
      ui.guide(320, 330, 1.6, "idle", self.t)
      if self.state == "fetch" then ui.badge("b", 60, 430, 16) end
    else
      local good = self.state == "ready"
      ui.guide(320, 280, 2, good and "happy" or "idle", self.t)
      ui.set(good and ui.c.good or ui.c.bad)
      g.setLineWidth(10)
      if good then g.line(280, 400, 308, 428, 364, 368) else g.line(290, 370, 350, 430) g.line(350, 370, 290, 430) end
      g.setLineWidth(1)
      ui.badge("a", 560, 430, 16)
    end
    return
  end
  if #self.list == 0 then
    ui.guide(320, 240, 2, "happy", self.t)
    return
  end
  local first = math.max(1, math.min(self.sel - 2, #self.list - 5))
  for i = first, math.min(#self.list, first + 5) do
    row(self.list[i], 50 + (i - first) * 65, i == self.sel)
  end
  ui.badge("a", 600, 462, 13)
  ui.badge("b", 40, 462, 13)
end

return Download
