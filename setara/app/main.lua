-- Setara app entry point: window, scene stack, input, and the test driver.
local input = require("core.input")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local ui = require("core.ui")

app = { stack = {}, time = 0, play_seconds = 0, version = require("version") }

local canvas
local speed = tonumber(os.getenv("SETARA_SPEED")) or 1
local script, script_wait, shot_name
-- Recording a film of the app (tools/film/make.py): SETARA_RECORD names a folder
-- in the save directory. Time then advances exactly 1/30 s per frame, every
-- frame is saved, and every sound is noted with its frame number.
local record = os.getenv("SETARA_RECORD")
local frame = 0

-- Scene stack ------------------------------------------------------------------

function app.top() return app.stack[#app.stack] end

function app.push(scene)
  app.stack[#app.stack + 1] = scene
  if scene.enter then scene:enter() end
end

function app.pop(result)
  if #app.stack <= 1 then return end -- the first scene is never removed
  local old = table.remove(app.stack)
  if old and old.leave then old:leave() end
  local top = app.top()
  if top and top.resume then top:resume(result) end
end

function app.replace(scene)
  local old = table.remove(app.stack)
  if old and old.leave then old:leave() end
  app.push(scene)
end

-- Drop everything above the first scene (home).
function app.home()
  while #app.stack > 1 do
    local old = table.remove(app.stack)
    if old.leave then old:leave() end
  end
  local top = app.top()
  if top and top.resume then top:resume() end
end

-- LÖVE callbacks ----------------------------------------------------------------

function love.load()
  love.graphics.setDefaultFilter("linear", "linear")
  love.mouse.setVisible(false)
  canvas = love.graphics.newCanvas(ui.W, ui.H)
  sfx.load()
  store.load()
  -- Handhelds without a clock battery start at the same "time" every day, so
  -- the seed also takes a start counter kept on the card.
  store.progress.starts = (tonumber(store.progress.starts) or 0) + 1
  love.math.setRandomSeed(tonumber(os.getenv("SETARA_SEED"))
    or (os.time() % 2147483647 + store.progress.starts * 7919 + math.floor(os.clock() * 1e6) % 100000))
  store.ensure_device()
  audio.set_volume(store.progress.settings.volume)
  local learned = love.filesystem.getInfo("data/buttons.json") and
    require("core.json").decode(love.filesystem.read("data/buttons.json") or "")
  if input.complete(learned) then input.custom = learned end
  -- English mode: chosen in the pause menu, or forced by a file named
  -- "english" on the card or by SETARA_LOCALE=en.
  local text = require("core.text")
  if os.getenv("SETARA_LOCALE") == "en" or love.filesystem.getInfo("english") or love.filesystem.getInfo("english.txt") then
    store.progress.settings.locale = "en"
  end
  text.locale = store.progress.settings.locale
  input.listener = function(button)
    local top = app.top()
    if top and top.input then top:input(button) end
  end
  app.push(require("scenes.boot").new())
  if record then
    love.filesystem.createDirectory(record)
    local log = {}
    app.sound_log = function(kind, name)
      if app.recording then
        log[#log + 1] = string.format("%d\t%s\t%s", frame, kind, name)
        love.filesystem.write(record .. "/sounds.tsv", table.concat(log, "\n") .. "\n")
      end
    end
  end

  local path = os.getenv("SETARA_SCRIPT")
  if path then
    local chunk = assert(loadfile(path))
    script = coroutine.create(chunk)
    script_wait = 0
  end
end

local function run_script(dt)
  if not script then return end
  script_wait = script_wait - dt
  if script_wait > 0 or shot_name then return end
  local api = {
    press = function(b) input.fake(b) coroutine.yield(0.05) end,
    hold = function(b) input.fake(b, true) end,
    release = function(b) input.fake_release(b) end,
    wait = function(t) coroutine.yield(t) end,
    shot = function(name) shot_name = name coroutine.yield(0) end,
    top = app.top,
    app = app,
  }
  -- film scripts: record(true) starts saving frames, mark("name") notes a cut point
  api.record = function(on) app.recording = on end
  api.mark = function(name) if app.sound_log then app.sound_log("mark", name) end end
  -- Leave the first-run tutorial if it is showing.
  api.skip_tutorial = function()
    local top = app.top()
    if top and top.step and top.happy then input.fake("start") coroutine.yield(0.5) end
  end
  -- Jump straight into a round: start_round("en-1", "word_stall", 1, { pair = true })
  api.start_round = function(pack_id, game_id, index, opts)
    local packs = require("core.packs")
    local pack = assert(packs.list[pack_id], "no pack " .. tostring(pack_id))
    local game
    for _, gm in ipairs(pack.games) do if gm.id == game_id then game = gm end end
    assert(game, "no game " .. tostring(game_id))
    opts = opts or {}
    app.push(require("scenes.play").new({ pack = pack, game = game, round_id = game.rounds[index or 1],
      pair = opts.pair, review = opts.review or false }))
    coroutine.yield(0.2)
    return app.top()
  end
  local ok, res = coroutine.resume(script, api)
  if not ok then
    print("SCRIPT ERROR: " .. tostring(res))
    love.event.quit(1)
  elseif coroutine.status(script) == "dead" then
    love.event.quit(0)
  else
    script_wait = tonumber(res) or 0
  end
end

function love.update(dt)
  dt = math.min(dt, 0.1) * speed
  if record then
    dt = 1 / 30
    frame = frame + 1
  end
  app.time = app.time + dt
  input.update(dt)
  audio.update(dt)
  local top = app.top()
  if top and top.update then top:update(dt) end
  run_script(dt)
end

function love.draw()
  love.graphics.setCanvas(canvas)
  love.graphics.clear(ui.c.bg[1], ui.c.bg[2], ui.c.bg[3])
  -- A scene with `overlay` draws on top of the one below it (pause menu).
  local first = #app.stack
  while first > 1 and app.stack[first].overlay do first = first - 1 end
  first = math.max(1, first)
  -- English mode draws the screen a little smaller and keeps a band under it
  -- for the captions, so that a caption never covers what is being shown.
  local english = require("core.text").locale == "en"
  if english then
    love.graphics.clear(ui.c.ink[1], ui.c.ink[2], ui.c.ink[3])
    love.graphics.push()
    love.graphics.translate(ui.W * 0.0625, 0)
    love.graphics.scale(0.875, 0.875)
    ui.background()
  end
  for i = first, #app.stack do
    local scene = app.stack[i]
    if scene.draw then scene:draw() end
  end
  if english then love.graphics.pop() end
  -- English mode: a caption for whatever is being spoken, in the band below.
  if english then
    local clip = audio.playing()
    local captions = require("core.packs").captions
    local caption = clip and captions and captions[clip]
    if caption then
      local text = require("core.text")
      local f = text.font("latin", 16)
      local _, lines = f:getWrap(caption, ui.W - 24)
      local n = math.min(3, #lines)
      local lh = math.min(f:getHeight() - 4, 19)   -- three lines must fit the band
      ui.set(ui.c.white)
      love.graphics.setFont(f)
      for i = 1, n do
        love.graphics.printf(lines[i], 12, 420 + (60 - n * lh) / 2 + (i - 1) * lh - 2, ui.W - 24, "center")
      end
    end
  end
  love.graphics.setCanvas()
  if record and app.recording then
    canvas:newImageData():encode("png", string.format("%s/f%06d.png", record, frame))
  end
  if shot_name then
    love.filesystem.createDirectory("shots")
    canvas:newImageData():encode("png", "shots/" .. shot_name .. ".png")
    shot_name = nil
  end
  local w, h = love.graphics.getDimensions()
  local s = math.min(w / ui.W, h / ui.H)
  love.graphics.clear(0, 0, 0)
  -- "Brightness" dims the picture; the backlight itself belongs to the firmware.
  local b = math.max(0.3, math.min(1, tonumber(store.progress and store.progress.settings.brightness) or 1))
  love.graphics.setColor(b, b, b)
  love.graphics.draw(canvas, (w - ui.W * s) / 2, (h - ui.H * s) / 2, 0, s, s)
end

function love.keypressed(key)
  if key == "escape" then love.event.quit() end
  if key == "f11" then love.window.setFullscreen(not love.window.getFullscreen()) end
  input.keypressed(key)
end

function love.keyreleased(key) input.keyreleased(key) end
function love.gamepadpressed(j, b) input.gamepadpressed(j, b) end
function love.gamepadreleased(j, b) input.gamepadreleased(j, b) end
function love.joystickpressed(j, b) input.joystickpressed(j, b) end
function love.joystickreleased(j, b) input.joystickreleased(j, b) end
function love.joystickhat(j, h, d) input.joystickhat(j, h, d) end

function love.quit()
  pcall(store.save)
end

-- A crash must not leave a child with an error screen: note it in the log
-- and start again. A crash right after starting falls through to LÖVE's own
-- handler, so the app cannot loop for ever.
local default_handler = love.errorhandler
function love.errorhandler(msg)
  print("ERROR: " .. tostring(msg))
  print(debug.traceback())
  if os.getenv("SETARA_SCRIPT") then os.exit(1) end
  pcall(function()
    store.log(tostring(msg))
    store.save_stats()
  end)
  if app.time > 10 then
    return function() return "restart" end
  end
  return default_handler(msg)
end
