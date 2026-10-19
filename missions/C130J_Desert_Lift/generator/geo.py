import math
R=6371008.8
MAGVAR=11.0  # deg East (WMM2025, 2026)
def dest(lat,lon,brg,dist_m):
    p1=math.radians(lat); l1=math.radians(lon); b=math.radians(brg); d=dist_m/R
    p2=math.asin(math.sin(p1)*math.cos(d)+math.cos(p1)*math.sin(d)*math.cos(b))
    l2=l1+math.atan2(math.sin(b)*math.sin(d)*math.cos(p1),math.cos(d)-math.sin(p1)*math.sin(p2))
    return math.degrees(p2), math.degrees(l2)
def inv(lat1,lon1,lat2,lon2):
    p1,p2=math.radians(lat1),math.radians(lat2); dl=math.radians(lon2-lon1)
    a=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    d=2*R*math.asin(math.sqrt(a))
    y=math.sin(dl)*math.cos(p2); x=math.cos(p1)*math.sin(p2)-math.sin(p1)*math.cos(p2)*math.cos(dl)
    return d,(math.degrees(math.atan2(y,x))+360)%360
def ddm(lat,lon):
    def f(v,pos,neg,w):
        h=pos if v>=0 else neg; v=abs(v); d=int(v); m=(v-d)*60
        if round(m,2)>=60: d+=1; m=0
        return f"{h}{d:0{w}d}{m:05.2f}"
    return f(lat,'N','S',2), f(lon,'E','W',3)
NM=1852.0
LZ_C=(36.9520,-116.0260); LZ_TRUE=11.0; LZ_LEN_FT=3500; LZ_WID_FT=90; LZ_ELEV=3921
LZ_N=dest(*LZ_C,LZ_TRUE,LZ_LEN_FT*0.3048/2)    # threshold RWY 18 (north end)
LZ_S=dest(*LZ_C,LZ_TRUE+180,LZ_LEN_FT*0.3048/2) # threshold RWY 36 (south end)
DZ_PI=(36.7220,-115.6300); DZ_ELEV=3010
NELLIS=(36.2352,-115.0330); NELLIS_ELEV=1870
HOTEL=dest(*NELLIS,38.0,12*NM)
WPTS=[  # name, lat, lon, planned alt ft MSL, remark
 ("ALPHA", 36.5000,-115.4400, 8500, "Ausflug NW (US-95-Korridor)"),
 ("BRAVO", 36.7400,-115.9800, 8500, "Mercury-Tal"),
 ("CHARLIE",)+dest(*LZ_N,LZ_TRUE,4*NM)+(5500, "Anflugpunkt LZ, 4 NM N, Endanflug RWY 18"),
 ("LZ",)+LZ_N+(LZ_ELEV, "LZ YUCCA, Schwelle/Aufsetzpunkt RWY 18"),
 ("DELTA", 36.9300,-115.6300, 8500, "Nordende Three Lakes Valley"),
 ("IP",   36.8200,-115.6320, 3610, "Initial Point, Beginn Run-in"),
 ("PI",)+DZ_PI+(3610, "DZ THREE LAKES, Point of Impact"),
 ("ECHO", 36.6000,-115.5500, 6500, "DZ-Escape"),
 ("FOXTROT", 36.4000,-115.3600, 6500, "US-95-Korridor"),
 ("GOLF", 36.3000,-115.1500, 5500, "suedlich Gass Peak"),
 ("HOTEL",)+HOTEL+(5500, "ILS-Einflugpunkt 21L, 12 NM"),
]
