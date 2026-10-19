-- =====================================================================
-- MISSION : C-130J "DESERT LIFT" (Karte Nevada, Singleplayer)
-- MODUL   : DCS: C-130J von Airplane Simulation Company (Typ "C-130J-30")
-- VERSION : 1.0 (2026-10-19)
-- BENOETIGT: MOOSE (libs/Moose.lua, Build 2026-02-06 / 130d358f),
--            wird im Mission Editor VOR diesem Skript geladen.
-- ---------------------------------------------------------------------
-- Ablauf:
--   1. Hot-Start auf Parkposition G28, Nellis AFB
--   2. Landung auf der improvisierten LZ "YUCCA" (Yucca Lake)
--   3. 4 CDS-Buendel mit dem ASC-Ladesystem einladen
--   4. Start, CARP-Abwurf am DZ "THREE LAKES" (Three Lakes Valley)
--   5. Rueckflug und Landung Nellis AFB
-- Das Skript meldet jede Phase, misst die Abwurfgenauigkeit und steuert
-- die Belebung (Konvoi zur LZ, Bergungstrupp am DZ, Gegner bei der LZ).
-- =====================================================================

local CFG = {
  PlayerUnit       = "HERC 1-1",
  ZoneNellis       = "BLUE_Nellis_Zone1",
  ZoneLZ           = "BLUE_LZ_Zone1",
  ZoneLZCargo      = "BLUE_LZCargo_Zone1",
  ZoneLZSmoke      = "BLUE_LZSmoke_Zone1",
  ZoneDZ           = "BLUE_DZ_Zone1",
  ZoneDZPI         = "BLUE_DZPI_Zone1",
  GroupLZConvoy    = "BLUE_LZConvoy_Group",
  GroupDZRecovery  = "BLUE_DZRecovery_Group",
  TemplateRedTech  = "RED_Technicals_Template",
  CrateType        = "cds_crate",   -- Frachtform der C-130J (siehe MOOSE CTLD, C130basetype)
  CrateCategory    = "Cargos",
  CrateCount       = 4,
  CrateMass        = 900,           -- kg pro CDS-Buendel
  CratePrefix      = "CDS-",
  CrateHeading     = 191,           -- Grad rechtweisend, = LZ-Achse
  LZConvoyDelay    = 480,           -- s nach Missionsstart
  SmokeRangeNM     = 10,            -- Rauch ab dieser Entfernung zum Ziel
  SmokeRepeat      = 290,           -- s, DCS-Rauch erlischt nach 5 min
  DropSearchRadius = 5000,          -- m um den PI
  DropSettleTime   = 45,            -- s Sammelzeit nach dem ersten gelandeten Buendel
  LoopInterval     = 2,             -- s
  MsgTitle         = "DESERT LIFT",
}

local PHASE = { PARKED = 1, OUTBOUND = 2, AT_LZ = 3, TO_DZ = 4, RTB = 5, DONE = 6 }

local state = {
  phase        = PHASE.PARKED,
  tStart       = timer.getTime(),
  tTakeoff     = nil,
  tLZLand      = nil,
  tLZTakeoff   = nil,
  tLand        = nil,
  crates       = {},   -- Name -> { vec3 = Startposition, loaded = bool }
  cratesLoaded = 0,
  dropBaseline = {},   -- Objekte, die schon vor dem Abwurf im DZ lagen
  dropObjects  = {},   -- Name -> { vec3, stillCount }
  dropFirstHit = nil,
  dropResult   = nil,
  lzSmokeT     = -1000,
  dzSmokeT     = -1000,
  redSpawned   = false,
  lzWarned     = false,
  rtbWarned    = false,
}

local zoneNellis  = ZONE:New(CFG.ZoneNellis)
local zoneLZ      = ZONE:New(CFG.ZoneLZ)
local zoneLZCargo = ZONE:New(CFG.ZoneLZCargo)
local zoneLZSmoke = ZONE:New(CFG.ZoneLZSmoke)
local zoneDZ      = ZONE:New(CFG.ZoneDZ)
local zoneDZPI    = ZONE:New(CFG.ZoneDZPI)

local piCoord     = zoneDZPI:GetCoordinate()

-- ---------------------------------------------------------------------
-- Hilfsfunktionen
-- ---------------------------------------------------------------------
local function msg(text, duration)
  MESSAGE:New(text, duration or 20, CFG.MsgTitle):ToAll()
end

local function dist2D(a, b)
  local dx, dz = a.x - b.x, a.z - b.z
  return math.sqrt(dx * dx + dz * dz)
end

local function fmtTime(seconds)
  seconds = math.floor(seconds or 0)
  return string.format("%d:%02d min", math.floor(seconds / 60), seconds % 60)
end

local function getPlayer()
  local unit = UNIT:FindByName(CFG.PlayerUnit)
  if unit and unit:IsAlive() then
    return unit
  end
  return nil
end

local function isStopped(unit)
  return (not unit:InAir()) and unit:GetVelocityKMH() < 10
end

-- ---------------------------------------------------------------------
-- Fracht: 4 CDS-Buendel im 2x2-Block am Ladeplatz der LZ
-- ---------------------------------------------------------------------
local function spawnCrates()
  local base = zoneLZCargo:GetCoordinate()
  for i = 1, CFG.CrateCount do
    local along  = math.floor((i - 1) / 2) * 3
    local across = ((i - 1) % 2) * 3
    local coord  = base:Translate(along, CFG.CrateHeading):Translate(across, CFG.CrateHeading + 90)
    local name   = CFG.CratePrefix .. i
    SPAWNSTATIC:NewFromType(CFG.CrateType, CFG.CrateCategory, country.id.USA)
      :InitCoordinate(coord)
      :InitCargo(true)
      :InitCargoMass(CFG.CrateMass)
      :Spawn(CFG.CrateHeading, name)
    state.crates[name] = { vec3 = coord:GetVec3(), loaded = false }
  end
end

-- Ein Buendel gilt als geladen, sobald es verschwunden ist oder sich
-- mehr als 5 m von seiner Startposition entfernt hat.
local function updateCrates()
  local count = 0
  for name, crate in pairs(state.crates) do
    if not crate.loaded then
      local obj = StaticObject.getByName(name)
      if (not obj) or (not obj:isExist()) or dist2D(obj:getPoint(), crate.vec3) > 5 then
        crate.loaded = true
      end
    end
    if crate.loaded then
      count = count + 1
    end
  end
  if count > state.cratesLoaded then
    state.cratesLoaded = count
    msg(string.format("Loadmaster: %d von %d CDS-Buendeln an Bord.", count, CFG.CrateCount), 10)
    if count == CFG.CrateCount then
      msg("Fracht komplett geladen und gesichert. Rampe schliessen, Start frei nach eigenem Ermessen.\n"
        .. "Naechstes Ziel: DELTA -> IP -> DZ THREE LAKES (CARP).", 20)
    end
  end
end

-- ---------------------------------------------------------------------
-- Abwurf-Auswertung: sucht neue Statics/Fracht im Umkreis des PI
-- ---------------------------------------------------------------------
local function scanDZ(radius)
  local found = {}
  local volume = {
    id = world.VolumeType.SPHERE,
    params = { point = piCoord:GetVec3(), radius = radius },
  }
  local categories = { Object.Category.STATIC }
  if Object.Category.CARGO then
    table.insert(categories, Object.Category.CARGO)
  end
  world.searchObjects(categories, volume, function(obj)
    if obj and obj:isExist() then
      found[obj:getName()] = obj:getPoint()
    end
    return true
  end)
  return found
end

local function evaluateDrop()
  local results = {}
  local sumX, sumZ = 0, 0
  for name, data in pairs(state.dropObjects) do
    local d = dist2D(data.vec3, piCoord:GetVec3())
    table.insert(results, { name = name, dist = d })
    sumX, sumZ = sumX + data.vec3.x, sumZ + data.vec3.z
  end
  if #results == 0 then
    msg("DZ-Kontrolle: Keine Fracht im Umkreis von " .. math.floor(CFG.DropSearchRadius) .. " m um den PI gefunden.", 20)
    return
  end
  table.sort(results, function(a, b) return a.dist < b.dist end)

  local total = 0
  local lines = {}
  for i, r in ipairs(results) do
    total = total + r.dist
    table.insert(lines, string.format("  Buendel %d: %4d m (%4d yd)", i, math.floor(r.dist), math.floor(r.dist * 1.0936)))
  end
  local avg = total / #results
  local grade
  if avg <= 100 then
    grade = "SEHR GUT - Volltreffer"
  elseif avg <= 250 then
    grade = "GUT - innerhalb der DZ"
  elseif avg <= 500 then
    grade = "AUSREICHEND - am Rand der DZ"
  else
    grade = "VERFEHLT - ausserhalb der DZ"
  end
  state.dropResult = { count = #results, avg = avg, best = results[1].dist, grade = grade }

  msg(string.format("DZ-Kontrolle THREE LAKES meldet %d Buendel am Boden:\n%s\nMittlere Ablage zum PI: %d m\nBewertung: %s\n\n"
    .. "Bergungstrupp faehrt zur Fracht. Kurs ECHO -> FOXTROT -> GOLF -> HOTEL, Landung Nellis.",
    #results, table.concat(lines, "\n"), math.floor(avg), grade), 45)

  -- Bergungstrupp faehrt zum Schwerpunkt der Buendel
  local recovery = GROUP:FindByName(CFG.GroupDZRecovery)
  if recovery and recovery:IsAlive() then
    local center = COORDINATE:NewFromVec2({ x = sumX / #results, y = sumZ / #results })
    recovery:RouteGroundTo(center, 35, "Off Road", 5)
  end
  state.phase = PHASE.RTB
end

local function updateDrop()
  local now = timer.getTime()
  for name, vec3 in pairs(scanDZ(CFG.DropSearchRadius)) do
    if not state.dropBaseline[name] then
      local data = state.dropObjects[name]
      if not data then
        state.dropObjects[name] = { vec3 = vec3, stillCount = 0 }
      else
        local agl = vec3.y - land.getHeight({ x = vec3.x, y = vec3.z })
        if dist2D(vec3, data.vec3) < 0.5 and agl < 3 then
          data.stillCount = data.stillCount + 1
          if data.stillCount >= 2 and not state.dropFirstHit then
            state.dropFirstHit = now
            msg("DZ-Kontrolle: Fracht am Boden, werte aus ...", 10)
          end
        else
          data.stillCount = 0
        end
        data.vec3 = vec3
      end
    end
  end
  if state.dropFirstHit and now - state.dropFirstHit >= CFG.DropSettleTime then
    evaluateDrop()
  end
end

-- ---------------------------------------------------------------------
-- Rauchzeichen an LZ (gruen, Aufsetzpunkt RWY 18) und DZ (orange, PI)
-- ---------------------------------------------------------------------
local function smokeLZ(force)
  local now = timer.getTime()
  if force or now - state.lzSmokeT >= CFG.SmokeRepeat then
    zoneLZSmoke:GetCoordinate():SmokeGreen()
    state.lzSmokeT = now
  end
end

local function smokeDZ(force)
  local now = timer.getTime()
  if force or now - state.dzSmokeT >= CFG.SmokeRepeat then
    piCoord:SmokeOrange()
    state.dzSmokeT = now
  end
end

-- ---------------------------------------------------------------------
-- Gegner: zwei Technicals naehern sich der LZ, sobald die Herc dort steht
-- ---------------------------------------------------------------------
local function spawnThreat()
  if state.redSpawned then
    return
  end
  state.redSpawned = true
  SPAWN:New(CFG.TemplateRedTech):Spawn()
  msg("ACHTUNG: Aufklaerung meldet zwei feindliche Technicals ca. 8 km oestlich der LZ, Annaeherung.\n"
    .. "Geschaetzte Ankunft in ca. 15 Minuten. Zuegig laden und abheben!", 25)
end

-- ---------------------------------------------------------------------
-- Phasensteuerung
-- ---------------------------------------------------------------------
local function mainLoop()
  local unit = getPlayer()
  if not unit then
    return
  end
  local coord = unit:GetCoordinate()
  local now = timer.getTime()

  if state.phase == PHASE.PARKED then
    if unit:InAir() then
      state.tTakeoff = now
      state.phase = PHASE.OUTBOUND
      msg("Phase 1: Abflug Nellis. SID fliegen, dann ALPHA -> BRAVO -> CHARLIE.\n"
        .. "Transit 8.500 ft MSL. LZ YUCCA: Landung RWY 18, gruener Rauch am Aufsetzpunkt.", 25)
    end

  elseif state.phase == PHASE.OUTBOUND then
    if coord:Get2DDistance(zoneLZ:GetCoordinate()) < CFG.SmokeRangeNM * 1852 then
      smokeLZ(false)
    end
    if isStopped(unit) then
      if zoneLZ:IsCoordinateInZone(coord) then
        state.tLZLand = now
        state.phase = PHASE.AT_LZ
        msg(string.format("Phase 2: Gelandet auf LZ YUCCA nach %s Flugzeit.\n"
          .. "Zum Ladeplatz (Westseite, Suedende) rollen, Heck zu den 4 CDS-Buendeln, Rampe oeffnen\n"
          .. "und die Fracht mit dem Loadmaster/EFB einladen.", fmtTime(now - (state.tTakeoff or now))), 30)
        spawnThreat()
      elseif zoneNellis:IsCoordinateInZone(coord) and not state.lzWarned then
        state.lzWarned = true
        msg("Zurueck in Nellis ohne Fracht - Mission noch nicht erfuellt. Ziel ist die LZ YUCCA.", 15)
      end
    end

  elseif state.phase == PHASE.AT_LZ then
    updateCrates()
    smokeLZ(false)
    if unit:InAir() and not zoneLZ:IsCoordinateInZone(coord) then
      if state.cratesLoaded == 0 then
        msg("Keine Fracht an Bord! Zurueck zur LZ YUCCA und die CDS-Buendel einladen.", 20)
        state.phase = PHASE.OUTBOUND
      else
        state.tLZTakeoff = now
        state.phase = PHASE.TO_DZ
        for name, obj in pairs(scanDZ(CFG.DropSearchRadius)) do
          state.dropBaseline[name] = true
        end
        msg(string.format("Phase 3: Abflug LZ mit %d/%d Buendeln, Bodenzeit %s.\n"
          .. "DELTA -> IP -> PI. Run-in 168 MAG, Abwurf 600 ft AGL (3.610 ft MSL), 130 KIAS.\n"
          .. "Oranger Rauch markiert den PI.", state.cratesLoaded, CFG.CrateCount,
          fmtTime(now - (state.tLZLand or now))), 30)
      end
    end

  elseif state.phase == PHASE.TO_DZ then
    if coord:Get2DDistance(piCoord) < CFG.SmokeRangeNM * 1852 then
      smokeDZ(false)
    end
    updateDrop()
    if isStopped(unit) and zoneNellis:IsCoordinateInZone(coord) and not state.rtbWarned then
      state.rtbWarned = true
      msg("Gelandet in Nellis, aber kein Abwurf erkannt.\n"
        .. "Falls die Fracht abgeworfen wurde: F10 -> DESERT LIFT -> Abwurf jetzt auswerten.", 20)
    end

  elseif state.phase == PHASE.RTB then
    if isStopped(unit) and zoneNellis:IsCoordinateInZone(coord) then
      state.tLand = now
      state.phase = PHASE.DONE
      local r = state.dropResult
      msg(string.format("MISSION ERFUELLT - Willkommen zurueck in Nellis!\n\n"
        .. "Gesamtflugzeit: %s\nBodenzeit LZ: %s\nAbgeworfene Buendel: %d\nMittlere Ablage: %d m\nBewertung: %s",
        fmtTime(now - (state.tTakeoff or now)), fmtTime((state.tLZTakeoff or 0) - (state.tLZLand or 0)),
        r and r.count or 0, r and math.floor(r.avg) or 0, r and r.grade or "-"), 60)
    end
  end
end

-- ---------------------------------------------------------------------
-- F10-Menue
-- ---------------------------------------------------------------------
local function showData()
  msg("MISSIONSDATEN (Details: Kneeboard)\n"
    .. "LZ YUCCA : N3657.40 W11601.49 (Schwelle RWY 18), ELEV 3921 ft\n"
    .. "           RWY 18/36, 180/360 MAG (191/011 TRUE), 3500 x 90 ft, Seeboden\n"
    .. "DZ PI    : N3643.32 W11537.80, ELEV 3010 ft\n"
    .. "           Run-in 168 MAG, Abwurf 600 ft AGL = 3610 ft MSL, 130 KIAS, CDS\n"
    .. "Nellis   : TWR 132.55 / 327.0, TACAN 12X, ILS 21L 109.10 (IDIQ)", 40)
end

local function showStatus()
  local names = {
    [PHASE.PARKED] = "Auf Parkposition Nellis",
    [PHASE.OUTBOUND] = "Unterwegs zur LZ YUCCA",
    [PHASE.AT_LZ] = "Auf der LZ - Fracht laden",
    [PHASE.TO_DZ] = "Unterwegs zum DZ THREE LAKES",
    [PHASE.RTB] = "Rueckflug nach Nellis",
    [PHASE.DONE] = "Mission erfuellt",
  }
  msg(string.format("Status: %s\nFracht an Bord/geladen: %d von %d", names[state.phase],
    state.cratesLoaded, CFG.CrateCount), 15)
end

local function forceDropEvaluation()
  if state.phase ~= PHASE.TO_DZ then
    msg("Auswertung nur nach dem Abflug von der LZ moeglich.", 10)
    return
  end
  for name, vec3 in pairs(scanDZ(CFG.DropSearchRadius * 2)) do
    if not state.dropBaseline[name] then
      state.dropObjects[name] = { vec3 = vec3, stillCount = 2 }
    end
  end
  evaluateDrop()
end

local menu = missionCommands.addSubMenu("DESERT LIFT")
missionCommands.addCommand("Missionsdaten anzeigen", menu, showData)
missionCommands.addCommand("Status anzeigen", menu, showStatus)
missionCommands.addCommand("Rauch LZ erneuern", menu, function() smokeLZ(true) end)
missionCommands.addCommand("Rauch DZ erneuern", menu, function() smokeDZ(true) end)
missionCommands.addCommand("Abwurf jetzt auswerten", menu, forceDropEvaluation)

-- ---------------------------------------------------------------------
-- Start
-- ---------------------------------------------------------------------
spawnCrates()

TIMER:New(function()
  local convoy = GROUP:FindByName(CFG.GroupLZConvoy)
  if convoy then
    convoy:Activate()
  end
end):Start(CFG.LZConvoyDelay)

TIMER:New(mainLoop):Start(5, CFG.LoopInterval)

msg("DESERT LIFT - Willkommen an Bord, HERC 1.\n"
  .. "Triebwerke laufen. Auftrag: Fracht von der improvisierten LZ YUCCA holen,\n"
  .. "per CARP-Abwurf am DZ THREE LAKES absetzen und nach Nellis zurueckkehren.\n"
  .. "Kneeboard: RShift+K. Missionsdaten: F10-Menue.", 30)
env.info("DESERT LIFT: Missionsskript geladen.")
