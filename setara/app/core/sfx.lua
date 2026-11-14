-- Sound effects and tunes, synthesised at start. No audio assets to licence.
local M = {}
local RATE = 22050
local sounds = {}
local looping

local function note(freq, dur, vol)
  return { f = freq, d = dur, v = vol or 0.5 }
end

-- A soft bell: sine plus a quiet octave, with a quick attack and a decay.
local function render(notes, decay)
  local total = 0
  for _, n in ipairs(notes) do total = total + n.d end
  local data = love.sound.newSoundData(math.floor(total * RATE) + 1, RATE, 16, 1)
  local i = 0
  for _, n in ipairs(notes) do
    local count = math.floor(n.d * RATE)
    for k = 0, count - 1 do
      local t = k / RATE
      local env = math.min(1, t * 200) * math.exp(-t * (decay or 6))
      local tail = math.min(1, (count - k) / (0.01 * RATE))
      local s = 0
      if n.f > 0 then
        s = (math.sin(2 * math.pi * n.f * t) + 0.3 * math.sin(4 * math.pi * n.f * t)) * n.v * env * tail
      end
      data:setSample(i, math.max(-1, math.min(1, s)))
      i = i + 1
    end
  end
  return data
end

local C4, D4, E4, F4, G4, A4, B4 = 261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9
local C5, D5, E5, G5, A5, C6 = 523.3, 587.3, 659.3, 784.0, 880.0, 1046.5

function M.load()
  local defs = {
    move = { { note(E5, 0.04, 0.25) }, 30 },
    right = { { note(G5, 0.09), note(C6, 0.22) }, 8 },
    wrong = { { note(E4, 0.12, 0.4), note(C4, 0.2, 0.4) }, 7 },
    star = { { note(C5, 0.08), note(E5, 0.08), note(G5, 0.08), note(C6, 0.3) }, 6 },
    flip = { { note(A4, 0.05, 0.3) }, 25 },
    hop = { { note(D5, 0.06, 0.4), note(A5, 0.08, 0.4) }, 14 },
    buzz = { { note(A5, 0.07, 0.5), note(A5, 0.07, 0.5) }, 12 },
    chime = { { note(E5, 0.3), note(C5, 0.3), note(G5, 0.6) }, 3 },
    done = { { note(C5, 0.12), note(E5, 0.12), note(G5, 0.12), note(E5, 0.12), note(C6, 0.4) }, 4 },
    tick = { { note(C6, 0.02, 0.2) }, 60 },
  }
  for name, def in pairs(defs) do
    sounds[name] = love.audio.newSource(render(def[1], def[2]), "static")
  end
  -- A calm looping tune for passing games in class ("pass the ball").
  local q = 0.28
  local line = { C5, E5, G5, E5, D5, F4 * 2, A5, F4 * 2, E5, G5, C6, G5, D5, G4 * 2, B4, D5 }
  local tune = {}
  for _, f in ipairs(line) do tune[#tune + 1] = note(f, q, 0.4) end
  sounds.tune = love.audio.newSource(render(tune, 4), "static")
  sounds.tune:setLooping(true)
end

function M.play(name)
  local s = sounds[name]
  if not s then return end
  s:stop()
  s:play()
end

function M.loop(name)
  M.stop_loop()
  looping = sounds[name]
  if looping then looping:play() end
end

function M.stop_loop()
  if looping then looping:stop() end
  looping = nil
end

return M
