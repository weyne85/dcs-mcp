local function at(zone, dx, dz) local z = ZONES[zone]; return COORDINATE:New(z.x + (dx or 0), 0, z.z + (dz or 0)) end
local function check(cond, text) if not cond then error("FAIL: " .. text) end; print("  OK: " .. text) end
-- Spieler parkt in Nellis
PLAYER.c = at("BLUE_Nellis_Zone1", 300, 0)
SIM.run(20)
check(SIM.statics["CDS-1"] and SIM.statics["CDS-4"], "4 CDS-Kisten gespawnt")
check(SIM.statics["CDS-1"].type == "cds_crate" and SIM.statics["CDS-1"].cargo == true and SIM.statics["CDS-1"].mass == 900, "Kisten: Typ/Cargo/Masse")
local c1, cz = SIM.statics["CDS-1"].p, ZONES["BLUE_LZCargo_Zone1"]
check(math.abs(c1.x - cz.x) < 1 and math.abs(c1.z - cz.z) < 1, "Kiste 1 im Ladeplatz-Zentrum")
-- Start
PLAYER.air = true; PLAYER.v = 300; PLAYER.c = at("BLUE_Nellis_Zone1", 6000, 0)
SIM.run(30)
check(SIM.msgs[#SIM.msgs]:find("Phase 1"), "Phase 1 gemeldet")
SIM.run(500)
check(SIM.activated["BLUE_LZConvoy_Group"] == 480, "Konvoi nach 480 s aktiviert")
-- Anflug LZ (8 NM) -> Rauch
PLAYER.c = at("BLUE_LZ_Zone1", 8 * 1852, 0)
SIM.run(510)
check(#SIM.smoke == 1 and SIM.smoke[1]:find("green"), "Gruener Rauch bei 8 NM")
-- Landung LZ
PLAYER.c = at("BLUE_LZ_Zone1", 200, 0); PLAYER.air = false; PLAYER.v = 3
SIM.run(520)
check(SIM.msgs[#SIM.msgs]:find("ACHTUNG") and SIM.spawned["RED_Technicals_Template"], "Landung LZ + Gegner gespawnt")
check(SIM.msgs[#SIM.msgs - 1]:find("Phase 2"), "Phase 2 gemeldet")
-- Laden: 2 Kisten verschwinden, 2 werden bewegt
SIM.statics["CDS-1"] = nil; SIM.statics["CDS-2"] = nil
SIM.run(530)
check(SIM.msgs[#SIM.msgs]:find("2 von 4"), "2/4 geladen")
SIM.statics["CDS-3"].p = { x = SIM.statics["CDS-3"].p.x + 10, y = 0, z = SIM.statics["CDS-3"].p.z }
SIM.statics["CDS-4"] = nil
SIM.run(540)
check(SIM.msgs[#SIM.msgs]:find("komplett"), "4/4 geladen")
-- CDS-3 "an Bord" bewegt sich mit, wir entfernen es fuer den Flug
SIM.statics["CDS-3"] = nil
-- Start von der LZ
PLAYER.air = true; PLAYER.v = 250; PLAYER.c = at("BLUE_LZ_Zone1", 0, 3000)
SIM.run(550)
check(SIM.msgs[#SIM.msgs]:find("Phase 3"), "Phase 3 gemeldet")
-- Anflug DZ
PLAYER.c = at("BLUE_DZPI_Zone1", 5 * 1852, 0)
SIM.run(560)
check(SIM.smoke[#SIM.smoke]:find("orange"), "Oranger Rauch am PI")
-- Abwurf: 4 neue Objekte am Boden, 50/80/120/200 m vom PI
local pi = ZONES["BLUE_DZPI_Zone1"]
for i, d in ipairs({ 50, 80, 120, 200 }) do SIM.statics["Drop" .. i] = { p = { x = pi.x + d, y = 0.5, z = pi.z } } end
SIM.run(700)
check(SIM.msgs[#SIM.msgs]:find("Bewertung: GUT"), "Auswertung: Mittel 112 m -> GUT")
check(SIM.msgs[#SIM.msgs]:find("4 Buendel"), "4 Buendel gezaehlt")
local r = SIM.routes["BLUE_DZRecovery_Group"]
check(r and math.abs(r.c.x - (pi.x + 112.5)) < 1 and r.s == 35 and r.f == "Off Road", "Bergungstrupp faehrt zum Schwerpunkt")
-- Landung Nellis
PLAYER.c = at("BLUE_Nellis_Zone1", 500, 0); PLAYER.air = false; PLAYER.v = 0
SIM.run(710)
check(SIM.msgs[#SIM.msgs]:find("MISSION ERFUELLT"), "Mission erfuellt")
-- F10-Menue
for _, n in ipairs({ "Missionsdaten anzeigen", "Status anzeigen", "Rauch LZ erneuern", "Rauch DZ erneuern", "Abwurf jetzt auswerten" }) do
  check(SIM.cmds[n], "F10: " .. n); SIM.cmds[n]()
end
print("ALLE TESTS BESTANDEN")
