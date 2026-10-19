SIM = { t = 0, msgs = {}, statics = {}, timers = {}, cmds = {}, smoke = {}, routes = {}, activated = {}, spawned = {} }
ZONES = ZONES or {}
timer = { getTime = function() return SIM.t end }
env = { info = function(s) print("[env] " .. s) end }
country = { id = { USA = 2 } }
Object = { Category = { UNIT = 1, STATIC = 3, CARGO = 6 } }
world = { VolumeType = { SPHERE = 2 } }
land = { getHeight = function(v2) return 0 end }
function world.searchObjects(cats, vol, fn)
  local p, r = vol.params.point, vol.params.radius
  for name, s in pairs(SIM.statics) do
    local dx, dz = s.p.x - p.x, s.p.z - p.z
    if math.sqrt(dx*dx+dz*dz) <= r then
      fn({ isExist = function() return true end, getName = function() return name end, getPoint = function() return s.p end })
    end
  end
end
StaticObject = { getByName = function(name)
  local s = SIM.statics[name]; if not s then return nil end
  return { isExist = function() return true end, getPoint = function() return s.p end }
end }
missionCommands = {
  addSubMenu = function(n) return n end,
  addCommand = function(n, menu, fn) SIM.cmds[n] = fn end,
}
-- MOOSE-Stubs (nur verwendete Methoden)
COORDINATE = {}; COORDINATE.__index = COORDINATE
function COORDINATE:New(x, y, z) return setmetatable({ x = x, y = y or 0, z = z }, COORDINATE) end
function COORDINATE:NewFromVec2(v) return COORDINATE:New(v.x, 0, v.y) end
function COORDINATE:GetVec3() return { x = self.x, y = self.y, z = self.z } end
function COORDINATE:Translate(d, a)
  local r = math.rad(a); return COORDINATE:New(self.x + d * math.cos(r), self.y, self.z + d * math.sin(r))
end
function COORDINATE:Get2DDistance(o) local dx, dz = self.x - o.x, self.z - o.z; return math.sqrt(dx*dx+dz*dz) end
function COORDINATE:SmokeGreen() table.insert(SIM.smoke, "green@" .. SIM.t) end
function COORDINATE:SmokeOrange() table.insert(SIM.smoke, "orange@" .. SIM.t) end
ZONE = {}; ZONE.__index = ZONE
function ZONE:New(name) local z = assert(ZONES[name], "zone missing: " .. name); return setmetatable({ n = name, x = z.x, z = z.z, r = z.r }, ZONE) end
function ZONE:GetCoordinate() return COORDINATE:New(self.x, 0, self.z) end
function ZONE:IsCoordinateInZone(c) local dx, dz = c.x - self.x, c.z - self.z; return math.sqrt(dx*dx+dz*dz) <= self.r end
MESSAGE = {}; MESSAGE.__index = MESSAGE
function MESSAGE:New(t, d, c) return setmetatable({ t = t }, MESSAGE) end
function MESSAGE:ToAll() table.insert(SIM.msgs, self.t); print(("[%5ds] MSG: %s"):format(SIM.t, self.t:gsub("\n", " | "))) end
PLAYER = { alive = true, air = false, v = 0, c = COORDINATE:New(0, 0, 0) }
UNIT = { FindByName = function(_, n)
  if n ~= "HERC 1-1" or not PLAYER.alive then return nil end
  return { IsAlive = function() return true end, InAir = function() return PLAYER.air end,
           GetVelocityKMH = function() return PLAYER.v end, GetCoordinate = function() return PLAYER.c end }
end }
GROUP = { FindByName = function(_, n)
  return { Activate = function() SIM.activated[n] = SIM.t end, IsAlive = function() return true end,
           RouteGroundTo = function(_, c, s, f, d) SIM.routes[n] = { c = c, s = s, f = f } end }
end }
SPAWN = { New = function(_, n) return { Spawn = function() SIM.spawned[n] = SIM.t end } end }
SPAWNSTATIC = { NewFromType = function(_, t, cat, cid)
  local o = { t = t, cat = cat }
  function o:InitCoordinate(c) self.c = c; return self end
  function o:InitCargo(b) self.cargo = b; return self end
  function o:InitCargoMass(m) self.m = m; return self end
  function o:Spawn(h, name) SIM.statics[name] = { p = self.c:GetVec3(), type = t, cargo = self.cargo, mass = self.m }; return self end
  return o
end }
TIMER = { New = function(_, fn) local o = { fn = fn }
  function o:Start(t0, dt) self.next = t0; self.dt = dt; table.insert(SIM.timers, self); return self end
  return o end }
function SIM.run(until_t)
  while SIM.t < until_t do
    SIM.t = SIM.t + 1
    for _, tm in ipairs(SIM.timers) do
      if tm.next and SIM.t >= tm.next then tm.fn(); tm.next = tm.dt and (tm.next + tm.dt) or nil end
    end
  end
end
