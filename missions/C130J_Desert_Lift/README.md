# Mission „DESERT LIFT“ – C-130J (ASC), Karte Nevada

Singleplayer-Transportmission für das Modul **DCS: C-130J** von Airplane Simulation Company
(DCS-Typname `C-130J-30`).

Ablauf: Hot-Start in Nellis → Landung auf einer improvisierten LZ → Fracht laden →
CARP-Luftabwurf am DZ → Rückflug und Landung in Nellis.

---

## 1. Dateien

| Datei | Zweck |
|---|---|
| `C130J_Desert_Lift.miz` | Fertige Mission (enthält MOOSE, Skript und Kneeboards) |
| `C130J_Desert_Lift.lua` | Missionsskript (identisch mit der Version in der `.miz`) |
| `kneeboards/*.png` | 8 Kneeboard-Seiten (auch in der `.miz` enthalten) |
| `generator/` | Python-Generator für `.miz` und Kneeboards + Skripttest (siehe Abschnitt 12) |
| `README.md` | Diese Datei |

Hinweis: Die Repo-Regel „pro Mission nur `.lua` + `README.md`“ ist hier auf ausdrücklichen Wunsch erweitert
(`.miz`, Kneeboards, Generator).

## 2. Voraussetzungen und Versionen

- DCS World mit Karte **Nevada** und Modul **C-130J** (ASC)
- **MOOSE**: `libs/Moose.lua`, Build `2026-02-06T12:37:28+01:00-130d358f` (in der `.miz` enthalten)
- MiST: nicht verwendet
- CTLD: nicht verwendet

## 3. Installation

1. `C130J_Desert_Lift.miz` nach `Saved Games\DCS\Missions\` kopieren.
2. In DCS: **Mission** → Datei öffnen → Start.
3. Kneeboard im Cockpit: `RShift+K`, blättern mit `[` und `]`.

---

## 4. Missionsablauf

| Phase | Was passiert | Skript-Meldung |
|---|---|---|
| 0 | Hot-Start auf Parkposition **G28**, Nellis AFB | Begrüßung |
| 1 | Start RWY 21L/R (SID), Route ALPHA → BRAVO → CHARLIE | „Phase 1“ |
| 2 | Landung **LZ YUCCA**, RWY 18. Grüner Rauch ab 10 NM | „Phase 2“ + Feindmeldung |
| 3 | 4 CDS-Bündel mit dem ASC-Ladesystem laden | „x von 4 an Bord“ |
| 4 | Start, DELTA → IP → PI, CARP-Abwurf. Oranger Rauch am PI | „Phase 3“, Auswertung |
| 5 | ECHO → FOXTROT → GOLF → HOTEL, ILS 21L/Sichtanflug | „Mission erfüllt“ + Bilanz |

**Bewertung der Abwurfgenauigkeit** (mittlere Ablage aller Bündel zum PI):
bis 100 m = sehr gut · bis 250 m = gut · bis 500 m = ausreichend · darüber = verfehlt.

## 5. Orte und Daten

Missweisung: 11° Ost (WMM 2025). Höhen in ft MSL.

**LZ YUCCA** (ausgetrockneter Yucca Lake, Seeboden laut USGS-Höhendaten auf ca. 4 × 2,5 km eben, 3921 ft)

| Wert | Daten |
|---|---|
| Richtung | 18/36 = 180°/360° MAG (191°/011° TRUE) |
| Maße | 3.500 × 90 ft |
| Schwelle 18 (Nord) | N3657.40 W11601.49 |
| Schwelle 36 (Süd) | N3656.84 W11601.63 |
| Ladeplatz | 120 m nördlich der Schwelle 36, 70 m westlich der Mittellinie |

**DZ THREE LAKES** (Three Lakes Valley, Talboden ca. 3010 ft, ca. 3 × 3 km eben)

| Wert | Daten |
|---|---|
| PI | N3643.32 W11537.80, ELEV 3010 ft |
| IP | N3649.20 W11537.92 |
| Run-in | 168° MAG, 5,9 NM |
| Abwurf | 600 ft AGL (3.610 ft MSL), 130 KIAS, CDS |

**Route** (Gelände ±1,5 NM entlang jeder Etappe mit USGS-Höhendaten geprüft)

| CNI | Name | Koordinate | Höhe | Kurs MAG / NM | max. Gelände |
|---|---|---|---|---|---|
| LL01 | ALPHA | N3630.00W11526.40 | 8.500 | 298 / 25,3 | 4.450 |
| LL02 | BRAVO | N3644.40W11558.80 | 8.500 | 288 / 29,7 | 5.570 |
| LL03 | CHARLIE | N3701.33W11600.54 | 5.500 | 344 / 17,0 | 4.717 |
| LL04 | LZ | N3657.40W11601.49 | 3.921 | 180 / 4,0 | 4.255 |
| LL05 | DELTA | N3655.80W11537.80 | 8.500 | 084 / 19,0 | 5.929 |
| LL06 | IP | N3649.20W11537.92 | 3.610 | 170 / 6,6 | 3.534 (Tal) |
| LL07 | PI | N3643.32W11537.80 | 3.610 | 168 / 5,9 | ca. 3.100 (Tal) |
| LL08 | ECHO | N3636.00W11533.00 | 6.500 | 141 / 8,3 | 5.101 |
| LL09 | FOXTROT | N3624.00W11521.60 | 6.500 | 132 / 15,1 | 3.365 |
| LL10 | GOLF | N3618.00W11509.00 | 5.500 | 110 / 11,8 | 3.139 |
| LL11 | HOTEL | N3623.56W11452.81 | 5.500 | 056 / 14,2 | 3.883 |

HOTEL liegt 12 NM vor Nellis auf der Anfluglinie 21L (207° MAG).

**Nellis AFB:** TWR 132.55 / 327.0 · TACAN 12X (LSV) · ILS 21L 109.10 (IDIQ) · Elevation 1.870 ft.
**Wetter:** 18.04.2026, 09:00 Uhr, CAVOK, Wind 200°/5 kt (Boden), 210°/8 kt (2000 m), 220°/14 kt (8000 m), QNH 29.92.

---

## 6. Einheiten

| Gruppe | Einheiten (Name → Typ) | Seite/Land | Ort | Late Act. | Skill | Route / Trigger |
|---|---|---|---|---|---|---|
| `HERC 1` | `HERC 1-1` → `C-130J-30` | Blau/USA | Nellis, Parkposition G28 (Hot) | nein | Player | ALPHA … HOTEL, Landung Nellis. Treibstoff 12.000 kg |
| `BLUE_LZSecurity_Group` | `-1`, `-2` → M1043 HMMWV Armament | Blau/USA | 180 m östl. der LZ-Mitte, N3657.10 W11601.44 | nein | Average | stationär, Sicherung gegen Osten |
| `BLUE_LZTroops_Group` | `-1`…`-5` → 4× Soldier M4, 1× Soldier M249 | Blau/USA | am Ladeplatz, N3656.91 W11601.68 | nein | Average | stationär |
| `BLUE_LZSupport_Group` | `-1` → M978 HEMTT Tanker, `-2` → Hummer | Blau/USA | südl. des Ladeplatzes, N3656.88 W11601.69 | nein | Average | stationär |
| `BLUE_LZConvoy_Group` | `-1` → M1043, `-2`…`-4` → M 818 | Blau/USA | 6 km SO der LZ, N3654.30 W11559.70 | **ja** (Skript aktiviert nach 8 min) | Average | fährt mit 30 km/h zum Ladeplatz |
| `RED_Technicals_Template` | `-1`, `-2` → HL_DSHK | Rot/Insurgents | 8 km östl. der LZ, N3656.74 W11556.18 | **ja** (Skript spawnt bei Landung auf der LZ) | Average | fährt mit 30 km/h bis 1,3 km östl. der LZ |
| `BLUE_DZTeam_Group` | `-1` → Hummer, `-2`…`-4` → 2× Soldier M4, 1× Soldier M249 | Blau/USA | 350 m westl. des PI, N3643.32 W11538.04 | nein | Average | stationär (DZ-Kontrolle) |
| `BLUE_DZRecovery_Group` | `-1` → M1043, `-2`, `-3` → M 818 | Blau/USA | 800 m SW des PI, N3642.97 W11538.11 | nein | Average | Skript schickt sie nach dem Abwurf zur Fracht |
| *(Skript)* `CDS-1`…`CDS-4` | Static `cds_crate`, Kategorie `Cargos`, canCargo, 900 kg | Blau/USA | 2×2-Block in `BLUE_LZCargo_Zone1` | – | – | per `SPAWNSTATIC` bei Missionsstart |

## 7. Trigger-Zonen

| Zone | Radius | Mitte | Zweck |
|---|---|---|---|
| `BLUE_Nellis_Zone1` | 5000 m | Nellis AFB | Start/Landung erkennen |
| `BLUE_LZ_Zone1` | 700 m | N3657.12 W11601.56 | Landung auf der LZ erkennen |
| `BLUE_LZCargo_Zone1` | 30 m | N3656.91 W11601.66 | Fracht-Spawn |
| `BLUE_LZSmoke_Zone1` | 20 m | N3657.37 W11601.50 | Grüner Rauch (Aufsetzpunkt RWY 18) |
| `BLUE_DZ_Zone1` | 500 m | N3643.32 W11537.80 | Grenze der DZ (Bewertung) |
| `BLUE_DZPI_Zone1` | 25 m | N3643.32 W11537.80 | PI: Rauch, Ablage-Messung |

## 8. Trigger (Ladereihenfolge)

| Nr | Typ | Bedingung | Aktion |
|---|---|---|---|
| 1 | MISSION START | – | DO SCRIPT FILE `Moose.lua` |
| 2 | ONCE | TIME MORE 2 | DO SCRIPT FILE `C130J_Desert_Lift.lua` |

## 9. Skriptlogik (Kurzfassung)

- Eine Schleife (alle 2 s) verfolgt `HERC 1-1` durch die Phasen.
  Landungen werden über „am Boden + < 10 km/h + in Zone“ erkannt, nicht über DCS-Land-Events.
  So funktioniert es auch auf der LZ ohne Flugplatz.
- **Laden:** Ein Bündel gilt als geladen, sobald das Static verschwindet oder sich > 5 m bewegt.
- **Abwurf:** Ab dem Start von der LZ sucht das Skript im Umkreis von 5 km um den PI nach neuen
  Statics/Cargo-Objekten. Sie werden ausgewertet, sobald sie am Boden liegen (AGL < 3 m) und still stehen.
  45 s nach dem ersten Bündel folgt die Auswertung.
- **F10-Menü „DESERT LIFT“:** Missionsdaten · Status · Rauch LZ/DZ erneuern · Abwurf jetzt auswerten (Suchradius 10 km).
- Alle MOOSE-Funktionen sind gegen die mitgelieferte `libs/Moose.lua` geprüft:
  `ZONE:New`, `ZONE_BASE:IsCoordinateInZone`, `ZONE_BASE:GetCoordinate`, `COORDINATE:Translate`,
  `COORDINATE:Get2DDistance`, `COORDINATE:NewFromVec2`, `COORDINATE:SmokeGreen/SmokeOrange`,
  `SPAWNSTATIC:NewFromType/InitCoordinate/InitCargo/InitCargoMass/Spawn`, `SPAWN:New/Spawn`,
  `GROUP:FindByName/Activate`, `CONTROLLABLE:RouteGroundTo`, `UNIT:FindByName/IsAlive/InAir`,
  `POSITIONABLE:GetVelocityKMH/GetCoordinate`, `MESSAGE:New/ToAll`, `TIMER:New/Start`.
- Der komplette Ablauf ist in einer simulierten DCS-Umgebung getestet (Lua 5.1, Stubs).
  Getestet wurden alle Phasen, Laden 2/4 → 4/4, Abwurf-Auswertung, Bergungstrupp und F10-Menü.

---

## 10. Bekannte Grenzen – bitte im Simulator prüfen

1. **CNI-MU-Bedienung (Kneeboards):** Es gibt keine offizielle Online-Doku der ASC-CNI-MU.
   Die Schritte stammen aus Community-Quellen (ED-Forum, DCS-BIOS/DCSAutoMate-Auslesungen) und sind
   auf den Karten mit **⚠ im Sim prüfen** markiert. Sicher sind die Tastennamen
   (INDX, LEGS, EXEC, DIR INTC, TOLD, NAV TUNE, MSN, LSK L1–L6/R1–R6). Sicher sind auch die Seitennamen
   `ACT LEGS` und `CARP INIT 1/5–5/5` mit den Feldern LOAD/CHUTE/ELEM WT/QTY/DROP PAYLD sowie PI ELEV/DZ ELEV.
   Diese stammen direkt aus dem Modul. Das offizielle Handbuch liegt unter
   `DCS World\Mods\aircraft\C130J\docs`.
2. **SID:** Ob die CNI-Datenbank SIDs für Nellis enthält, ist nicht bestätigt. Rückfallebene: Kneeboard 5.
3. **Laden:** Die Bündel werden wie bei MOOSE-CTLD als `cds_crate`-Statics erzeugt.
   Wie nah die Herc für das ASC-Ladesystem stehen muss, ist nicht dokumentiert.
4. **Abwurf-Erkennung:** Sie setzt voraus, dass abgeworfene Bündel als Static-/Cargo-Objekt am Boden liegen.
   Kommt keine Auswertung: F10 → „Abwurf jetzt auswerten“.
5. **Flugzeug in der `.miz`:** Die Mission ist mit pydcs erzeugt, das die ASC C-130J nicht kennt.
   Die Einheit wurde deshalb mit dem Typnamen `C-130J-30` (aus MOOSE) eingetragen.
   Zeigt der Mission Editor einen Fehler, `HERC 1` im ME löschen und neu setzen:
   C-130J, Parkposition G28 Nellis, „Takeoff from Parking Hot“, Skill „Player“, Unit-Name exakt `HERC 1-1`.
6. **Bekannte Modul-Fehler (Forum):** CARP-Nummer 1 an der Fracht kann den Computer-Abwurf verhindern.
   Die JUMP-Taste gibt sofort alle Fracht frei. Siehe Kneeboard 4.

## 11. Quellen

- MOOSE (lokal `libs/Moose.lua`): Typname `C-130J-30`, Frachtform `cds_crate`, Ladesystem-Hinweise (Ops.CTLD, Wrapper.DynamicCargo)
- [ED-Forum: Is CARP bugged?](https://forum.dcs.world/topic/382881-is-carp-bugged/) · [Set up an LZ in the CDU](https://forum.dcs.world/topic/382534-set-up-an-lz-in-the-cdu/) · [Lat and long points](https://forum.dcs.world/topic/382359-lat-and-long-points/) · [Navigation of M/E waypoints](https://forum.dcs.world/topic/384083-c-130j-navigation-of-me-waypoints/) · [C130J ILS Approach](https://forum.dcs.world/topic/388603-c130j-ils-approach/) · [Fail to perform multiple CARP airdrops](https://forum.dcs.world/topic/388219-fail-to-perform-multiple-carp-airdrops-with-c-130j-during-the-same-flight)
- [DCSAutoMate (CARP-Automatisierung C-130J)](https://github.com/Arcanum115/DCSAutoMate) · [DCS-BIOS-Fork mit C-130J-CNI-Auslesung](https://github.com/Arcanum115/dcs-bios)
- Gelände: USGS Elevation Point Query Service · Missweisung: WMM 2025
- Nellis-Frequenzen: pydcs-Terraindaten (TWR) und DCS-Community-Flugplatzdaten (ILS/TACAN)

---

## 12. Generator (`.miz` und Kneeboards neu erzeugen)

| Datei | Inhalt |
|---|---|
| `generator/geo.py` | Koordinaten, Wegpunkte, LZ/DZ-Daten, Missweisung, Hilfsfunktionen |
| `generator/brief.py` | Briefing-Texte |
| `generator/kneeboards.py` | Zeichnet die 8 Kneeboard-PNGs nach `kneeboards/` |
| `generator/gen_mission.py` | Baut `C130J_Desert_Lift.miz` (pydcs), bettet `libs/Moose.lua`, das Skript und die Kneeboards ein |
| `generator/test/` | Simulierter Durchlauf des Skripts (Lua 5.1 via lupa, DCS/MOOSE als Stubs) |

Schritt für Schritt (vom Repo-Wurzelordner aus):

1. `python -m venv .venv` und aktivieren
2. `pip install -r missions/C130J_Desert_Lift/generator/requirements.txt`
3. Daten ändern (meist `geo.py` oder `brief.py`)
4. `python missions/C130J_Desert_Lift/generator/kneeboards.py` (zuerst, die `.miz` bettet die PNGs ein)
5. `python missions/C130J_Desert_Lift/generator/gen_mission.py`
6. `python missions/C130J_Desert_Lift/generator/test/run_test.py` → muss mit `ALLE TESTS BESTANDEN` enden

Hinweise:
- pydcs gibt ohne DCS-Installation (z. B. unter Linux) viele Warnungen „Couldn't detect any installed DCS World version“ aus. Die sind harmlos.
- Schriften: DejaVu Sans / Sans Mono. Werden sie nicht gefunden, die TTF-Dateien nach `generator/fonts/` legen.
- Die Erzeugung ist reproduzierbar: Zwei Läufe ergeben dieselbe `.miz` (Inhalt).
