-- Start-up: install packs waiting on the card, load everything, go home.
local ui = require("core.ui")
local text = require("core.text")
local packs = require("core.packs")
local store = require("core.store")

local Boot = {}
Boot.__index = Boot

function Boot.new()
  return setmetatable({ t = 0, spin = 0 }, Boot)
end

function Boot:enter()
  self.co = coroutine.create(function()
    coroutine.yield()
    local ok, err = pcall(packs.install_updates, coroutine.yield)
    if not ok then store.log("install: " .. tostring(err):sub(1, 60)) end
    coroutine.yield()
    packs.load()
  end)
end

function Boot:update(dt)
  self.t = self.t + dt
  if self.co then
    local ok, err = coroutine.resume(self.co)
    if not ok then
      store.log("boot: " .. tostring(err))
      self.co = nil
      self.error = true
    elseif coroutine.status(self.co) == "dead" then
      self.co = nil
      store.save_stats()
      if packs.count() == 0 or not packs.core then
        self.empty = true
      else
        local home = require("scenes.home").new()
        app.replace(home)
        if not store.progress.tutorial_done then
          app.push(require("scenes.tutorial").new())
        end
        -- An unknown pad, or a file named "calibrate" on the card: learn the buttons first.
        local input = require("core.input")
        local asked = love.filesystem.getInfo("calibrate") or love.filesystem.getInfo("calibrate.txt")
        if asked or (input.unknown_pad() and not input.custom and not store.progress.calibration_seen) then
          app.push(require("scenes.calibrate").new())
        end
      end
    end
  end
end

function Boot:draw()
  ui.background(ui.c.sky)
  -- A deployment can put its own neutral start picture on the card.
  if self.start == nil then self.start = love.filesystem.getInfo("start.png") and ui.image("start.png") or false end
  if self.start then
    love.graphics.setColor(1, 1, 1)
    ui.draw_image(self.start, 0, 0, ui.W, ui.H)
  else
    ui.guide(320, 200, 2, self.empty and "think" or "idle", self.t)
  end
  ui.set(ui.c.ink)
  text.print("Setara " .. app.version, 0, 440, 630, "right", 16)
  if self.empty or self.error then
    -- No content on the card: say so in both languages, with the fix.
    ui.card(60, 290, 520, 120)
    ui.set(ui.c.ink)
    text.print("No content packs found.\nCopy the packs into the update folder on the card and start again.",
      76, 300, 488, "center", 20)
  else
    for i = 0, 2 do
      local on = math.floor(self.t * 4) % 3 == i
      ui.set(on and ui.c.gold or ui.c.white)
      love.graphics.circle("fill", 296 + i * 24, 300, 8)
    end
  end
end

return Boot
