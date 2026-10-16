"""
Slide Remote by Yellowtail
Control your slides from your phone: a desktop app that shows a QR code,
your phone becomes the clicker (next, back, blank, laser pointer, timer).

Run:        python SlideRemote.pyw
Build .exe: double-click build_windows.bat (creates a desktop shortcut)
"""
import base64
import http.server
import io
import json
import platform
import secrets
import socket
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from urllib.parse import urlparse, parse_qs

APP_NAME = "Slide Remote"
DEFAULT_PORT = 8765

# Yellowtail palette
YELLOW = "#F8C11D"
BLUE = "#204ED6"
NAVY = "#1B2C41"
GREY = "#EEEBE7"
MUTED = "#727272"
WHITE = "#FFFFFF"
LINE = "#DAD6D0"

LOGO_B64 = "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"


def fail(msg):
    import tkinter.messagebox as mb
    r = tk.Tk()
    r.withdraw()
    mb.showerror(APP_NAME, msg)
    sys.exit(1)


try:
    from PIL import Image, ImageDraw, ImageTk
    import qrcode
except ImportError as e:
    fail(f"Missing package: {e.name}\n\nOpen a terminal and run:\npip install pyautogui qrcode pillow")


def make_icon(size=256):
    """App icon: navy rounded square, yellow dot, white chevron."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size / 256
    d.rounded_rectangle([8 * s, 8 * s, 248 * s, 248 * s], radius=56 * s, fill=NAVY)
    d.ellipse([140 * s, 36 * s, 220 * s, 116 * s], fill=YELLOW)
    d.line([(100 * s, 76 * s), (160 * s, 136 * s), (100 * s, 196 * s)],
           fill=WHITE, width=int(30 * s), joint="curve")
    return im


# Icon-only mode for the build script (no GUI, no pyautogui needed)
if "--make-icon" in sys.argv:
    make_icon(256).save("icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    make_icon(1024).save("icon.icns")  # macOS app icon
    sys.exit(0)

try:
    import pyautogui
except ImportError:
    fail("Missing package: pyautogui\n\nOpen a terminal and run:\npip install pyautogui qrcode pillow")

pyautogui.FAILSAFE = False  # the laser may touch screen corners
pyautogui.PAUSE = 0

IS_MAC = platform.system() == "Darwin"
MOD = "command" if IS_MAC else "ctrl"

ACTIONS = {
    "next":   (lambda: pyautogui.press("right"), "Next slide"),
    "prev":   (lambda: pyautogui.press("left"), "Previous slide"),
    "blank":  (lambda: pyautogui.press("b"), "Blank screen"),
    "laser":  (lambda: pyautogui.hotkey(MOD, "l"), "Laser pointer"),
    "start":  ((lambda: pyautogui.hotkey("command", "shift", "enter")) if IS_MAC
               else (lambda: pyautogui.press("f5")), "Start from the beginning"),
    "resume": ((lambda: pyautogui.hotkey("command", "enter")) if IS_MAC
               else (lambda: pyautogui.hotkey("shift", "f5")), "Start from this slide"),
    "end":    (lambda: pyautogui.press("esc"), "End show"),
}


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        self.last_seen = 0.0
        self.device = ""
        self.slide = None
        self.last_action = None
        self.last_action_t = 0.0


STATE = State()


def device_name(ua):
    ua = ua or ""
    for key, name in (("iPhone", "iPhone"), ("iPad", "iPad"), ("Android", "Android phone")):
        if key in ua:
            return name
    return "Phone"


# ---------------------------------------------------------------- phone page
PAGE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1B2C41">
<title>Slide Remote</title>
<style>
:root{--yel:#F8C11D;--blue:#204ED6;--navy:#1B2C41;--navy2:#26405c;--grey:#EEEBE7;--muted:#727272;--red:#E5484D}
*{box-sizing:border-box;margin:0;-webkit-tap-highlight-color:transparent;-webkit-user-select:none;user-select:none}
html,body{height:100%;overflow:hidden;background:var(--navy);color:#fff;touch-action:manipulation;
  font:400 16px/1.25 Aptos,"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,sans-serif}
body{display:flex;flex-direction:column;gap:12px;
  padding:calc(env(safe-area-inset-top,0px) + 14px) 14px calc(env(safe-area-inset-bottom,0px) + 14px)}

.top{display:flex;align-items:center;justify-content:space-between;padding:0 2px}
.brand{display:flex;align-items:center;gap:10px;font-size:20px}
.brand b{font-weight:800}.brand i{font-weight:400}
.mark{width:32px;height:32px;border-radius:10px;background:#fff;display:grid;place-items:center;
  color:var(--yel);font-weight:900;font-size:20px}
.pill{border-radius:999px;padding:7px 13px;font-size:13px;font-weight:700;background:var(--yel);color:var(--navy)}
.pill.off{background:var(--red);color:#fff}

.info{background:#fff;color:var(--navy);border-radius:20px;padding:12px 18px;
  display:grid;grid-template-columns:1fr 1px 1fr;align-items:center;gap:14px}
.info .sep{height:38px;background:var(--grey)}
.info .k{font-size:13px;color:var(--muted)}
.info .v{font-size:30px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.1}
.info .right{text-align:right}
#timer.idle{color:#b9b4ad}
.chips{position:absolute;top:14px;left:14px;display:flex;gap:6px}
.chip{display:none;font-size:12px;font-weight:700;border-radius:999px;padding:6px 11px;background:var(--navy);color:#fff}
.chip.show{display:inline-block}

#pad{flex:1;min-height:0;background:var(--yel);color:var(--navy);border-radius:26px;position:relative;overflow:hidden;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;touch-action:none;transition:filter .1s}
#pad.hit{filter:brightness(.9)}
#pad .disc{width:104px;height:104px;border-radius:50%;background:var(--navy);display:grid;place-items:center}
#pad .disc svg{width:52px;height:52px;stroke:var(--yel)}
#pad .title{font-size:30px}#pad .title b{font-weight:800}#pad .title i{font-weight:400}
#pad .hint{font-size:14px;opacity:.75;text-align:center;padding:0 28px}
#pad.laser{background:var(--blue);color:#fff}
#pad.laser .disc{background:#fff}#pad.laser .disc svg{stroke:var(--blue)}

.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.tile{appearance:none;border:0;border-radius:18px;padding:12px 4px 11px;font:600 14px inherit;font-family:inherit;
  display:flex;flex-direction:column;align-items:center;gap:6px;transition:transform .08s}
.tile:active{transform:scale(.96)}
.tile.light{background:#fff;color:var(--navy)}
.tile.dark{background:var(--navy2);color:#fff}
.ic{position:relative;width:32px;height:30px;display:grid;place-items:center}
.ic::before{content:"";position:absolute;z-index:0;width:15px;height:15px;border-radius:50%;background:var(--yel);top:-3px;right:-4px}
.ic svg{position:relative;z-index:1;width:24px;height:24px}
.tile.on{background:var(--yel);color:var(--navy)}
.tile.on .ic::before{background:rgba(255,255,255,.4)}
#laserBtn.on{background:var(--blue);color:#fff}

#gone{position:fixed;inset:0;background:var(--navy);display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:32px;text-align:center}
#gone.show{display:flex}
#gone h2{font-size:26px}#gone h2 b{font-weight:800}#gone h2 i{font-weight:400}
#gone p{color:#c9d1dc;max-width:300px}
</style></head><body>

<div class="top">
  <div class="brand"><div class="mark">Y</div><span><b>Slide</b> <i>Remote</i></span></div>
  <div class="pill" id="pill">Connected</div>
</div>

<section class="info">
  <div id="timeBox"><div class="k">Time (tap to reset)</div><div class="v idle" id="timer">00:00</div></div>
  <div class="sep"></div>
  <div class="right"><div class="k">Slide</div><div class="v" id="count">1</div></div>
</section>

<section id="pad">
  <div class="chips"><span class="chip" id="chipBlank">Screen blanked</span><span class="chip" id="chipLaser">Laser on</span></div>
  <div class="disc"><svg id="padIcon" viewBox="0 0 24 24" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></div>
  <div class="title" id="padTitle"><b>Next</b> <i>slide</i></div>
  <div class="hint" id="padHint">Tap anywhere on yellow. Swipe right to go back.</div>
</section>

<div class="grid">
  <button class="tile light" id="prevBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></span>Back</button>
  <button class="tile light" id="blankBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="13" rx="2" fill="currentColor"/><path d="M9 21h6"/></svg></span>Blank</button>
  <button class="tile light" id="laserBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="3.2" fill="currentColor"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1"/></svg></span>Laser</button>
  <button class="tile dark" id="startBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M7 4.5l12 7.5-12 7.5z"/></svg></span>Start</button>
  <button class="tile dark" id="resumeBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 4.5v15" fill="none"/><path d="M9 4.5l11 7.5-11 7.5z"/></svg></span>From here</button>
  <button class="tile dark" id="endBtn"><span class="ic"><svg viewBox="0 0 24 24" fill="currentColor"><rect x="5.5" y="5.5" width="13" height="13" rx="2.5"/></svg></span>End</button>
</div>

<div id="gone"><h2><b>Scan</b> <i>again</i></h2><p>The code on your laptop has changed or the app was closed. Scan the QR code in Slide Remote to reconnect.</p></div>

<script>
const T = new URLSearchParams(location.search).get('t');
const $ = id => document.getElementById(id);
const pad = $('pad'), SENS = 2.4;
let laser = false, blank = false, slide = 1, t0 = null, tick = null;

function online(ok){ $('pill').classList.toggle('off', !ok); $('pill').textContent = ok ? 'Connected' : 'No connection'; }
async function send(body){
  try{
    const r = await fetch('/a',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(Object.assign({t:T, s:slide}, body))});
    if(r.status === 403){ $('gone').classList.add('show'); return false; }
    online(r.ok); return r.ok;
  }catch(e){ online(false); return false; }
}
setInterval(()=>send({ping:1}), 3000); send({ping:1});

const buzz = ms => { if(navigator.vibrate) navigator.vibrate(ms || 12); };
const flash = () => { pad.classList.add('hit'); setTimeout(()=>pad.classList.remove('hit'), 110); };
const showSlide = () => { $('count').textContent = slide; };

function startTimer(){
  if(t0) return; t0 = Date.now(); $('timer').classList.remove('idle');
  tick = setInterval(()=>{
    const s = Math.floor((Date.now()-t0)/1000);
    $('timer').textContent = String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0');
  }, 500);
}
$('timeBox').onclick = ()=>{ clearInterval(tick); t0 = null; $('timer').textContent = '00:00'; $('timer').classList.add('idle'); };

async function wake(){ try{ if(navigator.wakeLock) await navigator.wakeLock.request('screen'); }catch(e){} }
document.addEventListener('visibilitychange', ()=>{ if(!document.hidden) wake(); });

function next(){ buzz(); flash(); startTimer(); slide++; showSlide(); send({a:'next'}); }
function prev(){ buzz(); flash(); slide = Math.max(1, slide-1); showSlide(); send({a:'prev'}); }

// pad gestures: tap = next, swipe = next/back, laser mode = trackpad
let sx=0, sy=0, lx=0, ly=0, moved=false, acc={x:0,y:0}, busy=false, raf=0;
pad.addEventListener('touchstart', e=>{ wake(); const p=e.touches[0]; sx=lx=p.clientX; sy=ly=p.clientY; moved=false; }, {passive:true});
pad.addEventListener('touchmove', e=>{
  e.preventDefault(); const p=e.touches[0];
  if(laser){ acc.x += (p.clientX-lx)*SENS; acc.y += (p.clientY-ly)*SENS; if(!raf) raf = requestAnimationFrame(flush); }
  lx=p.clientX; ly=p.clientY;
  if(Math.abs(lx-sx) > 12 || Math.abs(ly-sy) > 12) moved = true;
}, {passive:false});
pad.addEventListener('touchend', e=>{
  e.preventDefault(); if(laser) return;
  const dx = lx - sx;
  if(!moved) next(); else if(Math.abs(dx) > 50) (dx < 0 ? next() : prev());
}, {passive:false});
pad.addEventListener('click', ()=>{ if(!laser && !('ontouchstart' in window)) next(); });

async function flush(){
  raf = 0;
  if(busy){ raf = requestAnimationFrame(flush); return; }
  const dx = Math.round(acc.x), dy = Math.round(acc.y);
  if(!dx && !dy) return;
  acc.x -= dx; acc.y -= dy; busy = true;
  await send({dx, dy}); busy = false;
  if(Math.round(acc.x) || Math.round(acc.y)) raf = requestAnimationFrame(flush);
}

function setLaser(on){
  laser = on;
  $('laserBtn').classList.toggle('on', on); pad.classList.toggle('laser', on); $('chipLaser').classList.toggle('show', on);
  $('padIcon').innerHTML = on ? '<circle cx="12" cy="12" r="4" fill="currentColor" stroke="none" style="fill:var(--blue)"/><circle cx="12" cy="12" r="9"/>' : '<path d="M9 5l7 7-7 7"/>';
  $('padTitle').innerHTML = on ? '<b>Laser</b> <i>pointer</i>' : '<b>Next</b> <i>slide</i>';
  $('padHint').textContent = on ? 'Drag your finger here to point. Tap Laser to go back to clicking.' : 'Tap anywhere on yellow. Swipe right to go back.';
}
function setBlank(on){ blank = on; $('blankBtn').classList.toggle('on', on); $('chipBlank').classList.toggle('show', on); }

$('prevBtn').onclick   = prev;
$('blankBtn').onclick  = ()=>{ buzz(); setBlank(!blank); send({a:'blank'}); };
$('laserBtn').onclick  = ()=>{ buzz(25); setLaser(!laser); send({a:'laser'}); };
$('startBtn').onclick  = ()=>{ buzz(); slide = 1; showSlide(); startTimer(); send({a:'start'}); };
$('resumeBtn').onclick = ()=>{ buzz(); startTimer(); send({a:'resume'}); };
$('endBtn').onclick    = ()=>{ buzz(30); if(laser){ setLaser(false); send({a:'laser'}); } setBlank(false); send({a:'end'}); };
</script></body></html>"""


# ---------------------------------------------------------------- server
class Handler(http.server.BaseHTTPRequestHandler):
    timeout = 5
    MAX_BODY_BYTES = 4096

    def log_message(self, *args):
        pass

    def _reply(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.close_connection = True
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _token_ok(self, t):
        with STATE.lock:
            tok = STATE.token
        return isinstance(t, str) and t.isascii() and secrets.compare_digest(t, tok)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/":
            return self._reply(404)
        if not self._token_ok(parse_qs(u.query).get("t", [""])[0]):
            return self._reply(403, b"This code has expired. Scan the QR code in Slide Remote again.")
        self._reply(200, PAGE.encode(), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/a":
            return self._reply(404)
        try:
            if self.headers.get("Transfer-Encoding"):
                return self._reply(400)
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0:
                return self._reply(400)
            if length > self.MAX_BODY_BYTES:
                return self._reply(413)
            body = self.rfile.read(length)
            if len(body) != length:
                return self._reply(400)
            data = json.loads(body)
        except (ValueError, OSError):
            return self._reply(400)
        if not isinstance(data, dict) or not self._token_ok(data.get("t")):
            return self._reply(403)

        with STATE.lock:
            STATE.last_seen = time.time()
            STATE.device = device_name(self.headers.get("User-Agent"))
            if isinstance(data.get("s"), int):
                STATE.slide = data["s"]

        if "a" in data:
            action = data["a"]
            entry = ACTIONS.get(action) if isinstance(action, str) else None
            if not entry:
                return self._reply(400)
            entry[0]()
            with STATE.lock:
                STATE.last_action, STATE.last_action_t = entry[1], time.time()
        elif "dx" in data:
            try:
                dx = max(-400, min(400, int(data["dx"])))
                dy = max(-400, min(400, int(data["dy"])))
            except (KeyError, TypeError, ValueError, OverflowError):
                return self._reply(400)
            pyautogui.moveRel(dx, dy)
        self._reply(204)


def start_server(port):
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    for p in range(port, port + 20):
        try:
            srv = http.server.ThreadingHTTPServer(("0.0.0.0", p), Handler)
        except OSError:
            continue
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return srv, p
    fail("Couldn't open a network port. Is another copy of Slide Remote already running?")


def lan_ips():
    ips = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # sends nothing; picks the LAN interface
        ips.append(s.getsockname()[0])
    except OSError:
        pass
    finally:
        s.close()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except OSError:
        pass
    return ips or ["127.0.0.1"]


# ---------------------------------------------------------------- desktop window
def round_rect(cv, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, splinesteps=24, **kw)


def pick_font(root, names):
    fams = set(tkfont.families(root))
    return next((n for n in names if n in fams), "TkDefaultFont")


class App:
    W, H = 880, 568

    def __init__(self, root, port):
        self.root = root
        self.server, self.port = start_server(port)
        self.ips = lan_ips()
        self.ip_i = 0
        self.k = max(1.0, root.winfo_fpixels("1i") / 96.0)
        self.fam = pick_font(root, ("Aptos", "Segoe UI Variable Text", "Segoe UI", "Helvetica Neue", "Helvetica", "Arial"))
        self.fam_d = pick_font(root, ("Aptos Display", "Aptos", "Segoe UI Variable Display", "Segoe UI", "Helvetica Neue", "Arial"))

        S = self.S
        root.title(APP_NAME)
        root.configure(bg=GREY)
        root.resizable(False, False)
        root.geometry(f"{S(self.W)}x{S(self.H)}")
        self._icon = ImageTk.PhotoImage(make_icon(64))
        root.iconphoto(True, self._icon)
        root.protocol("WM_DELETE_WINDOW", self.quit)

        self.cv = tk.Canvas(root, width=S(self.W), height=S(self.H), bg=GREY, highlightthickness=0)
        self.cv.pack()
        self.build()
        self.refresh_qr()
        self.tick()

    def S(self, v):
        return int(round(v * self.k))

    def F(self, size, weight="normal", slant="roman", display=False):
        return tkfont.Font(family=self.fam_d if display else self.fam, size=-self.S(size), weight=weight, slant=slant)

    def url(self):
        with STATE.lock:
            tok = STATE.token
        return f"http://{self.ips[self.ip_i]}:{self.port}/?t={tok}"

    # -- layout
    def build(self):
        cv, S = self.cv, self.S
        W = self.W

        # header
        cv.create_rectangle(0, 0, S(W), S(92), fill=NAVY, outline="")
        round_rect(cv, S(28), S(18), S(164), S(74), S(14), fill=WHITE, outline="")
        logo = Image.open(io.BytesIO(base64.b64decode(LOGO_B64)))
        logo.thumbnail((S(112), S(40)), Image.LANCZOS)
        self._logo = ImageTk.PhotoImage(logo)
        cv.create_image(S(96), S(46), image=self._logo)

        fb, fi = self.F(30, "bold", display=True), self.F(30, "normal", "italic", display=True)
        cv.create_text(S(188), S(46), text="Slide", font=fb, fill=WHITE, anchor="w")
        cv.create_text(S(188) + fb.measure("Slide "), S(46), text="Remote", font=fi, fill=WHITE, anchor="w")

        self.pill_bg = round_rect(cv, S(W - 232), S(30), S(W - 28), S(62), S(16), fill="#33475e", outline="")
        self.pill_tx = cv.create_text(S(W - 130), S(46), text="Waiting for phone", font=self.F(14, "bold"), fill=WHITE)

        # QR card, with the Yellowtail dot peeking out behind it
        cv.create_oval(S(318), S(92), S(384), S(158), fill=YELLOW, outline="")
        round_rect(cv, S(28), S(116), S(360), S(540), S(20), fill=WHITE, outline="")
        self.qr_item = cv.create_image(S(194), S(300))
        cv.create_text(S(194), S(468), text="Scan with your phone camera", font=self.F(17, "bold"), fill=NAVY)
        self.url_tx = cv.create_text(S(194), S(496), text="", font=self.F(12), fill=MUTED)
        cv.create_text(S(194), S(516), text="Phone and PC on the same Wi-Fi or hotspot", font=self.F(12), fill=MUTED)

        # status card
        x1, x2 = 392, W - 28
        round_rect(cv, S(x1), S(116), S(x2), S(252), S(20), fill=WHITE, outline="")
        cv.create_text(S(x1 + 24), S(142), text="Phone", font=self.F(13), fill=MUTED, anchor="w")
        self.dev_tx = cv.create_text(S(x1 + 24), S(170), text="Not connected yet", font=self.F(22, "bold"), fill=NAVY, anchor="w")
        cv.create_line(S(x1 + 24), S(196), S(x2 - 24), S(196), fill=GREY, width=S(2))
        cv.create_text(S(x1 + 24), S(214), text="Slide", font=self.F(12), fill=MUTED, anchor="w")
        self.slide_tx = cv.create_text(S(x1 + 24), S(234), text="–", font=self.F(16, "bold"), fill=NAVY, anchor="w")
        cv.create_text(S(x1 + 150), S(214), text="Last action", font=self.F(12), fill=MUTED, anchor="w")
        self.act_tx = cv.create_text(S(x1 + 150), S(234), text="–", font=self.F(16, "bold"), fill=NAVY, anchor="w")

        # steps card (a real sequence, so numbered)
        round_rect(cv, S(x1), S(268), S(x2), S(460), S(20), fill=WHITE, outline="")
        steps = [
            ("Scan the code", "Your phone opens the remote in its browser."),
            ("Start your slideshow", "Click into it once so it receives the clicks."),
            ("Tap Next on your phone", "Use Laser to point, Blank to black out."),
        ]
        for i, (title, sub) in enumerate(steps):
            y = 310 + i * 56
            cv.create_oval(S(x1 + 36), S(y - 20), S(x1 + 64), S(y + 8), fill=YELLOW, outline="")
            cv.create_text(S(x1 + 42), S(y + 3), text=str(i + 1), font=self.F(26, "bold", display=True), fill=BLUE)
            cv.create_text(S(x1 + 76), S(y - 9), text=title, font=self.F(15, "bold"), fill=NAVY, anchor="w")
            cv.create_text(S(x1 + 76), S(y + 11), text=sub, font=self.F(13), fill=MUTED, anchor="w")

        # buttons
        self.copy_btn = self.pill_button(x1, 480, 132, "Copy link", self.copy_link, primary=True)
        self.pill_button(x1 + 144, 480, 132, "New code", self.new_code)
        self.net_btn = self.pill_button(x1 + 288, 480, x2 - x1 - 288, "", self.next_ip)

    def pill_button(self, x, y, w, label, cmd, primary=False):
        cv, S = self.cv, self.S
        tag = f"btn{id(cmd)}"
        fill = YELLOW if primary else WHITE
        bg = round_rect(cv, S(x), S(y), S(x + w), S(y + 50), S(24), fill=fill,
                        outline="" if primary else LINE, width=S(1.5), tags=tag)
        tx = cv.create_text(S(x + w / 2), S(y + 25), text=label, font=self.F(15, "bold"), fill=NAVY, tags=tag)
        cv.tag_bind(tag, "<Button-1>", lambda e: cmd())
        cv.tag_bind(tag, "<Enter>", lambda e: cv.configure(cursor="hand2"))
        cv.tag_bind(tag, "<Leave>", lambda e: cv.configure(cursor=""))
        return tx

    # -- actions
    def refresh_qr(self):
        qr = qrcode.QRCode(border=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(self.url())
        img = qr.make_image(fill_color=NAVY, back_color=WHITE).convert("RGB")
        img = img.resize((self.S(270), self.S(270)), Image.NEAREST)
        self._qr = ImageTk.PhotoImage(img)
        self.cv.itemconfigure(self.qr_item, image=self._qr)
        short = self.url().replace("http://", "")
        self.cv.itemconfigure(self.url_tx, text=short)
        net = f"Wi-Fi {self.ips[self.ip_i]}" + ("  (switch)" if len(self.ips) > 1 else "")
        self.cv.itemconfigure(self.net_btn, text=net)

    def copy_link(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url())
        self.cv.itemconfigure(self.copy_btn, text="Copied")
        self.root.after(1400, lambda: self.cv.itemconfigure(self.copy_btn, text="Copy link"))

    def new_code(self):
        with STATE.lock:
            STATE.token = secrets.token_urlsafe(32)
            STATE.last_seen = 0
        self.refresh_qr()

    def next_ip(self):
        if len(self.ips) > 1:
            self.ip_i = (self.ip_i + 1) % len(self.ips)
            self.refresh_qr()

    def tick(self):
        with STATE.lock:
            seen, dev, slide = STATE.last_seen, STATE.device, STATE.slide
            act, act_t = STATE.last_action, STATE.last_action_t
        now = time.time()
        live = now - seen < 8
        cv = self.cv
        cv.itemconfigure(self.pill_bg, fill=YELLOW if live else "#33475e")
        cv.itemconfigure(self.pill_tx, text="Phone connected" if live else "Waiting for phone",
                         fill=NAVY if live else WHITE)
        if live:
            cv.itemconfigure(self.dev_tx, text=f"{dev} connected")
        elif seen:
            cv.itemconfigure(self.dev_tx, text="Connection lost")
        else:
            cv.itemconfigure(self.dev_tx, text="Not connected yet")
        cv.itemconfigure(self.slide_tx, text=str(slide) if slide else "–")
        if act:
            ago = int(now - act_t)
            when = "just now" if ago < 3 else (f"{ago} s ago" if ago < 60 else f"{ago // 60} min ago")
            cv.itemconfigure(self.act_tx, text=f"{act}, {when}")
        self.root.after(500, self.tick)

    def quit(self):
        threading.Thread(target=self.server.shutdown, daemon=True).start()
        self.root.destroy()


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    port = DEFAULT_PORT
    if "--port" in sys.argv:
        try:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        except (IndexError, ValueError):
            pass
    root = tk.Tk()
    App(root, port)
    root.mainloop()


if __name__ == "__main__":
    main()
