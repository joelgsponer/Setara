-- One place of the valley: pick a level, pick a game. Every level is open.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local g = love.graphics

local Place = {}
Place.__index = Place

local MAX_LEVEL = { en = 6, fa = 6, math = 6, garden = 4 }
local COLS = 4

function Place.new(subject)
  local self = setmetatable({ subject = subject, t = 0, row = 1, col = 1, scroll = 0, chip = 1 }, Place)
  self.levels = packs.levels(subject)
  self.level = store.progress.level[subject]
  if not packs.subjects[subject][self.level or -1] then self.level = self.levels[1] end
  self:load()
  return self
end

function Place:load()
  self.pack = packs.subjects[self.subject][self.level]
  self.games = {}
  for _, game in ipairs(self.pack.all_games or self.pack.games or {}) do
    if #(game.rounds or {}) > 0 then self.games[#self.games + 1] = game end
  end
  self.col = math.min(self.col, math.max(1, #self.games))
  ui.clear_images()
end

function Place:enter()
  audio.say(packs.string("place_" .. self.subject).audio)
end

function Place:resume()
  -- the placement game may have picked a level
  local want = store.progress.level[self.subject]
  if want and want ~= self.level and packs.subjects[self.subject][want] then
    self.level = want
    self:load()
  end
end

-- The top row: one chip per level, then "find my level", then one or two players.
function Place:chips()
  local chips = {}
  for l = 1, MAX_LEVEL[self.subject] or 6 do
    chips[#chips + 1] = { kind = "level", level = l, on = packs.subjects[self.subject][l] ~= nil }
  end
  chips[#chips + 1] = { kind = "find", on = true }
  chips[#chips + 1] = { kind = "pair", on = true }
  return chips
end

function Place:selected_game()
  if self.row < 1 then return nil end
  return self.games[(self.row - 1) * COLS + self.col]
end

function Place:speak()
  local game = self:selected_game()
  if game then
    audio.say(packs.clips(game.pack or self.pack, game.title_audio))
  elseif self.row == 0 then
    local chip = self:chips()[self.chip] or {}
    if chip.kind == "level" then audio.say(packs.string("level_" .. chip.level).audio)
    elseif chip.kind == "find" then audio.say(packs.string("find_level").audio)
    else audio.say(packs.string(app.pair and "two_players" or "one_player").audio) end
  end
end

local function next_round(game)
  for _, id in ipairs(game.rounds) do
    if store.stars(id) < 3 then return id end
  end
  return game.rounds[1]
end

function Place:input(b)
  local rows = math.ceil(#self.games / COLS)
  if b == "b" then
    app.pop()
    return
  elseif b == "start" then
    app.push(require("scenes.pause").new())
    return
  end
  if self.row == 0 then
    local chips = self:chips()
    if b == "left" or b == "right" then
      local step = b == "left" and -1 or 1
      local i = self.chip
      repeat i = i + step until not chips[i] or chips[i].on
      if chips[i] then
        self.chip = i
        if chips[i].kind == "level" then
          self.level = chips[i].level
          store.progress.level[self.subject] = self.level
          self:load()
        end
        sfx.play("move")
        self:speak()
      end
    elseif b == "down" and rows > 0 then
      self.row = 1
      sfx.play("move")
      self:speak()
    elseif b == "a" then
      local chip = chips[self.chip] or {}
      if chip.kind == "find" then
        app.push(require("scenes.placement").new(self.subject))
      elseif chip.kind == "pair" then
        app.pair = not app.pair
        sfx.play("flip")
        self:speak()
      elseif rows > 0 then
        self.row = 1
        self:speak()
      end
    end
    return
  end
  if b == "a" then
    local game = self:selected_game()
    if game then
      store.progress.level[self.subject] = self.level
      app.push(require("scenes.play").new({ pack = game.pack or self.pack, game = game, round_id = next_round(game),
        pair = app.pair }))
    end
    return
  end
  local row, col = self.row, self.col
  if b == "left" then col = col - 1
  elseif b == "right" then col = col + 1
  elseif b == "up" then row = row - 1
  elseif b == "down" then row = row + 1
  else return end
  if row == 0 then
    self.row = 0
    self.chip = 1
    for i, chip in ipairs(self:chips()) do
      if chip.kind == "level" and chip.level == self.level then self.chip = i end
    end
  elseif row >= 1 and row <= rows and col >= 1 and col <= COLS and self.games[(row - 1) * COLS + col] then
    self.row, self.col = row, col
  else
    return
  end
  sfx.play("move")
  self:speak()
end

function Place:update(dt)
  self.t = self.t + dt
end

local function game_stars(game)
  local have = 0
  for _, id in ipairs(game.rounds) do have = have + store.stars(id) end
  return have, #game.rounds * 3
end

function Place:draw()
  local color = ui.c[self.subject]
  ui.background(ui.mix(ui.c.bg, color, 0.12))
  local s = packs.string("place_" .. self.subject)
  ui.header(color, s.en, s.fa)

  -- level chips
  local chips = self:chips()
  local x = 14
  for i, chip in ipairs(chips) do
    local w = chip.kind == "level" and 52 or 64
    if chip.kind == "find" then x = x + 60 end
    local selected = self.row == 0 and self.chip == i
    local current = chip.kind == "level" and chip.level == self.level
    local fill = current and color or ui.c.paper
    ui.card(x, 54, w, 44, { fill = fill, selected = selected, dim = not chip.on, radius = 10 })
    if chip.kind == "level" then
      ui.set(current and ui.c.white or ui.c.ink)
      text.centered("bold", tostring(chip.level), x, 54, w, 44, 30)
    elseif chip.kind == "find" then
      -- a magnifying glass: find my level
      ui.set(ui.c.ink)
      g.setLineWidth(4)
      g.circle("line", x + 28, 73, 10)
      g.line(x + 35, 81, x + 44, 90)
      g.setLineWidth(1)
    else
      -- one or two players
      local n = app.pair and 2 or 1
      for k = 1, n do
        local px = x + w / 2 + (k - (n + 1) / 2) * 22
        ui.set(k == 1 and ui.c.en or ui.c.fa)
        g.circle("fill", px, 68, 8)
        g.rectangle("fill", px - 9, 77, 18, 14, 5, 5)
      end
    end
    x = x + w + 6
  end

  -- game tiles
  -- two rows are visible; the view follows the selection
  local tw, th = 147, 176
  local first = math.max(0, math.min(self.row - 1, math.ceil(#self.games / COLS) - 2))
  if self.row <= 1 then first = 0 end
  for i, game in ipairs(self.games) do
    local row, col = math.floor((i - 1) / COLS), (i - 1) % COLS
    if row >= first and row < first + 2 then
      local tx, ty = 14 + col * (tw + 8), 110 + (row - first) * (th + 8)
      local selected = self.row == row + 1 and self.col == col + 1
      ui.card(tx, ty, tw, th, { selected = selected })
      if game.icon then ui.thing(game.icon, (game.pack or self.pack).root, tx + 26, ty + 8, 95, 92) end
      ui.set(ui.c.ink)
      if game.title_fa and game.title_fa[1] then
        text.centered("fabold", game.title_fa[1], tx + 4, ty + 98, tw - 8, 44, 24)
      end
      local have, max = game_stars(game)
      ui.star(tx + 34, ty + 154, 10, have > 0)
      ui.set(ui.c.ink)
      text.print(have .. " / " .. max, tx + 50, ty + 141, 96, "left", 20, true)
    end
  end
end

return Place
