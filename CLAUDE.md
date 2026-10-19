# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Zweck des Repos

Arbeitsumgebung zum Schreiben von **DCS-World-Missionsskripten in Lua** auf Basis von MOOSE, MiST und CTLD.
Ergebnis pro Mission: genau eine `.lua` + eine `README.md` (Details und verbindliche Regeln in der importierten Referenz unten).

## Referenz (verbindlich)

@docs/README.md

## Struktur

- `libs/` – unveränderte Drittbibliotheken (nur lesen, nicht editieren), als Nachschlagequelle für echte Signaturen:
  - `Moose.lua` – MOOSE, Build-Commit vom 2026-02-06 (Zeile 1 von `Moose.lua`)
  - `mist.lua` – MiST 4.5.126 (`mist.majorVersion/minorVersion/build`)
  - `CTLD.lua` – CTLD 1.6.1 (`ctld.Version`), `CTLD-i18n.lua` – Übersetzungen (translation_version 1.6)
  - `A10_laste_Winds.lua` – eigenständiges Beispielskript (MOOSE-basiert, F10-Menü für A-10C LASTE-Wind/Temp-Daten); zeigt den im Repo üblichen Stil: Kopfkommentar mit Version und Mission-Editor-Setup, `env.info`-Log beim Laden, `pcall` um MOOSE-Aufrufe
- `libs/test`, `docs/test` – Platzhalterdateien ohne Inhalt

## Build / Lint / Test

- Kein Build-System, kein Linter, keine Tests im Repo. Lua ist in der Cloud-Umgebung nicht installiert.
- Skripte laufen nur in DCS (Mission Editor). Fehler werden über `dcs.log` ausgewertet.
- Funktionen lassen sich offline per `grep` in `libs/*.lua` verifizieren (große Dateien: `Moose.lua` ~292k Zeilen – nie komplett lesen, gezielt suchen).

## Wichtige Fakten, die über die Referenz hinausgehen

- **CTLD 1.6.1 braucht `CTLD-i18n.lua` vor `CTLD.lua`** (sonst Warnmeldung im Spiel). Ladereihenfolge damit: MiST → CTLD-i18n → CTLD → Missionsskript.
- `CTLD.lua` verlangt laut Kopfkommentar die **mit dem CTLD-Paket gelieferte MiST-Version** (wegen dynamischer Spawns).
- MOOSE-Skripte werden mit Verzögerung nach `Moose.lua` geladen (z. B. Trigger „TIME MORE (5)“), damit MOOSE initialisiert ist.
