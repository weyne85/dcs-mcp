"""Erzeugt die Kneeboard-Seiten (PNG 1200x1600) fuer C-130J Desert Lift."""
import sys, os, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from geo import *

OUT = Path(__file__).resolve().parent.parent / "kneeboards"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1200, 1600
M = 48  # Rand

# DejaVu-Schriften suchen (Linux-Systempfad, Windows-Fontordner oder neben diesem Skript)
_FONT_DIRS = ["/usr/share/fonts/truetype/dejavu/", os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts/"),
              os.path.join(os.path.dirname(__file__), "fonts/")]
FD = next((d for d in _FONT_DIRS if os.path.exists(d + "DejaVuSans.ttf")), None)
if FD is None:
    sys.exit("DejaVu-Schriften nicht gefunden: DejaVuSans*.ttf und DejaVuSansMono*.ttf nach generator/fonts/ legen.")
F = {
    "title": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 46),
    "sub": ImageFont.truetype(FD + "DejaVuSans.ttf", 24),
    "h": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 30),
    "b": ImageFont.truetype(FD + "DejaVuSans.ttf", 26),
    "bb": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 26),
    "s": ImageFont.truetype(FD + "DejaVuSans.ttf", 22),
    "sb": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 22),
    "mono": ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", 25),
    "monos": ImageFont.truetype(FD + "DejaVuSansMono.ttf", 22),
    "num": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 28),
}
C = {
    "bg": (250, 250, 246), "ink": (25, 30, 38), "navy": (28, 52, 92), "muted": (95, 100, 110),
    "line": (200, 203, 208), "warn": (196, 110, 0), "warnbg": (255, 243, 222), "ok": (30, 120, 60),
    "box": (236, 240, 246), "key": (55, 60, 70), "green": (40, 150, 70), "orange": (230, 120, 20),
    "red": (190, 40, 40), "sand": (232, 222, 196), "blue": (40, 90, 170),
}
WARN = "⚠ im Sim prüfen"


class Page:
    def __init__(self, nr, title, sub):
        self.img = Image.new("RGB", (W, H), C["bg"])
        self.d = ImageDraw.Draw(self.img)
        self.y = 0
        self.nr = nr
        d = self.d
        d.rectangle([0, 0, W, 112], fill=C["navy"])
        d.text((M, 18), title, font=F["title"], fill="white")
        d.text((M, 74), sub, font=F["sub"], fill=(200, 212, 230))
        tag = f"{nr}/7"
        tw = d.textlength(tag, font=F["h"])
        d.text((W - M - tw, 38), tag, font=F["h"], fill="white")
        self.y = 136

    # -- Hilfen -------------------------------------------------------
    def wrap(self, text, font, width):
        lines = []
        for para in text.split("\n"):
            words, cur = para.split(" "), ""
            for w_ in words:
                t = (cur + " " + w_).strip()
                if self.d.textlength(t, font=font) <= width:
                    cur = t
                else:
                    if cur:
                        lines.append(cur)
                    cur = w_
            lines.append(cur)
        return lines

    def need(self, h):
        if self.y + h > H - 70:
            raise RuntimeError(f"Seite {self.nr}: Inhalt passt nicht (y={self.y}, +{h})")

    def h(self, text):
        self.need(50)
        self.y += 8
        self.d.text((M, self.y), text, font=F["h"], fill=C["navy"])
        self.y += 40
        self.d.line([M, self.y, W - M, self.y], fill=C["navy"], width=2)
        self.y += 12

    def p(self, text, font="b", color="ink", indent=0, gap=6):
        f = F[font]
        lh = f.size + 8
        lines = self.wrap(text, f, W - 2 * M - indent)
        self.need(lh * len(lines))
        for ln in lines:
            self.d.text((M + indent, self.y), ln, font=f, fill=C[color])
            self.y += lh
        self.y += gap

    def step(self, n, text, warn=False, keys=None):
        """Nummerierter Schritt. keys: Cockpit-Tasten (werden fett/monospace hervorgehoben)."""
        f = F["b"]
        lh = f.size + 8
        indent = 62
        bw = int(self.d.textlength(WARN, font=F["s"])) + 24
        tw = W - 2 * M - indent - (bw + 14 if warn else 0)
        lines = self.wrap(text, f, tw)
        hgt = max(48, lh * len(lines)) + 10
        self.need(hgt)
        cy = self.y + 22
        self.d.ellipse([M, cy - 22, M + 44, cy + 22], fill=C["navy"])
        nt = str(n)
        self.d.text((M + 22 - self.d.textlength(nt, font=F["num"]) / 2, cy - 17), nt, font=F["num"], fill="white")
        yy = self.y + 4
        for ln in lines:
            self._rich(M + indent, yy, ln, f)
            yy += lh
        if warn:
            bx = W - M - bw
            self.d.rounded_rectangle([bx, self.y + 4, W - M, self.y + 38], 8, fill=C["warnbg"], outline=C["warn"])
            self.d.text((bx + 10, self.y + 9), WARN, font=F["s"], fill=C["warn"])
        self.y += hgt

    def _rich(self, x, y, line, f):
        """Text in [eckigen Klammern] wird als Taste/Seite fett dargestellt."""
        parts = []
        buf, key = "", False
        for ch in line:
            if ch == "[" and not key:
                parts.append((buf, False)); buf = ""; key = True
            elif ch == "]" and key:
                parts.append((buf, True)); buf = ""; key = False
            else:
                buf += ch
        parts.append((buf, key))
        for t, k in parts:
            if not t:
                continue
            if k:
                fw = F["bb"]
                tw = self.d.textlength(t, font=fw)
                self.d.rounded_rectangle([x - 3, y - 1, x + tw + 3, y + f.size + 5], 5, fill=(222, 228, 238))
                self.d.text((x, y), t, font=fw, fill=C["key"])
                x += tw + 8
            else:
                self.d.text((x, y), t, font=f, fill=C["ink"])
                x += self.d.textlength(t, font=f)

    def table(self, headers, rows, widths, font="s", hfont="sb", mono_cols=()):
        f, hf = F[font], F[hfont]
        lh = f.size + 14
        self.need(lh * (len(rows) + 1) + 10)
        x0 = M
        self.d.rectangle([M, self.y, W - M, self.y + lh], fill=C["navy"])
        x = x0
        for htxt, wd in zip(headers, widths):
            self.d.text((x + 8, self.y + 6), htxt, font=hf, fill="white")
            x += wd
        self.y += lh
        for i, r in enumerate(rows):
            if i % 2 == 0:
                self.d.rectangle([M, self.y, W - M, self.y + lh], fill=C["box"])
            x = x0
            for j, (cell, wd) in enumerate(zip(r, widths)):
                ff = F["monos"] if j in mono_cols else f
                self.d.text((x + 8, self.y + 6), str(cell), font=ff, fill=C["ink"])
                x += wd
            self.y += lh
        self.y += 12

    def kv(self, items, kw=330, font="b", vfont="mono"):
        f, vf = F[font], F[vfont]
        lh = f.size + 12
        self.need(lh * len(items) + 24)
        top = self.y
        self.y += 10
        for k, v in items:
            self.d.text((M + 18, self.y), k, font=f, fill=C["muted"])
            for i, ln in enumerate(self.wrap(v, vf, W - 2 * M - kw - 30)):
                if i:
                    self.y += lh
                self.d.text((M + kw, self.y), ln, font=vf, fill=C["ink"])
            self.y += lh
        self.d.rounded_rectangle([M, top, W - M, self.y + 6], 10, outline=C["navy"], width=2)
        self.y += 20

    def note(self, text, warn=False):
        f = F["s"]
        lh = f.size + 8
        lines = self.wrap(text, f, W - 2 * M - 40)
        hgt = lh * len(lines) + 24
        self.need(hgt)
        self.d.rounded_rectangle([M, self.y, W - M, self.y + hgt], 10,
                                 fill=C["warnbg"] if warn else C["box"], outline=C["warn"] if warn else C["line"])
        yy = self.y + 12
        for ln in lines:
            self.d.text((M + 20, yy), ln, font=f, fill=C["ink"])
            yy += lh
        self.y += hgt + 14

    def canvas(self, hgt):
        self.need(hgt)
        box = (M, self.y, W - M, self.y + hgt)
        self.d.rounded_rectangle(box, 10, fill=(244, 240, 228), outline=C["line"], width=2)
        self.y += hgt + 14
        return box

    def save(self, name):
        foot = "C-130J DESERT LIFT  ·  Nevada  ·  ⚠ = Schritt aus Community-Quellen, im Simulator prüfen"
        self.d.line([M, H - 58, W - M, H - 58], fill=C["line"], width=1)
        self.d.text((M, H - 46), foot, font=F["s"], fill=C["muted"])
        self.img.save(OUT / name, optimize=True)


WP = {w[0]: w for w in WPTS}


def cni(name):
    la, lo = ddm(WP[name][1], WP[name][2])
    return la + lo


def legs():
    rows, prev = [], ("NELLIS",) + NELLIS
    for i, w in enumerate(WPTS, start=1):
        d, b = inv(prev[1], prev[2], w[1], w[2])
        rows.append((w, i, d / NM, (b - MAGVAR) % 360))
        prev = w
    return rows


# =================================================================== Seite 0: Uebersicht
def page0():
    pg = Page(0, "MISSION DESERT LIFT", "Übersicht · C-130J-30 · Singleplayer · Nevada")
    pg.h("Ablauf")
    for n, t in enumerate([
        "Hot-Start Parkposition [G28] Nellis AFB. SID ab RWY 21L/R, dann ALPHA – BRAVO – CHARLIE.",
        "Sturmlandung LZ YUCCA (Yucca Lake), RWY 18. Grüner Rauch = Aufsetzpunkt.",
        "4 CDS-Bündel am Ladeplatz (Westseite, Südende) mit dem ASC-Ladesystem einladen. Achtung: Gegner nähern sich!",
        "Start, DELTA – IP – PI: CARP-Abwurf am DZ THREE LAKES, 600 ft AGL, 130 KIAS. Oranger Rauch = PI.",
        "ECHO – FOXTROT – GOLF – HOTEL, ILS 21L oder Sichtanflug, Landung Nellis.",
    ], 1):
        pg.step(n, t)
    pg.h("Routenskizze (Norden oben)")
    x0, y0, x1, y1 = pg.canvas(560)
    pts = [("NELLIS",) + NELLIS] + [w[:3] for w in WPTS]
    lats = [p[1] for p in pts]; lons = [p[2] for p in pts]
    la0, la1, lo0, lo1 = min(lats) - 0.05, max(lats) + 0.05, min(lons) - 0.08, max(lons) + 0.08
    kx = math.cos(math.radians(36.6))
    sx = (x1 - x0 - 80) / ((lo1 - lo0) * kx); sy = (y1 - y0 - 60) / (la1 - la0); s = min(sx, sy)
    ox = x0 + 40 + ((x1 - x0 - 80) - (lo1 - lo0) * kx * s) / 2
    oy = y0 + 30

    def xy(la, lo):
        return ox + (lo - lo0) * kx * s, oy + (la1 - la) * s
    d = pg.d
    path = [xy(p[1], p[2]) for p in pts] + [xy(*NELLIS)]
    for a, b in zip(path, path[1:]):
        d.line([a, b], fill=C["navy"], width=4)
    for p in pts:
        x, y = xy(p[1], p[2]); name = p[0]
        col = {"LZ": C["green"], "PI": C["orange"], "NELLIS": C["blue"]}.get(name, C["navy"])
        r = 13 if name in ("LZ", "PI", "NELLIS") else 8
        d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline="white", width=2)
        label = {"LZ": "LZ YUCCA", "PI": "DZ / PI", "NELLIS": "NELLIS"}.get(name, name)
        off = {"CHARLIE": (16, -14), "LZ": (-150, 10), "DELTA": (16, -26), "IP": (18, -16), "PI": (18, -8),
               "ECHO": (16, -6), "FOXTROT": (-142, -8), "GOLF": (-90, 14), "HOTEL": (14, -30),
               "NELLIS": (-40, 18), "ALPHA": (22, -34), "BRAVO": (-112, -2)}[name]
        d.text((x + off[0], y + off[1]), label, font=F["sb"], fill=col)
    d.text((x0 + 20, y1 - 40), "Transit 8.500 ft MSL · Gesamt ca. 169 NM", font=F["s"], fill=C["muted"])
    pg.h("Frequenzen & Wetter")
    pg.kv([("Nellis TWR", "132.55 / 327.0"), ("TACAN / ILS 21L", "12X LSV / 109.10 IDIQ"),
           ("Wetter", "CAVOK, Wind 200/5, 18°C, QNH 29.92"), ("Missweisung", "11° Ost (MAG = TRUE − 11°)")],
          kw=330, font="b", vfont="mono")
    pg.save("00_Uebersicht.png")


# =================================================================== Seite 1: Wegpunkte
def page1():
    pg = Page(1, "1 · WEGPUNKTE EINGEBEN", "Koordinaten in die CNI-MU tippen")
    pg.h("Eingabeformat")
    pg.note("Grad + Dezimalminuten, ohne Leerzeichen und Gradzeichen:\n"
            "N3630.00W11526.40  =  N 36°30.00'  W 115°26.40'", warn=False)
    pg.h("Wegpunkt-Tabelle")
    rows = []
    for w, i, dnm, crs in legs():
        rows.append((f"LL{i:02d}", w[0], cni(w[0]), f"{w[3]:,}".replace(",", "."), f"{crs:03.0f}°/{dnm:4.1f}"))
    pg.table(["CNI", "Name", "Eingabe (Scratchpad)", "Höhe ft", "MAG/NM"], rows,
             [100, 170, 450, 160, 220], mono_cols=(2,))
    pg.h("So geht's (Pilot-CNI-MU)")
    pg.step(1, "Scratchpad leeren: [CLR] drücken (ggf. mehrmals), bis die unterste Zeile leer ist.", warn=True)
    pg.step(2, "Koordinate aus der Tabelle eintippen, z. B. N3630.00W11526.40 (Buchstaben N und W, Punkt-Taste).", warn=True)
    pg.step(3, "Eingabe vergleichen. Falsches Zeichen: [CLR] löscht das letzte Zeichen.", warn=True)
    pg.step(4, "Punkt per Zeilentaste (LSK) in die Route setzen: siehe Karte 2. Die CNI benennt die Punkte LL01, LL02 … in Eingabereihenfolge.")
    pg.note("Alternative: In der digitalen Karte (DIG MAP) Cursor auf den Punkt setzen und Koordinate ins Scratchpad senden.  ⚠ im Sim prüfen", warn=True)
    pg.save("01_Wegpunkte.png")


# =================================================================== Seite 2: Route
def page2():
    pg = Page(2, "2 · ROUTE ERSTELLEN", "Wegpunkte zur aktiven Route verbinden (LEGS)")
    pg.h("CNI-MU Tasten (Zeilentasten links L1–L6, rechts R1–R6)")
    x0, y0, x1, y1 = pg.canvas(290)
    d = pg.d
    sx0, sx1 = x0 + 220, x1 - 220
    d.rounded_rectangle([sx0, y0 + 20, sx1, y1 - 20], 8, fill=(18, 28, 22), outline=C["key"], width=3)
    d.text((sx0 + 120, y0 + 30), "ACT LEGS  1/2", font=F["monos"], fill=(120, 230, 140))
    for i in range(6):
        yy = y0 + 62 + i * 26
        d.rectangle([sx0 - 52, yy, sx0 - 14, yy + 18], fill=C["key"])
        d.text((sx0 - 112, yy - 3), f"L{i+1}", font=F["sb"], fill=C["ink"])
        d.rectangle([sx1 + 14, yy, sx1 + 52, yy + 18], fill=C["key"])
        d.text((sx1 + 62, yy - 3), f"R{i+1}", font=F["sb"], fill=C["ink"])
    for i, t in enumerate(["168°  5.9NM", "*LL07", "141°  8.3NM", "*LL08"]):
        d.text((sx0 + 20, y0 + 62 + i * 26), t, font=F["monos"], fill=(120, 230, 140))
    d.text((sx0 + 20, y0 + 226), "[ N3643.32W11537.80   ]", font=F["monos"], fill=(230, 230, 230))
    d.text((x0 + 12, y0 + 226), "Scratchpad →", font=F["s"], fill=C["muted"])
    pg.h("Route aufbauen")
    pg.step(1, "[INDX] drücken → INDEX-Seite. Mit [R1] die ROUTE-1-Seite öffnen.", warn=True)
    pg.step(2, "ORIGIN und DEST: KLSV ins Scratchpad, Zeilentaste neben dem Feld drücken.", warn=True)
    pg.step(3, "[L6] → LEGS-Seite (oder Taste [LEGS]).", warn=True)
    pg.step(4, "Koordinate ALPHA ins Scratchpad (Karte 1) → Zeilentaste links neben der ersten freien (gestrichelten) Zeile → erscheint als LL01.", warn=True)
    pg.step(5, "Für BRAVO … HOTEL wiederholen, immer in die nächste freie Zeile. Weitere Seiten mit [NEXT PAGE].")
    pg.step(6, "Punkt einfügen: Koordinate ins Scratchpad → Zeilentaste neben dem Punkt, VOR den er soll.", warn=True)
    pg.step(7, "Punkt löschen: [DEL] → Zeilentaste neben dem Punkt.", warn=True)
    pg.step(8, "[EXEC] drücken. Kopfzeile zeigt jetzt ACT LEGS = Route aktiv.")
    pg.step(9, "Falls nicht aktiv: ROUTE-Seite → [R5] ACTIVATE → [EXEC].", warn=True)
    pg.h("Wichtig")
    pg.note("• Kein VNAV: Der Autopilot folgt der Route nur seitlich. Höhen (Karte 1) selbst fliegen.\n"
            "• Die Herc fliegt den nächsten Punkt nicht automatisch direkt an: DIR INTC → Punkt per "
            "Zeilentaste wählen → EXEC. Oder den Kurs auf die Linie fliegen.")
    pg.save("02_Route.png")


# =================================================================== Seite 3: LZ
def page3():
    pg = Page(3, "3 · IMPROVISIERTE LZ", "LZ YUCCA · Yucca Lake · Sturmlandung")
    la_n, lo_n = ddm(*LZ_N); la_s, lo_s = ddm(*LZ_S)
    pg.kv([("Ident", "YUCCA"), ("Oberfläche", "Trockener Seeboden, eben, fest"),
           ("Elevation", f"{LZ_ELEV} ft"), ("Richtung", "18 / 36 = 180°/360° MAG (191°/011° TRUE)"),
           ("Länge × Breite", "3.500 × 90 ft (1.067 × 27 m)"),
           ("Schwelle 18 (N)", la_n + lo_n), ("Schwelle 36 (S)", la_s + lo_s),
           ("Landung", "RWY 18 (Wind 200/5), Aufsetzen erste 500 ft"),
           ("Anflug", "CHARLIE 5.500 ft, 4 NM, ca. 3,7°")], kw=300, font="s", vfont="monos")
    pg.h("Einprogrammieren")
    pg.step(1, "Eigenen Punkt: [INDX] → [NEXT PAGE] → CUSTOM DATA → Ident YUCCA + Koordinate Schwelle 18 eintragen.", warn=True)
    pg.step(2, "LZ-Daten: [LEGS] → Zeilentaste neben LL04 → MFP → LZ INIT: Ident YUCCA, Richtung 180, Länge 3500, Breite 90, Elevation 3921 → [EXEC].", warn=True)
    pg.step(3, "Landedaten: [TOLD] → LANDING: Platz YUCCA (nur Ident, ohne / und Bahn), 18 °C, Gewicht → Vref und Landestrecke ablesen.", warn=True)
    pg.step(4, "HUD-Symbol LZ prüfen. Erscheint es nicht, visuell landen: Rauch + Fahrzeuge markieren die Bahn.", warn=True)
    pg.h("Lageskizze LZ (Norden oben)")
    x0, y0, x1, y1 = pg.canvas(390)
    d = pg.d
    cx = (x0 + x1) // 2
    d.rectangle([cx - 22, y0 + 40, cx + 22, y1 - 40], fill=C["sand"], outline=C["muted"], width=2)
    d.text((cx - 20, y0 + 10), "18", font=F["bb"], fill=C["ink"])
    d.text((cx - 20, y1 - 36), "36", font=F["bb"], fill=C["ink"])
    d.ellipse([cx - 10, y0 + 56, cx + 10, y0 + 76], fill=C["green"])
    d.text((cx + 34, y0 + 52), "grüner Rauch = Aufsetzpunkt", font=F["s"], fill=C["green"])
    d.text((cx + 34, y0 + 8), "↓ Landerichtung 180° MAG", font=F["s"], fill=C["navy"])
    by = y1 - 120
    for i in range(4):
        bx = cx - 150 + (i % 2) * 22; byy = by + (i // 2) * 22
        d.rectangle([bx, byy, bx + 16, byy + 16], fill=(120, 90, 50))
    d.text((x0 + 16, by - 30), "Ladeplatz: 4 CDS", font=F["sb"], fill=(120, 90, 50))
    d.text((x0 + 16, by - 2), "+ Truppe, HEMTT", font=F["s"], fill=C["ink"])
    d.text((x0 + 16, by + 24), "70 m W, 120 m vor 36", font=F["s"], fill=C["muted"])
    for yy in (y0 + 170, y1 - 100):
        d.rectangle([cx + 120, yy, cx + 150, yy + 16], fill=C["blue"])
    d.text((cx + 160, y0 + 162), "Sicherung (HMMWV)", font=F["s"], fill=C["blue"])
    d.line([x1 - 40, y0 + 200, cx + 210, y0 + 200], fill=C["red"], width=3)
    d.polygon([(cx + 210, y0 + 192), (cx + 192, y0 + 200), (cx + 210, y0 + 208)], fill=C["red"])
    d.text((x1 - 330, y0 + 210), "Gegner aus Osten (8 km)", font=F["sb"], fill=C["red"])
    d.line([x1 - 40, y1 - 50, cx + 60, y1 - 82], fill=C["blue"], width=3)
    d.polygon([(cx + 60, y1 - 82), (cx + 78, y1 - 88), (cx + 76, y1 - 74)], fill=C["blue"])
    d.text((x1 - 300, y1 - 40), "Konvoi aus Südosten", font=F["s"], fill=C["blue"])
    pg.save("03_LZ.png")


# =================================================================== Seite 4: CARP
def page4():
    pg = Page(4, "4 · CARP / LUFTABWURF", "DZ THREE LAKES · CDS · Computer-Abwurf")
    pg.kv([("PI", cni("PI")), ("IP", cni("IP")), ("Run-in", "168° MAG (179° TRUE), 5,9 NM"),
           ("Abwurfhöhe", "600 ft AGL = 3.610 ft MSL"), ("Geschwindigkeit", "130 KIAS"),
           ("Last", "CDS, 4 Bündel à 900 kg (1.984 lb)"),
           ("PI / DZ / OBSTR ELEV", "3010 / 3020 / 3030 ft"), ("Danach", "Steigflug 6.500 ft → ECHO")],
          kw=320, font="s", vfont="monos")
    pg.h("Einprogrammieren")
    pg.step(1, "[LEGS] → Zeilentaste neben LL07 (PI) → MFP → CARP INIT. Nicht über die [MSN]-Taste (funktioniert laut Community nicht).", warn=True)
    pg.step(2, "CARP INIT 1/5: Abwurfpunkt PI, Run-in-Kurs 168, Höhe 600 AGL, Geschwindigkeit 130.", warn=True)
    pg.step(3, "CARP INIT 2/5: LOAD = CDS · CHUTE/# = G-12D/1 · ELEM WT/QTY = 1984LB/4 → DROP PAYLD prüfen (7936 LB).", warn=True)
    pg.step(4, "CARP INIT 3/5: DZ-Geometrie (LE-TE, LE-PI, SD DIST, TP DIST, DZ ESC) – Vorgabewerte übernehmen.", warn=True)
    pg.step(5, "CARP INIT 4/5: PI ELEV 3010 · DZ ELEV 3020 · OBSTR ELEV 3030. Regel: DZ ≥ PI, OBSTR ≥ DZ. Abgelehnt? OBSTR um 100 erhöhen.", warn=True)
    pg.step(6, "[EXEC]. In der Route erscheinen die CARP-Punkte (TP, SD, DZ ESC).", warn=True)
    pg.step(7, "Beim Laden KEINE CARP-Nummer an den Bündeln setzen (bekannter Fehler mit CARP 1).", warn=True)
    pg.step(8, "Schalter COMPUTER DROP auf AUTO. Taste JUMP NICHT drücken – gibt sofort alle Fracht frei!", warn=True)
    pg.h("Anflug & Abwurf")
    pg.step("A", "Ab DELTA im Tal sinken. Am IP: 3.610 ft MSL, 130 KIAS, Klappen 50 %, Kurs 168.", warn=True)
    pg.step("B", "Ca. 2 min vor PI: Rampe und Tür öffnen (Loadmaster/EFB). Kurs und Höhe exakt halten.", warn=True)
    pg.step("C", "Freigabe automatisch am CARP. Danach Rampe zu, steigen auf 6.500 ft, Kurs ECHO (141°).")
    pg.save("04_CARP.png")


# =================================================================== Seite 5: Abflug
def page5():
    pg = Page(5, "5 · ABFLUG NELLIS", "SID aus der Datenbank · Startdaten (TOLD)")
    pg.kv([("Platz", "Nellis AFB (KLSV), Elevation 1.870 ft"), ("Parkposition", "G28"),
           ("Startbahn", "21L oder 21R (Wind 200/5)"), ("Tower", "132.55 / 327.0"),
           ("TACAN", "12X (LSV)"), ("QNH / Temp", "29.92 inHg / 18 °C")], kw=300, font="s", vfont="monos")
    pg.h("Startdaten")
    pg.step(1, "[TOLD] → TAKEOFF: Bahn 21L, 18 °C, QNH 29.92, Gewicht (EFB) eintragen → Geschwindigkeiten ablesen.", warn=True)
    pg.h("SID programmieren")
    pg.step(2, "[INDX] → [R1] ROUTE 1 → ORIGIN = KLSV (falls noch leer).", warn=True)
    pg.step(3, "Abflugseite (DEPARTURE / DEP) öffnen → Bahn 21L wählen → SID wählen → passenden Übergang (Transition) wählen.", warn=True)
    pg.step(4, "[LEGS] prüfen: Ende der SID mit ALPHA verbinden. Lücke (DISCONTINUITY) schließen: ALPHA (LL01) per Zeilentaste ins Scratchpad holen und auf die Lücke setzen.", warn=True)
    pg.step(5, "[EXEC] → Route aktiv (ACT LEGS).")
    pg.h("Start")
    pg.step(6, "Rollfreigabe beim Tower holen, nach Anweisung zur 21L rollen. Start.")
    pg.step(7, "Nach dem Start: [DIR INTC] → erster SID-Punkt (bzw. ALPHA) → [EXEC].", warn=True)
    pg.h("Ohne SID in der Datenbank (Rückfallebene)")
    pg.note("Start 21L → Bahnkurs bis 3.500 ft MSL → Rechtskurve direkt ALPHA (298° MAG, 25 NM) → "
            "Steigflug auf 8.500 ft. Achtung: Gass Peak (6.943 ft) liegt ca. 3 NM nordöstlich der Linie.", warn=False)
    pg.save("05_Abflug.png")


# =================================================================== Seite 6: Landung
def page6():
    pg = Page(6, "6 · LANDUNG NELLIS", "ILS 21L (Standard) · Sichtanflug (Alternative)")
    pg.kv([("ILS 21L", "109.10 · Kennung IDIQ"), ("Anflugkurs", "207° MAG, Gleitweg 3°"),
           ("HOTEL", cni("HOTEL") + " · 5.500 ft"), ("Elevation", "1.870 ft"),
           ("Tower / TACAN", "132.55 / 327.0 · 12X")], kw=280, font="s", vfont="monos")
    pg.h("A  ILS-Anflug")
    pg.step(1, "Option 1: [INDX] → [R1] ROUTE → DEST KLSV → ARRIVAL → Anflug ILS 21L → [EXEC]. Bei Fehlern/Lücken: Option 2.", warn=True)
    pg.step(2, "Option 2: Route bis HOTEL (12 NM vor der Bahn) fliegen. Ab HOTEL Kurs 207° auf den Landekurs.")
    pg.step(3, "[NAV TUNE] → ILS-Frequenz 109.10 und Kurs 207 eintragen. Kennung IDIQ abhören.", warn=True)
    pg.step(4, "Keine ILS-Nadeln? Navigationsquelle (CDI) auf VOR1 bzw. ILS umschalten.", warn=True)
    pg.step(5, "APPR-Modus wählen, Landekurs einfangen, Gleitweg von unten bei 5.500 ft erfassen.", warn=True)
    pg.step(6, "Entscheidungshöhe ca. 2.070 ft MSL (200 ft über Platz) – bei CAVOK nur Richtwert.")
    pg.h("B  Sichtanflug (straight-in 21L)")
    pg.step(1, "Ab GOLF: Nellis in Sicht. Weiter nach HOTEL, dort auf Kurs 207° eindrehen.")
    pg.step(2, "3°-Gleitweg = ca. 320 ft pro NM. Richtwerte:")
    pg.table(["Entfernung zur Bahn", "Höhe MSL", "über Platz"],
             [("10 NM", "5.050 ft", "3.180 ft"), ("5 NM", "3.460 ft", "1.590 ft"),
              ("3 NM", "2.820 ft", "950 ft"), ("1 NM", "2.190 ft", "320 ft")], [460, 300, 344])
    pg.step(3, "Fahrwerk und Klappen nach Checkliste. Freigabe vom Tower (132.55) holen.")
    pg.save("06_Landung.png")


# =================================================================== Seite 7: Fracht
def page7():
    pg = Page(7, "7 · FRACHT LADEN (LZ)", "ASC-Ladesystem · 4 CDS-Bündel")
    pg.h("Am Ladeplatz")
    pg.step(1, "Nach der Landung (RWY 18) zum Südende rollen. Ladeplatz: Westseite, 120 m vor dem Südende, Bodentruppe + 4 Bündel.")
    pg.step(2, "Heck zu den Bündeln drehen, Abstand ca. 15–25 m. Parkbremse setzen.", warn=True)
    pg.step(3, "Rampe und Tür öffnen (Loadmaster/EFB).", warn=True)
    pg.step(4, "EFB → Cargo-/Loadmaster-Seite: Bündel in der Nähe auswählen und laden. Sie erscheinen im Laderaum-Schema.", warn=True)
    pg.step(5, "Keine CARP-Nummer setzen (siehe Karte 4). Erstes Abwurfbündel nach hinten an die Rampe.", warn=True)
    pg.step(6, "Warten auf die Meldung „4 von 4 CDS-Bündeln an Bord“ (Skript).")
    pg.step(7, "Rampe schließen, Ladung prüfen (Gewicht/Schwerpunkt im EFB).", warn=True)
    pg.h("Start von der LZ")
    pg.step(8, "Zum Nordende zurückrollen und auf RWY 18 starten (Gegenwind). Unter Zeitdruck ist auch RWY 36 möglich (ca. 5 kt Rückenwind).")
    pg.step(9, "Nach dem Start: [DIR INTC] → DELTA (LL05) → [EXEC]. Steigflug auf 8.500 ft.", warn=True)
    pg.h("Lage")
    pg.note("Sobald du auf der LZ stehst, meldet die Aufklärung zwei Technicals 8 km östlich. "
            "Ankunft in ca. 15 min. Die eigene Sicherung (2 HMMWV) hält sie auf – trotzdem zügig laden!", warn=True)
    pg.h("F10-Menü „DESERT LIFT“")
    pg.p("Missionsdaten · Status · Rauch LZ/DZ erneuern · Abwurf jetzt auswerten", font="s")
    pg.save("07_Fracht_laden.png")


for fn in (page0, page1, page2, page3, page4, page5, page6, page7):
    fn()
print("ok", sorted(p.name for p in OUT.glob("*.png")))
