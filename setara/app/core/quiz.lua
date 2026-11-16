-- The item loop shared by most engines, with the spec's shared rules:
--   * a wrong answer is never punished, the item comes back later in the round
--   * three right in a row makes it a little harder, two wrong a little easier
--   * stars come from first-try answers
local Q = {}
Q.__index = Q

-- opts.ordered keeps the sheet's order (dialogues); otherwise the questions
-- come in a new order every time. opts.draw: the round is a pool, and each
-- play asks only that many of it, so that a round is not the same twice.
function Q.new(items, opts)
  local self = setmetatable({}, Q)
  opts = opts or {}
  self.queue = {}
  for i, it in ipairs(items) do self.queue[i] = it end
  if not opts.ordered then Q.shuffle(self.queue) end
  local draw = tonumber(opts.draw)
  if draw and draw >= 1 then
    for i = #self.queue, math.floor(draw) + 1, -1 do self.queue[i] = nil end
  end
  self.total = #self.queue
  self.done = 0          -- items finished at least once
  self.first_right = 0   -- items right at the first try
  self.attempts = 0
  self.right_run, self.wrong_run = 0, 0
  self.level = 3         -- number of choices for choice games: 2 to 4
  self.tried = false
  self.again = {}        -- items already given back once
  return self
end

function Q:current() return self.queue[1] end
function Q:finished() return #self.queue == 0 end
function Q:is_repeat() return self.again[self.queue[1]] == "back" end

function Q:wrong()
  self.attempts = self.attempts + 1
  self.tried = true
  self.right_run = 0
  self.wrong_run = self.wrong_run + 1
  if self.wrong_run >= 2 then
    self.level = math.max(2, self.level - 1)
    self.wrong_run = 0
  end
end

-- The current item is solved. Moves on to the next one.
function Q:right()
  local item = table.remove(self.queue, 1)
  self.attempts = self.attempts + 1
  local back = self.again[item] == "back"
  if not back then self.done = self.done + 1 end
  if not self.tried then
    if not back then self.first_right = self.first_right + 1 end
    self.wrong_run = 0
    self.right_run = self.right_run + 1
    if self.right_run >= 3 then
      self.level = math.min(4, self.level + 1)
      self.right_run = 0
    end
  elseif not back then
    self.again[item] = "back"
    self.queue[#self.queue + 1] = item
  end
  self.tried = false
end

function Q:stars()
  if self.total == 0 then return 1 end
  local ratio = self.first_right / self.total
  if ratio >= 0.85 then return 3 elseif ratio >= 0.5 then return 2 end
  return 1
end

-- Fisher-Yates
function Q.shuffle(list)
  for i = #list, 2, -1 do
    local j = love.math.random(i)
    list[i], list[j] = list[j], list[i]
  end
  return list
end

return Q
