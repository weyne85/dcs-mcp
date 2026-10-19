"""Erzeugt C130J_Desert_Lift.miz (Nevada) mit pydcs."""
import sys, os
from datetime import datetime
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))

import dcs
from dcs import task
from dcs.terrain import Nevada
from dcs.mapping import LatLng, Point
from dcs.planes import C_130
from dcs.point import PointAction
from dcs.mission import StartType
from dcs.weather import Wind
from dcs.triggers import TriggerStart, TriggerOnce, Event
from dcs.action import DoScriptFile
from dcs.condition import TimeAfter
from dcs import vehicles as V

from geo import *
from brief import BRIEF_SITUATION, BRIEF_TASK

HERE = Path(__file__).resolve().parent
OUT = HERE.parent                  # missions/C130J_Desert_Lift
REPO = OUT.parents[1]              # Repo-Wurzel (libs/Moose.lua)
KNEE = OUT / "kneeboards"
FT = 0.3048
KT = 1.852


class C130J30(C_130):
    """DCS: C-130J (Airplane Simulation Company). Typname laut MOOSE: "C-130J-30"."""
    id = "C-130J-30"
    flyable = True
    height = 11.84
    width = 40.41
    length = 34.37
    fuel_max = 20830


terrain = Nevada()
m = dcs.Mission(terrain)
m.coalition["red"].add_country(dcs.countries.Insurgents())
usa = m.country("USA")
ins = m.country("Insurgents")


def P(lat, lon):
    return Point.from_latlng(LatLng(lat, lon), terrain)


# ------------------------------------------------------------------ Zeit / Wetter
m.start_time = datetime(2026, 4, 18, 9, 0, 0)
w = m.weather
w.season_temperature = 18
w.qnh = 760
w.visibility_distance = 80000
w.clouds_density = 0
w.clouds_thickness = 200
w.clouds_base = 3000
w.enable_fog = False
w.enable_dust = False
w.turbulence_at_ground = 0
# DCS speichert die Richtung, in die der Wind weht (Wind aus 200 -> 20)
w.wind_at_ground = Wind(20, 2.5)   # aus 200, ca. 5 kt
w.wind_at_2000 = Wind(30, 4.0)     # aus 210, ca. 8 kt
w.wind_at_8000 = Wind(40, 7.0)     # aus 220, ca. 14 kt

# ------------------------------------------------------------------ Trigger-Zonen
nellis = terrain.airports["Nellis"]
lz_cargo = dest(*dest(*LZ_S, LZ_TRUE, 120), LZ_TRUE + 270, 70)
m.triggers.add_triggerzone(nellis.position, 5000, name="BLUE_Nellis_Zone1")
m.triggers.add_triggerzone(P(*LZ_C), 700, name="BLUE_LZ_Zone1")
m.triggers.add_triggerzone(P(*lz_cargo), 30, name="BLUE_LZCargo_Zone1")
m.triggers.add_triggerzone(P(*dest(*LZ_N, LZ_TRUE + 180, 60)), 20, name="BLUE_LZSmoke_Zone1")
m.triggers.add_triggerzone(P(*DZ_PI), 500, name="BLUE_DZ_Zone1")
m.triggers.add_triggerzone(P(*DZ_PI), 25, name="BLUE_DZPI_Zone1")

# ------------------------------------------------------------------ Spieler: HERC 1
slot = [s for s in nellis.parking_slots if s.slot_name == "G28"][0]
herc = m.flight_group_from_airport(usa, "HERC 1", C130J30, nellis, maintask=task.Transport,
                                   start_type=StartType.Warm, parking_slots=[slot])
u = herc.units[0]
u.name = "HERC 1-1"
u.set_player()
u.fuel = 12000
u.onboard_num = "130"  # feste Hecknummer, damit die .miz reproduzierbar bleibt

wp = {w[0]: w for w in WPTS}
for name, lat, lon, alt_ft, _ in WPTS:
    spd = 130 * KT if name in ("IP", "PI") else 240 * KT
    p = herc.add_waypoint(P(lat, lon), alt_ft * FT, spd, name=name)
    if name == "LZ":
        p.name = "LZ YUCCA"
herc.land_at(nellis)


# ------------------------------------------------------------------ Bodeneinheiten
def ground(country, name, units, pos, heading, spacing=8, along=None, late=False):
    """units: Liste von Typen; Aufstellung in Reihe quer zur Blickrichtung."""
    g = m.vehicle_group(country, name, units[0], P(*pos), heading=heading)
    g.units[0].name = name + "-1"
    for i, t in enumerate(units[1:], start=2):
        unit = m.vehicle(name + "-" + str(i), t)
        q = dest(*pos, (along if along is not None else heading + 90), spacing * (i - 1))
        unit.position = P(*q)
        unit.heading = heading
        g.add_unit(unit)
    g.late_activation = late
    return g


# LZ YUCCA: Sicherung, Truppe, Versorgung
lz_east_mid = dest(*LZ_C, LZ_TRUE + 90, 180)
lz_east_south = dest(*dest(*LZ_S, LZ_TRUE, 150), LZ_TRUE + 90, 150)
g = ground(usa, "BLUE_LZSecurity_Group", [V.Armor.M1043_HMMWV_Armament, V.Armor.M1043_HMMWV_Armament],
           lz_east_mid, 90, spacing=250, along=LZ_TRUE + 180)
g = ground(usa, "BLUE_LZTroops_Group", [V.Infantry.Soldier_M4, V.Infantry.Soldier_M4, V.Infantry.Soldier_M249,
                                        V.Infantry.Soldier_M4, V.Infantry.Soldier_M4],
           dest(*lz_cargo, LZ_TRUE + 270, 25), LZ_TRUE + 90, spacing=4, along=LZ_TRUE)
g = ground(usa, "BLUE_LZSupport_Group", [V.Unarmed.M978_HEMTT_Tanker, V.Unarmed.Hummer],
           dest(*dest(*lz_cargo, LZ_TRUE + 180, 60), LZ_TRUE + 270, 30), LZ_TRUE, spacing=15, along=LZ_TRUE + 270)

# Konvoi zur LZ (Late Activation, Skript aktiviert nach 8 min)
conv_start = (36.9050, -115.9950)
conv_end = dest(*lz_cargo, LZ_TRUE + 180, 30)
g = ground(usa, "BLUE_LZConvoy_Group", [V.Armor.M1043_HMMWV_Armament, V.Unarmed.M_818, V.Unarmed.M_818,
                                        V.Unarmed.M_818], conv_start, 300, spacing=20, along=120, late=True)
g.add_waypoint(P(*conv_end), PointAction.OffRoad, 30)

# Gegner: zwei Technicals (Template, Late Activation, Skript spawnt bei Landung auf der LZ)
red_start = dest(*LZ_C, 95, 8000)
red_end = dest(*LZ_C, 100, 1300)
g = ground(ins, "RED_Technicals_Template", [V.Armor.HL_DSHK, V.Armor.HL_DSHK], red_start, 275, spacing=25,
           along=95, late=True)
g.add_waypoint(P(*red_end), PointAction.OffRoad, 30)

# DZ THREE LAKES: DZ-Kontrolltrupp und Bergungstrupp
g = ground(usa, "BLUE_DZTeam_Group", [V.Unarmed.Hummer, V.Infantry.Soldier_M4, V.Infantry.Soldier_M4,
                                      V.Infantry.Soldier_M249], dest(*DZ_PI, 270, 350), 90, spacing=5, along=0)
g = ground(usa, "BLUE_DZRecovery_Group", [V.Armor.M1043_HMMWV_Armament, V.Unarmed.M_818, V.Unarmed.M_818],
           dest(*DZ_PI, 215, 800), 35, spacing=15, along=215)

# ------------------------------------------------------------------ Skripte
moose = m.map_resource.add_resource_file(str(REPO / "libs/Moose.lua"))
script = m.map_resource.add_resource_file(str(OUT / "C130J_Desert_Lift.lua"))
t1 = TriggerStart(comment="Load MOOSE")
t1.add_action(DoScriptFile(moose))
m.triggerrules.triggers.append(t1)
t2 = TriggerOnce(Event.NoEvent, "Load Desert Lift")
t2.add_condition(TimeAfter(2))
t2.add_action(DoScriptFile(script))
m.triggerrules.triggers.append(t2)

# ------------------------------------------------------------------ Kneeboards
for png in sorted(KNEE.glob("*.png")):
    m.add_aircraft_kneeboard(C130J30, png)

# ------------------------------------------------------------------ Briefing
m.set_description_text(BRIEF_SITUATION)
m.set_description_bluetask_text(BRIEF_TASK)
m.set_description_redtask_text("Keine spielbare Seite.")

m.save(str(OUT / "C130J_Desert_Lift.miz"))
print("saved")
