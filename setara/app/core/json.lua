-- Small JSON reader and writer. Enough for level files, manifests and saves.
local M = {}

local esc = { ['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t' }

local function enc(v, out)
  local t = type(v)
  if t == "nil" then out[#out + 1] = "null"
  elseif t == "boolean" then out[#out + 1] = v and "true" or "false"
  elseif t == "number" then
    if v ~= v or v == math.huge or v == -math.huge then out[#out + 1] = "0"
    elseif v == math.floor(v) then out[#out + 1] = string.format("%d", v)
    else out[#out + 1] = string.format("%.6g", v) end
  elseif t == "string" then
    out[#out + 1] = '"' .. v:gsub('[%c"\\]', function(c)
      return esc[c] or string.format("\\u%04x", c:byte())
    end) .. '"'
  elseif t == "table" then
    if #v > 0 or next(v) == nil and v.__array then
      out[#out + 1] = "["
      for i = 1, #v do
        if i > 1 then out[#out + 1] = "," end
        enc(v[i], out)
      end
      out[#out + 1] = "]"
    else
      local keys = {}
      for k in pairs(v) do if type(k) == "string" then keys[#keys + 1] = k end end
      table.sort(keys)
      out[#out + 1] = "{"
      for i, k in ipairs(keys) do
        if i > 1 then out[#out + 1] = "," end
        enc(k, out)
        out[#out + 1] = ":"
        enc(v[k], out)
      end
      out[#out + 1] = "}"
    end
  else
    error("cannot encode " .. t)
  end
end

function M.encode(v)
  local out = {}
  enc(v, out)
  return table.concat(out)
end

local function utf8char(cp)
  if cp < 0x80 then return string.char(cp)
  elseif cp < 0x800 then return string.char(0xC0 + math.floor(cp / 64), 0x80 + cp % 64)
  elseif cp < 0x10000 then
    return string.char(0xE0 + math.floor(cp / 4096), 0x80 + math.floor(cp / 64) % 64, 0x80 + cp % 64)
  end
  return string.char(0xF0 + math.floor(cp / 262144), 0x80 + math.floor(cp / 4096) % 64,
    0x80 + math.floor(cp / 64) % 64, 0x80 + cp % 64)
end

local unesc = { b = "\b", f = "\f", n = "\n", r = "\r", t = "\t", ['"'] = '"', ["\\"] = "\\", ["/"] = "/" }

-- Returns the value, or nil and an error message. Never throws.
function M.decode(s)
  if type(s) ~= "string" then return nil, "not a string" end
  local pos = 1
  local value

  local function ws()
    pos = s:find("[^ \t\r\n]", pos) or #s + 1
  end

  local function str()
    local out, i = {}, pos + 1
    while true do
      local j = s:find('["\\]', i)
      if not j then error("unterminated string") end
      out[#out + 1] = s:sub(i, j - 1)
      if s:sub(j, j) == '"' then pos = j + 1 return table.concat(out) end
      local c = s:sub(j + 1, j + 1)
      if c == "u" then
        local cp = tonumber(s:sub(j + 2, j + 5), 16) or error("bad \\u escape")
        i = j + 6
        if cp >= 0xD800 and cp < 0xDC00 and s:sub(i, i + 1) == "\\u" then
          local lo = tonumber(s:sub(i + 2, i + 5), 16) or error("bad \\u escape")
          cp = 0x10000 + (cp - 0xD800) * 0x400 + (lo - 0xDC00)
          i = i + 6
        end
        out[#out + 1] = utf8char(cp)
      else
        out[#out + 1] = unesc[c] or error("bad escape")
        i = j + 2
      end
    end
  end

  function value()
    ws()
    local c = s:sub(pos, pos)
    if c == "{" then
      local t = {}
      pos = pos + 1
      ws()
      if s:sub(pos, pos) == "}" then pos = pos + 1 return t end
      while true do
        ws()
        if s:sub(pos, pos) ~= '"' then error("expected key at " .. pos) end
        local k = str()
        ws()
        if s:sub(pos, pos) ~= ":" then error("expected : at " .. pos) end
        pos = pos + 1
        t[k] = value()
        ws()
        local d = s:sub(pos, pos)
        pos = pos + 1
        if d == "}" then return t end
        if d ~= "," then error("expected , or } at " .. pos) end
      end
    elseif c == "[" then
      local t = {}
      pos = pos + 1
      ws()
      if s:sub(pos, pos) == "]" then pos = pos + 1 return t end
      while true do
        t[#t + 1] = value()
        ws()
        local d = s:sub(pos, pos)
        pos = pos + 1
        if d == "]" then return t end
        if d ~= "," then error("expected , or ] at " .. pos) end
      end
    elseif c == '"' then
      return str()
    elseif s:sub(pos, pos + 3) == "true" then pos = pos + 4 return true
    elseif s:sub(pos, pos + 4) == "false" then pos = pos + 5 return false
    elseif s:sub(pos, pos + 3) == "null" then pos = pos + 4 return nil
    else
      local num = s:match("^-?%d+%.?%d*[eE]?[+-]?%d*", pos)
      if not num or num == "" then error("unexpected character at " .. pos) end
      pos = pos + #num
      return tonumber(num) or error("bad number")
    end
  end

  local ok, res = pcall(function()
    local v = value()
    ws()
    if pos <= #s then error("trailing data") end
    return v
  end)
  if ok then return res end
  return nil, tostring(res)
end

return M
