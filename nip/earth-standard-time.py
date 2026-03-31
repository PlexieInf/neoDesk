
"""
EARTH STANDARD TIME  v2.3
Green phosphor terminal.  World clock + Islamic prayer times.
"""

import sys, time, os, math, re
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, available_timezones

_IS_WIN = sys.platform == "win32"
if _IS_WIN:
    import msvcrt
else:
    import tty, termios, select

# -----------------------------------------------------------------------------
#  ANSI  -  green phosphor only.  no cyan, no amber, no colour variety.
#  real VT100 terminals had one phosphor colour.  we honour that.
# -----------------------------------------------------------------------------
G0   = "\033[32m"     # dim green   (phosphor at rest)
G1   = "\033[92m"     # bright green (phosphor excited)
DIM  = "\033[2m"
BOLD = "\033[1m"
REV  = "\033[7m"      # reverse video  (the only "highlight" old terminals had)
RESET= "\033[0m"
BLINK= "\033[5m"

def g(s):  return G1   + s + RESET
def d(s):  return G0 + DIM + s + RESET
def b(s):  return BOLD + s + RESET
def hi(s): return REV  + s + RESET   # reverse-video: the classic selection indicator

# -----------------------------------------------------------------------------
#  LOCATION MAP
# -----------------------------------------------------------------------------
LOCATION_MAP = {
    "pakistan":"Asia/Karachi","malaysia":"Asia/Kuala_Lumpur","germany":"Europe/Berlin",
    "uae":"Asia/Dubai","united arab emirates":"Asia/Dubai","india":"Asia/Kolkata",
    "usa":"America/New_York","united states":"America/New_York","uk":"Europe/London",
    "united kingdom":"Europe/London","japan":"Asia/Tokyo","france":"Europe/Paris",
    "australia":"Australia/Sydney","china":"Asia/Shanghai","canada":"America/Toronto",
    "brazil":"America/Sao_Paulo","russia":"Europe/Moscow","south africa":"Africa/Johannesburg",
    "nigeria":"Africa/Lagos","egypt":"Africa/Cairo","turkey":"Europe/Istanbul",
    "saudi arabia":"Asia/Riyadh","singapore":"Asia/Singapore","new zealand":"Pacific/Auckland",
    "mexico":"America/Mexico_City","argentina":"America/Argentina/Buenos_Aires",
    "london":"Europe/London","new york":"America/New_York","nyc":"America/New_York",
    "los angeles":"America/Los_Angeles","la":"America/Los_Angeles","chicago":"America/Chicago",
    "toronto":"America/Toronto","paris":"Europe/Paris","berlin":"Europe/Berlin",
    "dubai":"Asia/Dubai","mumbai":"Asia/Kolkata","delhi":"Asia/Kolkata",
    "karachi":"Asia/Karachi","tokyo":"Asia/Tokyo","beijing":"Asia/Shanghai",
    "shanghai":"Asia/Shanghai","hong kong":"Asia/Hong_Kong","sydney":"Australia/Sydney",
    "melbourne":"Australia/Melbourne","auckland":"Pacific/Auckland","moscow":"Europe/Moscow",
    "istanbul":"Europe/Istanbul","cairo":"Africa/Cairo","lagos":"Africa/Lagos",
    "johannesburg":"Africa/Johannesburg","nairobi":"Africa/Nairobi","riyadh":"Asia/Riyadh",
    "kuala lumpur":"Asia/Kuala_Lumpur","kl":"Asia/Kuala_Lumpur","jakarta":"Asia/Jakarta",
    "seoul":"Asia/Seoul","bangkok":"Asia/Bangkok","tehran":"Asia/Tehran",
    "sao paulo":"America/Sao_Paulo","buenos aires":"America/Argentina/Buenos_Aires",
    "mexico city":"America/Mexico_City","amsterdam":"Europe/Amsterdam",
    "rome":"Europe/Rome","madrid":"Europe/Madrid","lisbon":"Europe/Lisbon",
    "utc":"UTC","islamabad":"Asia/Karachi","lahore":"Asia/Karachi",
    "dhaka":"Asia/Dhaka","colombo":"Asia/Colombo","zurich":"Europe/Zurich",
    "vienna":"Europe/Vienna","warsaw":"Europe/Warsaw","prague":"Europe/Prague",
}

TZ_COORDS = {
    "Asia/Karachi":(24.86,67.01),"Asia/Kolkata":(28.61,77.21),"Asia/Dubai":(25.20,55.27),
    "Asia/Riyadh":(24.69,46.72),"Asia/Tehran":(35.69,51.39),"Asia/Dhaka":(23.72,90.41),
    "Asia/Kuala_Lumpur":(3.14,101.69),"Asia/Jakarta":(-6.21,106.85),"Asia/Tokyo":(35.69,139.69),
    "Asia/Shanghai":(31.23,121.47),"Asia/Hong_Kong":(22.32,114.17),"Asia/Seoul":(37.57,126.98),
    "Asia/Bangkok":(13.75,100.52),"Asia/Singapore":(1.35,103.82),"Asia/Colombo":(6.93,79.85),
    "Europe/London":(51.51,-0.13),"Europe/Paris":(48.86,2.35),"Europe/Berlin":(52.52,13.41),
    "Europe/Istanbul":(41.01,28.95),"Europe/Moscow":(55.75,37.62),"Europe/Amsterdam":(52.37,4.90),
    "Europe/Rome":(41.90,12.50),"Europe/Madrid":(40.42,-3.70),"Europe/Lisbon":(38.72,-9.14),
    "Europe/Vienna":(48.21,16.37),"Europe/Zurich":(47.38,8.54),"Europe/Warsaw":(52.23,21.01),
    "Europe/Prague":(50.09,14.42),"America/New_York":(40.71,-74.01),
    "America/Los_Angeles":(34.05,-118.24),"America/Chicago":(41.88,-87.63),
    "America/Toronto":(43.65,-79.38),"America/Sao_Paulo":(-23.55,-46.63),
    "America/Mexico_City":(19.43,-99.13),"America/Argentina/Buenos_Aires":(-34.60,-58.38),
    "Africa/Cairo":(30.04,31.24),"Africa/Lagos":(6.45,3.40),
    "Africa/Johannesburg":(-26.20,28.04),"Africa/Nairobi":(-1.29,36.82),
    "Australia/Sydney":(-33.87,151.21),"Australia/Melbourne":(-37.81,144.96),
    "Pacific/Auckland":(-36.87,174.77),"UTC":(21.39,39.86),
}

def get_coords(tz_name):
    if tz_name in TZ_COORDS: return TZ_COORDS[tz_name]
    for k,v in TZ_COORDS.items():
        if k.split("/")[0] == tz_name.split("/")[0]: return v
    return (21.39,39.86)

# -----------------------------------------------------------------------------
#  SOLAR / PRAYER CALCULATIONS  (offline, Muslim World League method)
# -----------------------------------------------------------------------------
def _r(d): return d*math.pi/180
def _d(r): return r*180/math.pi

def _sun(jd):
    n   = jd - 2451545.0
    L   = (280.460 + 0.9856474*n) % 360
    g   = _r((357.528 + 0.9856003*n) % 360)
    lam = _r(L + 1.915*math.sin(g) + 0.020*math.sin(2*g))
    eps = _r(23.439 - 0.0000004*n)
    dec = _d(math.asin(math.sin(eps)*math.sin(lam)))
    RA  = _d(math.atan2(math.cos(eps)*math.sin(lam), math.cos(lam))) / 15
    EoT = (L/15 - (RA % 24)) * 60
    return dec, EoT

def _jd(y, m, d):
    if m <= 2: y -= 1; m += 12
    A = int(y/100); B = 2-A+int(A/4)
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def _hour_angle(target_alt_deg, lat_deg, dec_deg):
    lr, dr, ar = _r(lat_deg), _r(dec_deg), _r(target_alt_deg)
    cos_h = (math.sin(ar) - math.sin(lr)*math.sin(dr)) / (math.cos(lr)*math.cos(dr))
    if cos_h >  1: return None
    if cos_h < -1: return 0.0
    return _d(math.acos(cos_h)) / 15

def _asr_offset(lat_deg, dec_deg, shadow=1):
    lr, dr = _r(lat_deg), _r(dec_deg)
    target_alt = _d(math.atan(1.0 / (shadow + math.tan(abs(lr - dr)))))
    return _hour_angle(target_alt, lat_deg, dec_deg)

def calc_prayer_times(tz_name, date_obj=None):
    lat, lon = get_coords(tz_name)
    tz       = ZoneInfo(tz_name)
    if date_obj is None:
        date_obj = datetime.now(tz).date()
    jd       = _jd(date_obj.year, date_obj.month, date_obj.day)
    dec, eot = _sun(jd)
    utc_off  = datetime(date_obj.year, date_obj.month, date_obj.day,
                        12, tzinfo=tz).utcoffset().total_seconds() / 3600
    noon     = 12 - eot/60 - lon/15 + utc_off

    def to_dt(h):
        if h is None: return None
        tm = int(round(h * 60)); hh, mm = divmod(tm % 1440, 60)
        return datetime(date_obj.year, date_obj.month, date_obj.day, hh, mm, tzinfo=tz)

    sr_off  = _hour_angle(-0.833, lat, dec)
    asr_off = _asr_offset(lat, dec, shadow=1)
    return {
        "FAJR":    to_dt(noon - (_hour_angle(-18,    lat, dec) or 1.5)),
        "SUNRISE": to_dt(noon - (sr_off              or 1.0)),
        "DHUHR":   to_dt(noon + 0.033),
        "ASR":     to_dt(noon + (asr_off             or 3.5)),
        "MAGHRIB": to_dt(noon + (sr_off              or 1.0)),
        "ISHA":    to_dt(noon + (_hour_angle(-17,    lat, dec) or 1.5)),
    }

# -----------------------------------------------------------------------------
#  HIJRI CALENDAR  (Kuwaiti algorithm)
# -----------------------------------------------------------------------------
HIJRI_MONTHS = [
    "MUHARRAM","SAFAR","RABI-UL-AWWAL","RABI-UL-THANI",
    "JUMAD-UL-ULA","JUMAD-UL-AKHIRA","RAJAB","SHA'BAN",
    "RAMADAN","SHAWWAL","ZUL-QA'DAH","ZUL-HIJJAH"
]

def to_hijri(year, month, day):
    jd = int(_jd(year, month, day) + 0.5)
    l  = jd - 1948440 + 10632
    n  = int((l-1)/10631)
    l  = l - 10631*n + 354
    j  = (int((10985-l)/5316))*(int((50*l)/17719)) + (int(l/5670))*(int((43*l)/15238))
    l  = l - (int((30-j)/15))*(int((17719*j)/50)) - (int(j/16))*(int((15238*j)/43)) + 29
    m  = int((24*l)/709)
    d  = l - int((709*m)/24)
    y  = 30*n + j - 30
    return y, m, d

def lunar_phase(dt):
    ref   = datetime(2000,1,6,18,14,tzinfo=timezone.utc)
    cycle = 29.53058867
    days  = (dt.astimezone(timezone.utc) - ref).total_seconds() / 86400 % cycle
    pct   = (1 - math.cos(2*math.pi*days/cycle)) / 2 * 100
    names = [(1.85,"NEW MOON"),(7.38,"WAXING CRESCENT"),(9.22,"FIRST QUARTER"),
             (14.76,"WAXING GIBBOUS"),(16.61,"FULL MOON"),(22.15,"WANING GIBBOUS"),
             (23.99,"LAST QUARTER"),(29.53,"WANING CRESCENT")]
    phase = next((n for t,n in names if days < t), "NEW MOON")
    return phase, pct, days

# -----------------------------------------------------------------------------
#  APP STATE
# -----------------------------------------------------------------------------
tabs           = []
active_tab     = 0
input_buffer   = ""
mode           = "main"      # main | add | switch | close | search_results | prayer
search_results = []
message        = ""
message_expiry = 0.0
prayer_cache   = {}

def get_prayers(tz_name):
    tz    = ZoneInfo(tz_name)
    today = datetime.now(tz).date()
    if tz_name in prayer_cache:
        cd, data = prayer_cache[tz_name]
        if cd == today: return data
    data = calc_prayer_times(tz_name, today)
    prayer_cache[tz_name] = (today, data)
    return data

# -----------------------------------------------------------------------------
#  TERMINAL HELPERS
# -----------------------------------------------------------------------------
def clear(): print("\033[2J\033[H", end="")

def cols():
    try:    return os.get_terminal_size().columns
    except: return 80

def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*m','',s)

def utc_off_str(tz):
    m = int(datetime.now(tz).utcoffset().total_seconds()/60)
    s = "+" if m>=0 else "-"; m=abs(m); h,mn=divmod(m,60)
    return f"UTC{s}{h:02d}:{mn:02d}"

def diff_str(tz1, tz2):
    delta = int((datetime.now(tz2).utcoffset()-datetime.now(tz1).utcoffset()).total_seconds())
    if delta==0: return "SAME"
    s="+"
    if delta<0: s="-"; delta=-delta
    h,r=divmod(delta,3600); mn=r//60
    return f"{s}{h}H{mn:02d}M" if mn else f"{s}{h}H"

# -----------------------------------------------------------------------------
#  BOX DRAWING  -  plain ASCII only.  + - | =
# -----------------------------------------------------------------------------
def topbar(w):  return G0 + "+" + "="*(w-2) + "+" + RESET
def botbar(w):  return G0 + "+" + "="*(w-2) + "+" + RESET
def midbar(w):  return G0 + "+" + "-"*(w-2) + "+" + RESET

def row(content, w):
    inner = w - 4
    vis   = len(strip_ansi(content))
    pad   = max(0, inner - vis)
    return G0 + "|" + RESET + " " + content + " "*pad + " " + G0 + "|" + RESET

# -----------------------------------------------------------------------------
#  COMMAND BAR  -  lives inside the box, always visible, never disappears
# -----------------------------------------------------------------------------
def _cmdbar(w, cmds):
    parts = "  ".join(g(k) + d(v) for k,v in cmds)
    print(midbar(w))
    print(row("  " + parts, w))
    print(midbar(w))

    if message and time.time() < message_expiry:
        hint = g(message)
    else:
        _hints = {
            "main":           d("type command letter and press ENTER"),
            "add":            d("city / country / IANA zone name  --  blank line cancels"),
            "search_results": d("enter number to pick  --  B cancels"),
            "switch":         d("enter tab number  --  any other input cancels"),
            "close":          d("enter tab number  --  any other input cancels"),
            "prayer":         d("B goes back  --  Q quits"),
        }
        hint = _hints.get(mode, d(""))

    print(row("  " + hint, w))
    print(botbar(w))
    print(G1 + "  >> " + RESET + G1 + input_buffer + BLINK + "_" + RESET,
          end="", flush=True)

# -----------------------------------------------------------------------------
#  RENDERING
# -----------------------------------------------------------------------------
def render():
    w = cols()
    clear()
    _header(w)
    if   mode == "add":            _add_screen(w)
    elif mode == "search_results": _search_screen(w)
    elif mode == "prayer":         _prayer_screen(w)
    else:                          _main_screen(w)

def _header(w):
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d  %H:%M:%S  UTC")
    title   = ("EARTH STANDARD TIME  v2.3" + "  " + now_utc).center(w-4)
    print(topbar(w))
    print(row(g(b(title)), w))
    print(midbar(w))

def _main_screen(w):
    if not tabs:
        print(row("", w))
        print(row(d("  NO CLOCKS LOADED."), w))
        print(row(d("  TYPE  N  AND PRESS ENTER TO ADD ONE."), w))
        print(row("", w))
    else:
        ref = ZoneInfo(tabs[active_tab])
        for i, tz_name in enumerate(tabs):
            tz  = ZoneInfo(tz_name)
            now = datetime.now(tz)
            act = i == active_tab

            t24  = now.strftime("%H:%M:%S")
            t12  = now.strftime("%I:%M %p")
            date = now.strftime("%a %d-%b-%Y").upper()
            off  = utc_off_str(tz)
            dif  = ("" if act else "  " + diff_str(ref, tz) + f" FROM [{active_tab}]")

            if act:
                label = hi(g(b(f"  [{i}] {tz_name:<32}")))
                clock = g(b(f"      {t24}  {t12}"))
                meta  = d(f"      {date}  {off}")
            else:
                label = d(f"  [{i}] {tz_name}")
                clock = G0 + f"      {t24}" + RESET + d(f"  {t12}")
                meta  = d(f"      {date}  {off}{dif}")

            if i > 0: print(midbar(w))
            else:      print(row("", w))
            print(row(label, w))
            print(row(clock, w))
            print(row(meta,  w))

        print(row("", w))

    _cmdbar(w, [("N)","NEW"), ("S)","SWITCH"), ("C)","CLOSE"), ("P)","PRAYER"), ("Q)","QUIT")])

def _add_screen(w):
    print(row("", w))
    print(row(g(b("  ADD CLOCK")), w))
    print(row("", w))
    print(row(d("  ENTER A CITY, COUNTRY, OR IANA ZONE NAME."), w))
    print(row(d("  LEAVE BLANK AND PRESS ENTER TO CANCEL."), w))
    print(row("", w))
    print(row(d("  E.G.  DUBAI   JAPAN   AMERICA/CHICAGO   LONDON"), w))
    print(row("", w))
    _cmdbar(w, [("ENTER","CONFIRM"), ("(BLANK)","CANCEL")])

def _search_screen(w):
    print(row("", w))
    print(row(g(b("  MULTIPLE MATCHES")), w))
    print(row(d("  MORE THAN ONE ZONE MATCHED.  PICK A NUMBER."), w))
    print(row("", w))
    for i, tz in enumerate(search_results[:12]):
        print(row(d(f"  [{i}]  ") + g(tz), w))
    print(row("", w))
    _cmdbar(w, [("0-9","SELECT"), ("B)","CANCEL")])

def _prayer_screen(w):
    if not tabs:
        print(row(d("  NO TIMEZONE SELECTED."), w))
        _cmdbar(w, [("B)","BACK"), ("Q)","QUIT")])
        return

    tz_name = tabs[active_tab]
    tz      = ZoneInfo(tz_name)
    now     = datetime.now(tz)
    lat,lon = get_coords(tz_name)

    hy,hm,hd = to_hijri(now.year,now.month,now.day)
    hijri    = f"{hd} {HIJRI_MONTHS[hm-1]} {hy} AH"
    phase, pct, moon_day = lunar_phase(now)

    prayers = get_prayers(tz_name)
    ORDER   = ["FAJR","SUNRISE","DHUHR","ASR","MAGHRIB","ISHA"]

    next_name = next_dt = None
    for name in ORDER:
        dt = prayers.get(name)
        if dt and dt > now:
            next_name, next_dt = name, dt; break
    if next_name is None:
        tom   = now.date() + timedelta(days=1)
        tp    = calc_prayer_times(tz_name, tom)
        next_name = "FAJR (TOMORROW)"
        next_dt   = tp.get("FAJR")

    lat_s = f"{abs(lat):.2f}{'N' if lat>=0 else 'S'}"
    lon_s = f"{abs(lon):.2f}{'E' if lon>=0 else 'W'}"
    greg  = now.strftime("%a %d %b %Y").upper()

    print(row(g(b(f"  PRAYER TIMES  --  {tz_name.upper()}")), w))
    print(midbar(w))
    print(row(d(f"  {greg}  //  {hijri}"), w))
    print(row(d(f"  {lat_s} {lon_s}  //  METHOD: MWL SUN-ANGLE  (OFFLINE)"), w))
    print(midbar(w))

    # each salah window: FAJR->SUNRISE, DHUHR->ASR, ASR->MAGHRIB, MAGHRIB->ISHA, ISHA->tomorrow FAJR
    tom_prayers = calc_prayer_times(tz_name, now.date() + timedelta(days=1))
    WINDOW_END = {
        "FAJR":    prayers.get("SUNRISE"),
        "DHUHR":   prayers.get("ASR"),
        "ASR":     prayers.get("MAGHRIB"),
        "MAGHRIB": prayers.get("ISHA"),
        "ISHA":    tom_prayers.get("FAJR"),
    }

    for name in ORDER:
        dt      = prayers.get(name)
        t24     = dt.strftime("%H:%M") if dt else "--:--"
        t12     = dt.strftime("%I:%M %p") if dt else ""
        is_past = dt and dt < now
        is_next = (name == next_name)

        if name == "SUNRISE" or not is_past:
            win_tag = ""
        elif WINDOW_END.get(name) and now < WINDOW_END[name]:
            win_tag = g("  [AVAILABLE]")
        else:
            win_tag = d("  [WINDOW CLOSED]")

        if is_next:
            secs  = int((next_dt-now).total_seconds())
            m2,s2 = divmod(secs,60); h2,m2 = divmod(m2,60)
            cd    = f"  <-- NEXT  {h2:02d}H {m2:02d}M {s2:02d}S"
            line  = hi(g(b(f"  >>> {name:<10} {t24}  {t12}{cd}")))
        elif is_past:
            line  = d(f"       {name:<10} {t24}  {t12}") + win_tag
        else:
            line  = G0 + f"       {name:<10} {t24}" + RESET + d(f"  {t12}")

        print(row(line, w))

    print(midbar(w))
    filled = int(pct / 100 * 20)
    bar_   = G0 + "[" + RESET + G1 + "#"*filled + RESET + d("-"*(20-filled)) + G0 + "]" + RESET
    print(row(g(b("  LUNAR")), w))
    print(row(d("  HIJRI  : ") + g(hijri), w))
    print(row(d("  PHASE  : ") + g(f"{phase:<22}") + d(f"  {bar_}  {pct:.0f}%"), w))
    print(row(d(f"  CYCLE  : DAY {moon_day:.1f} OF 29.53"), w))
    print(row("", w))
    _cmdbar(w, [("B)","BACK"), ("Q)","QUIT")])

# -----------------------------------------------------------------------------
#  TIMEZONE SEARCH
# -----------------------------------------------------------------------------
def find_tz(q):
    q = q.lower().replace(" ","_")
    return sorted(tz for tz in available_timezones() if q in tz.lower())

def resolve(place):
    pl = place.lower().strip()
    if pl in LOCATION_MAP: return LOCATION_MAP[pl], []
    if place in available_timezones(): return place, []
    m = find_tz(pl)
    if len(m)==1: return m[0], []
    if len(m)>1:  return None, m
    return None, []

# -----------------------------------------------------------------------------
#  COMMANDS
# -----------------------------------------------------------------------------
def set_msg(msg, dur=3.0):
    global message, message_expiry
    message=msg; message_expiry=time.time()+dur

def cmd_main(cmd):
    global mode, input_buffer, active_tab
    if cmd=="q": return False
    if cmd=="n": mode="add"; input_buffer=""
    elif cmd=="s":
        if len(tabs)>1: set_msg(f"SWITCH TO TAB [0-{len(tabs)-1}]:"); mode="switch"; input_buffer=""
        else: set_msg("ONLY ONE TAB OPEN.")
    elif cmd=="c":
        if tabs: set_msg(f"CLOSE TAB [0-{len(tabs)-1}]:"); mode="close"; input_buffer=""
        else: set_msg("NO TABS.")
    elif cmd=="p":
        if tabs: mode="prayer"; input_buffer=""
        else: set_msg("ADD A TIMEZONE FIRST.")
    return True

def cmd_add(cmd):
    global mode, input_buffer, active_tab, search_results
    place=cmd.strip()
    if not place: mode="main"; input_buffer=""; return
    tz, cands = resolve(place)
    if tz:
        if tz not in tabs: tabs.append(tz)
        active_tab=tabs.index(tz); set_msg(f"ADDED: {tz}"); mode="main"
    elif cands:
        search_results=cands; mode="search_results"
    else:
        set_msg(f"NOT FOUND: {place!r}"); mode="main"
    input_buffer=""

def cmd_search(cmd):
    global mode, active_tab, search_results, input_buffer
    if cmd=="b": mode="main"; input_buffer=""; return
    if cmd.isdigit():
        i=int(cmd)
        if 0<=i<len(search_results):
            tz=search_results[i]
            if tz not in tabs: tabs.append(tz)
            active_tab=tabs.index(tz); set_msg(f"ADDED: {tz}")
            search_results=[]; mode="main"; input_buffer=""; return
    set_msg("INVALID."); input_buffer=""

def cmd_switch(cmd):
    global active_tab, mode, input_buffer
    if cmd.isdigit():
        i=int(cmd)
        if 0<=i<len(tabs): active_tab=i; set_msg(f"NOW ON [{i}] {tabs[i]}")
        else: set_msg("OUT OF RANGE.")
    else: set_msg("CANCELLED.")
    mode="main"; input_buffer=""

def cmd_close(cmd):
    global active_tab, mode, input_buffer
    if cmd.isdigit():
        i=int(cmd)
        if 0<=i<len(tabs):
            removed=tabs.pop(i); active_tab=min(active_tab,max(0,len(tabs)-1))
            set_msg(f"CLOSED: {removed}")
        else: set_msg("OUT OF RANGE.")
    else: set_msg("CANCELLED.")
    mode="main"; input_buffer=""

def dispatch(cmd):
    global mode, input_buffer
    if   mode=="main":           return cmd_main(cmd)
    elif mode=="add":            cmd_add(cmd)
    elif mode=="search_results": cmd_search(cmd)
    elif mode=="switch":         cmd_switch(cmd)
    elif mode=="close":          cmd_close(cmd)
    return True

# -----------------------------------------------------------------------------
#  KEY INPUT  (cross-platform)
# -----------------------------------------------------------------------------
def get_key():
    if _IS_WIN:
        if msvcrt.kbhit():
            ch=msvcrt.getch()
            if ch in (b'\x00',b'\xe0'): msvcrt.getch(); return None
            try:    return ch.decode("utf-8")
            except: return None
        time.sleep(0.05); return None
    else:
        rl,_,_=select.select([sys.stdin],[],[],0.05)
        if rl:
            ch=os.read(sys.stdin.fileno(),1)
            try:    return ch.decode("utf-8")
            except: return None
        return None

# -----------------------------------------------------------------------------
#  MAIN
# -----------------------------------------------------------------------------
def main():
    global input_buffer, mode

    for tz in ["UTC","America/New_York","Asia/Dubai"]:
        tabs.append(tz)

    clear()
    w=cols()
    print(topbar(w))
    print(row("", w))
    print(row(g(b("EARTH STANDARD TIME  v2.3".center(w-4))), w))
    print(row(d("INITIALIZING...".center(w-4)), w))
    print(row("", w))
    print(botbar(w))
    time.sleep(0.6)

    if not _IS_WIN:
        fd=sys.stdin.fileno(); old=termios.tcgetattr(fd); tty.setraw(fd)

    try:
        running=True
        while running:
            render()
            key=get_key()
            if key is None: continue
            if key in ("\r","\n"):
                cmd=input_buffer.strip().lower(); input_buffer=""
                if mode=="prayer":
                    if cmd=="b": mode="main"
                    elif cmd=="q": running=False
                else:
                    running=dispatch(cmd)
            elif key in ("\x7f","\x08"): input_buffer=input_buffer[:-1]
            elif key=="\x03":            running=False
            elif key.isprintable():      input_buffer+=key
    finally:
        if not _IS_WIN: termios.tcsetattr(fd,termios.TCSADRAIN,old)
        clear()
        print(g("  SESSION TERMINATED.\n"))

if __name__=="__main__":
    main()
