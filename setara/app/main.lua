-- Setara app entry point.
-- Scaffold only: shows the version. The shell (menus, progress, settings,
-- card update) goes in shell/, the game mechanics in engines/.
local VERSION = require("version")
local engines = require("engines")

function love.draw()
  love.graphics.printf("Setara " .. VERSION, 0, 200, 640, "center")
  love.graphics.printf(#engines.ids .. " engines registered, none implemented",
    0, 230, 640, "center")
end

function love.keypressed(key)
  if key == "escape" then love.event.quit() end
end
