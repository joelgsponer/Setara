-- LÖVE configuration. The handheld screen is 640x480; the PC window matches it.
function love.conf(t)
  t.identity = "setara"
  t.version = "11.4"
  t.window.title = "Setara"
  t.window.width = 640
  t.window.height = 480
  t.window.resizable = false
  -- Phones and tablets: the whole screen, lying or standing; buttons on the glass.
  t.window.usedpiscale = false
  local try = os.getenv("SETARA_TOUCH")   -- "800x360" on a PC shows what a phone shows
  local tw, th = (try or ""):match("^(%d+)x(%d+)$")
  if tw then t.window.width, t.window.height = tonumber(tw), tonumber(th) end
  t.modules.physics = false
  t.modules.video = false   -- spec: no video
end
