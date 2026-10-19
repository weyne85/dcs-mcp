"""Simulierter Durchlauf des Missionsskripts (Lua 5.1 via lupa, DCS/MOOSE als Stubs).

Aufruf: python generator/test/run_test.py
"""
import os, re, zipfile
from pathlib import Path
from lupa import lua51

HERE = Path(__file__).resolve().parent
MISSION_DIR = HERE.parents[1]
os.chdir(HERE)
L = lua51.LuaRuntime(unpack_returned_tuples=True)
with zipfile.ZipFile(MISSION_DIR / "C130J_Desert_Lift.miz") as z:
    mis = z.read("mission").decode("utf-8")
# Trigger-Zonen aus der mission-Datei lesen
zones = {}
for m in re.finditer(r'\["name"\]="(BLUE_\w+_Zone1)",.*?\["radius"\]=([\d.]+),.*?\["x"\]=(-?[\d.]+),\s*\["y"\]=(-?[\d.]+)', mis, re.S):
    zones[m.group(1)] = (float(m.group(3)), float(m.group(4)), float(m.group(2)))
print("zones", {k: tuple(round(x) for x in v) for k, v in zones.items()})
L.execute("ZONES = {}")
for k, (x, y, r) in zones.items():
    L.execute(f'ZONES["{k}"] = {{ x = {x}, z = {y}, r = {r} }}')
L.execute(open("stubs.lua").read())
L.execute((MISSION_DIR / "C130J_Desert_Lift.lua").read_text(encoding="utf-8"))
L.execute(open("scenario.lua").read())
