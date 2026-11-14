-- LÖVE configuration. The handheld screen is 640x480; the PC window matches it.
function love.conf(t)
  t.identity = "setara"
  t.version = "11.4"
  t.window.title = "Setara"
  t.window.width = 640
  t.window.height = 480
  t.window.resizable = false
  t.modules.physics = false
  t.modules.video = false   -- spec: no video
  t.modules.touch = false
end
