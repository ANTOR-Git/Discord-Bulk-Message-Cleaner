"""
Discord Bulk Message Deleter — Made by Antor
Modern UI Edition
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import time
import io
import math
from PIL import Image, ImageTk, ImageDraw

BASE = "https://discord.com/api/v9"
CDN  = "https://cdn.discordapp.com"

# Discord dark palette
BG       = "#1e1f22"
SIDEBAR  = "#1e1f22"
SURFACE  = "#2b2d31"
SURFACE2 = "#313338"
SURFACE3 = "#383a40"
ACCENT   = "#5865f2"
ACCENT_H = "#4752c4"
ACCENT_S = "#3c45a5"
RED      = "#ed4245"
RED_H    = "#c03537"
GREEN    = "#57f287"
TEXT     = "#dbdee1"
TEXT2    = "#b5bac1"
MUTED    = "#80848e"
WHITE    = "#ffffff"
WARN     = "#fee75c"
ONLINE   = "#23a55a"
YELLOW   = "#faa81a"

GUILD_COLORS = ["#5865f2","#57f287","#eb459e","#fee75c","#ed4245","#3ba55d","#faa81a","#00b0f4"]

def guild_color(name):
    return GUILD_COLORS[sum(ord(c) for c in name) % len(GUILD_COLORS)]


# ── API ───────────────────────────────────────────────────────────────────────

def hdr(token):
    return {"Authorization": token, "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_me(token):
    r = requests.get(f"{BASE}/users/@me", headers=hdr(token)); r.raise_for_status(); return r.json()

def get_guilds(token):
    r = requests.get(f"{BASE}/users/@me/guilds", headers=hdr(token)); r.raise_for_status(); return r.json()

def get_guild_channels(token, gid):
    r = requests.get(f"{BASE}/guilds/{gid}/channels", headers=hdr(token)); r.raise_for_status(); return r.json()

def get_dm_channels(token):
    r = requests.get(f"{BASE}/users/@me/channels", headers=hdr(token)); r.raise_for_status(); return r.json()

def fetch_image_bytes(url):
    try:
        r = requests.get(url, timeout=6); r.raise_for_status(); return r.content
    except: return None

def search_guild(token, gid, cid, uid, offset=0):
    params = {"author_id": uid, "include_nsfw": "true", "offset": offset}
    if cid: params["channel_id"] = cid
    r = requests.get(f"{BASE}/guilds/{gid}/messages/search", headers=hdr(token), params=params)
    if r.status_code == 429:
        ra = r.json().get("retry_after", 1); time.sleep(ra)
        return search_guild(token, gid, cid, uid, offset)
    r.raise_for_status(); return r.json()

def search_dm(token, cid, uid, offset=0):
    params = {"author_id": uid, "include_nsfw": "true", "offset": offset}
    r = requests.get(f"{BASE}/channels/{cid}/messages/search", headers=hdr(token), params=params)
    if r.status_code == 429:
        ra = r.json().get("retry_after", 1); time.sleep(ra)
        return search_dm(token, cid, uid, offset)
    r.raise_for_status(); return r.json()

def delete_msg(token, cid, mid):
    r = requests.delete(f"{BASE}/channels/{cid}/messages/{mid}", headers=hdr(token))
    if r.status_code == 429:
        ra = r.json().get("retry_after", 1); time.sleep(ra)
        return delete_msg(token, cid, mid)
    return r.status_code in (200, 204)


# ── Image helpers ─────────────────────────────────────────────────────────────

def make_circle(data, size=36):
    try:
        img = Image.open(io.BytesIO(data)).convert("RGBA").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)
    except: return None

def make_initials(letter, size=36, bg="#5865f2"):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    # draw circle with slight gradient feel via two ellipses
    d.ellipse((0, 0, size-1, size-1), fill=bg)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", int(size * 0.45))
    except:
        font = None
    txt = letter.upper()
    if font:
        bb = d.textbbox((0,0), txt, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
    else:
        tw = th = size // 3
    d.text(((size-tw)//2, (size-th)//2 - 1), txt, fill="white", font=font)
    return ImageTk.PhotoImage(img)


# ── Animated button ───────────────────────────────────────────────────────────

class AnimButton(tk.Frame):
    """Simple button with smooth hover color animation."""
    def __init__(self, parent, text, command=None,
                 bg_normal=ACCENT, bg_hover=ACCENT_H, bg_press=ACCENT_S,
                 fg=WHITE, font=("Segoe UI", 10, "bold"),
                 width=160, height=36, radius=8, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self._n       = bg_normal
        self._h       = bg_hover
        self._p       = bg_press
        self._cur_rgb = self._hex_rgb(bg_normal)
        self._tgt_rgb = self._hex_rgb(bg_normal)
        self._anim_id = None

        self.btn = tk.Button(self, text=text, command=command,
                              font=font, fg=fg,
                              bg=bg_normal,
                              activebackground=bg_hover,
                              activeforeground=fg,
                              relief="flat", bd=0, cursor="hand2",
                              padx=16, pady=8)
        self.btn.pack(fill="both", expand=True)

        for w in (self, self.btn):
            w.bind("<Enter>",          self._on_enter)
            w.bind("<Leave>",          self._on_leave)
            w.bind("<ButtonPress-1>",  self._on_press)
            w.bind("<ButtonRelease-1>",self._on_release)

    def _hex_rgb(self, h):
        h = h.lstrip("#")
        return [int(h[i:i+2], 16) for i in (0, 2, 4)]

    def _rgb_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def _anim_to(self, target_hex):
        self._tgt_rgb = self._hex_rgb(target_hex)
        if self._anim_id:
            try: self.after_cancel(self._anim_id)
            except: pass
        self._step()

    def _step(self):
        changed = False
        for i in range(3):
            diff = self._tgt_rgb[i] - self._cur_rgb[i]
            if abs(diff) > 1:
                self._cur_rgb[i] += diff * 0.3
                changed = True
            else:
                self._cur_rgb[i] = self._tgt_rgb[i]
        try:
            c = self._rgb_hex(self._cur_rgb)
            self.btn.config(bg=c)
        except: return
        if changed:
            self._anim_id = self.after(16, self._step)

    def _on_enter(self, e):  self._anim_to(self._h)
    def _on_leave(self, e):  self._anim_to(self._n)
    def _on_press(self, e):  self._anim_to(self._p)
    def _on_release(self, e):self._anim_to(self._h)

    def config_text(self, text):
        self.btn.config(text=text)


# ── Smooth progress bar ───────────────────────────────────────────────────────

class SmoothProgress(tk.Canvas):
    def __init__(self, parent, height=8, **kw):
        super().__init__(parent, height=height, bg=SURFACE2,
                         highlightthickness=0, **kw)
        self._pct     = 0.0
        self._target  = 0.0
        self._anim_id = None
        self.bind("<Configure>", lambda e: self._draw())

    def set_value(self, val, maximum):
        self._target = val / maximum if maximum > 0 else 0
        if self._anim_id: self.after_cancel(self._anim_id)
        self._tick()

    def reset(self):
        self._pct = 0.0; self._target = 0.0; self._draw()

    def _tick(self):
        diff = self._target - self._pct
        if abs(diff) > 0.002:
            self._pct += diff * 0.18
            self._draw()
            self._anim_id = self.after(16, self._tick)
        else:
            self._pct = self._target; self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width(); h = self.winfo_height()
        if w < 2: return
        r = h // 2
        # track
        self._round_rect(0, 0, w, h, r, SURFACE3)
        # fill
        fw = max(0, int(w * self._pct))
        if fw > 0:
            self._round_rect(0, 0, fw, h, r, ACCENT)
        # glow tip
        if fw > r * 2:
            self.create_oval(fw - r*2, 0, fw, h, fill="#7983f5", outline="")

    def _round_rect(self, x1, y1, x2, y2, r, color):
        if x2 - x1 < 2*r: r = (x2-x1)//2
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=color, outline=color)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=color, outline=color)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=color, outline=color)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(x1+r, y1, x2-r, y2, fill=color, outline=color)
        self.create_rectangle(x1, y1+r, x2, y2-r, fill=color, outline=color)


# ── Spinner (loading dots) ────────────────────────────────────────────────────

class Spinner(tk.Canvas):
    def __init__(self, parent, size=20, **kw):
        super().__init__(parent, width=size, height=size, bg=parent.cget("bg"),
                         highlightthickness=0, **kw)
        self._size    = size
        self._angle   = 0
        self._running = False
        self._job     = None

    def start(self):
        self._running = True; self._tick()
    def stop(self):
        self._running = False
        if self._job: self.after_cancel(self._job)
        self.delete("all")

    def _tick(self):
        if not self._running: return
        self.delete("all")
        cx = cy = self._size // 2
        r = cx - 2
        for i in range(8):
            a = math.radians(self._angle + i * 45)
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a)
            alpha = int(60 + 195 * (i / 8))
            color = "#{:02x}{:02x}{:02x}".format(
                int(0x58 + (0xff-0x58)*(1-i/8)),
                int(0x65 + (0xff-0x65)*(1-i/8)),
                int(0xf2 + (0xff-0xf2)*(1-i/8))
            )
            self.create_oval(x-2, y-2, x+2, y+2, fill=color, outline="")
        self._angle = (self._angle + 15) % 360
        self._job = self.after(40, self._tick)


# ── Sidebar row ───────────────────────────────────────────────────────────────

class SidebarRow(tk.Frame):
    """Animated hover row for servers/DMs."""
    def __init__(self, parent, icon_img=None, label="", checkable=False,
                 on_click=None, **kw):
        super().__init__(parent, bg=SIDEBAR, cursor="hand2", **kw)
        self._selected   = False
        self._hovered    = False
        self._checkable  = checkable
        self._checked    = False
        self._on_click   = on_click
        self._anim_id    = None
        self._cur_bg     = self._hex_rgb(SIDEBAR)
        self._img_ref    = icon_img   # keep ref

        # icon
        self.icon_lbl = tk.Label(self, bg=SIDEBAR, width=36, height=36)
        self.icon_lbl.pack(side="left", padx=(8,6), pady=6)
        if icon_img:
            self.icon_lbl.config(image=icon_img)

        # label
        self.name_lbl = tk.Label(self, text=label, font=("Segoe UI", 10),
                                  bg=SIDEBAR, fg=TEXT2, anchor="w")
        self.name_lbl.pack(side="left", fill="x", expand=True, pady=6)

        # checkbox dot (for DMs)
        if checkable:
            self.check_canvas = tk.Canvas(self, width=18, height=18,
                                           bg=SIDEBAR, highlightthickness=0)
            self.check_canvas.pack(side="right", padx=10)
            self._draw_check()

        # bind all children
        for w in [self, self.icon_lbl, self.name_lbl]:
            w.bind("<Enter>",          self._on_enter)
            w.bind("<Leave>",          self._on_leave)
            w.bind("<ButtonPress-1>",  self._on_press)
            w.bind("<ButtonRelease-1>",self._on_release)
        if checkable:
            self.check_canvas.bind("<Enter>",          self._on_enter)
            self.check_canvas.bind("<Leave>",          self._on_leave)
            self.check_canvas.bind("<ButtonPress-1>",  self._on_press)
            self.check_canvas.bind("<ButtonRelease-1>",self._on_release)

    def set_icon(self, img):
        self._img_ref = img
        self.icon_lbl.config(image=img)

    def _draw_check(self):
        self.check_canvas.delete("all")
        if self._checked:
            self.check_canvas.create_oval(0,0,17,17, fill=ACCENT, outline="")
            self.check_canvas.create_text(9,9, text="✓", fill=WHITE,
                                           font=("Segoe UI",9,"bold"))
        else:
            self.check_canvas.create_oval(0,0,17,17, fill=SURFACE3, outline=MUTED)

    def get_checked(self): return self._checked

    def select(self, val=True):
        self._selected = val
        self._update_bg(ACCENT if val else (SURFACE3 if self._hovered else SIDEBAR))

    def _on_enter(self, e):
        self._hovered = True
        if not self._selected:
            self._update_bg(SURFACE3)

    def _on_leave(self, e):
        self._hovered = False
        if not self._selected:
            self._update_bg(SIDEBAR)

    def _on_press(self, e): pass

    def _on_release(self, e):
        if self._checkable:
            self._checked = not self._checked
            self._draw_check()
            self._update_bg(SURFACE if self._checked else SIDEBAR)
            self._selected = self._checked
        if self._on_click:
            self._on_click(self)

    def _hex_rgb(self, h):
        h = h.lstrip("#")
        return [int(h[i:i+2],16) for i in (0,2,4)]

    def _rgb_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]),int(rgb[1]),int(rgb[2]))

    def _update_bg(self, target_hex):
        target = self._hex_rgb(target_hex)
        if self._anim_id: self.after_cancel(self._anim_id)
        self._anim_to(target)

    def _anim_to(self, target):
        changed = False
        for i in range(3):
            diff = target[i] - self._cur_bg[i]
            if abs(diff) > 1:
                self._cur_bg[i] += diff * 0.3
                changed = True
            else:
                self._cur_bg[i] = target[i]
        c = self._rgb_hex(self._cur_bg)
        try:
            self.config(bg=c)
            self.icon_lbl.config(bg=c)
            self.name_lbl.config(bg=c)
            if self._checkable:
                self.check_canvas.config(bg=c)
        except: pass
        if changed:
            self._anim_id = self.after(16, lambda: self._anim_to(target))


# ── Tab bar (custom, replacing ttk.Notebook) ──────────────────────────────────

class TabBar(tk.Frame):
    def __init__(self, parent, tabs, on_change=None, **kw):
        super().__init__(parent, bg=SURFACE2, **kw)
        self._tabs      = tabs
        self._on_change = on_change
        self._active    = 0
        self._btns      = []
        self._indicator = None
        self._build()

    def _build(self):
        for i, (label, _) in enumerate(self._tabs):
            btn = tk.Label(self, text=label,
                           font=("Segoe UI", 10, "bold"),
                           bg=SURFACE2, fg=MUTED,
                           padx=24, pady=12, cursor="hand2")
            btn.pack(side="left")
            idx = i
            btn.bind("<Button-1>", lambda e, n=idx: self._switch(n))
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=TEXT2) if b != self._btns[self._active] else None)
            btn.bind("<Leave>", lambda e, b=btn, n=i: b.config(fg=WHITE if n==self._active else MUTED))
            self._btns.append(btn)

        # active indicator line
        self._line = tk.Frame(self, bg=ACCENT, height=3)

        self._switch(0, animate=False)

    def _switch(self, idx, animate=True):
        self._active = idx
        for i, b in enumerate(self._btns):
            b.config(fg=WHITE if i == idx else MUTED)
        # move indicator
        btn = self._btns[idx]
        self._line.place(in_=btn, x=0, rely=1.0, y=-3,
                         relwidth=1.0, height=3)
        if self._on_change:
            self._on_change(idx)

    def active(self):
        return self._active


# ── Main App ──────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord Cleaner  —  Made by Antor")
        self.geometry("1280x780")
        self.minsize(1050, 650)
        self.configure(bg=BG)

        self.token          = tk.StringVar()
        self.user_id        = None
        self.user_tag       = None
        self.user_avatar    = None
        self.guilds         = []
        self.guild_icons    = {}
        self.guild_rows     = []
        self.dm_channels    = []
        self.dm_rows        = []
        self.guild_channels = []
        self.selected_guild = None
        self.selected_guild_row = None
        self.found_msgs     = []
        self._stop_flag     = False
        self._total_msgs    = 0

        self._apply_style()
        self.update_idletasks()
        self._build_login()
        self._build_main()
        self.login_frame.pack(fill="both", expand=True)

    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("TScrollbar", background=SURFACE2, troughcolor=SIDEBAR,
                    borderwidth=0, relief="flat", arrowsize=0, width=6)
        s.map("TScrollbar", background=[("active", SURFACE3)])

    # ── LOGIN ─────────────────────────────────────────────────────────────

    def _build_login(self):
        self.login_frame = tk.Frame(self, bg=BG)

        # animated bg dots (subtle)
        self._dots_canvas = tk.Canvas(self.login_frame, bg=BG, highlightthickness=0)
        self._dots_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._dots = []
        self._init_dots()

        # ── scrollable canvas so both panels always visible ────────────────
        login_canvas = tk.Canvas(self.login_frame, bg=BG, highlightthickness=0)
        login_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        row = tk.Frame(login_canvas, bg=BG)
        row_win = login_canvas.create_window((0, 0), window=row, anchor="nw")

        def _center_row(e=None):
            login_canvas.update_idletasks()
            cw = login_canvas.winfo_width()
            ch = login_canvas.winfo_height()
            rw = row.winfo_reqwidth()
            rh = row.winfo_reqheight()
            x = max(0, (cw - rw) // 2)
            y = max(0, (ch - rh) // 2)
            login_canvas.coords(row_win, x, y)

        self.login_frame.bind("<Configure>", lambda e: _center_row())
        row.bind("<Configure>", lambda e: _center_row())

        # ── LOGIN CARD ─────────────────────────────────────────────────────
        card = tk.Frame(row, bg=SURFACE, padx=52, pady=48)
        card.pack(side="left", anchor="n")

        # icon + title
        title_row = tk.Frame(card, bg=SURFACE)
        title_row.pack(pady=(0,4))
        tk.Label(title_row, text="🧹", font=("Segoe UI Emoji",26),
                 bg=SURFACE).pack(side="left", padx=(0,8))
        tk.Label(title_row, text="Discord Cleaner",
                 font=("Segoe UI",22,"bold"), bg=SURFACE, fg=WHITE).pack(side="left")

        tk.Label(card, text="Bulk delete your messages across servers & DMs",
                 font=("Segoe UI",9), bg=SURFACE, fg=MUTED).pack(pady=(0,30))

        # token field
        tk.Label(card, text="USER TOKEN", font=("Segoe UI",8,"bold"),
                 bg=SURFACE, fg=MUTED, anchor="w").pack(fill="x")

        ef = tk.Frame(card, bg=SURFACE3, pady=0)
        ef.pack(fill="x", pady=(6,0))
        tk.Frame(ef, bg=ACCENT, width=3).pack(side="left", fill="y")

        self.token_entry = tk.Entry(ef, textvariable=self.token,
                                     width=42, show="•",
                                     font=("Consolas",10),
                                     bg=SURFACE3, fg=TEXT,
                                     insertbackground=WHITE,
                                     relief="flat", bd=10)
        self.token_entry.pack(side="left", fill="x", expand=True, ipady=5)

        self.eye_btn = tk.Label(ef, text="👁", font=("Segoe UI",12),
                                 bg=SURFACE3, fg=MUTED, cursor="hand2", padx=8)
        self.eye_btn.pack(side="right")
        self.eye_btn.bind("<Button-1>", lambda e: self._toggle_eye())

        self.login_err = tk.Label(card, text="", font=("Segoe UI",9),
                                   bg=SURFACE, fg=RED)
        self.login_err.pack(pady=(12,0))

        self.login_btn = AnimButton(card, "Log In  →",
                                     command=self._do_login,
                                     bg_normal=ACCENT, bg_hover=ACCENT_H,
                                     width=200, height=42,
                                     font=("Segoe UI",11,"bold"))
        self.login_btn.pack(pady=(16,0))

        tk.Label(card, text="Made by Antor",
                 font=("Segoe UI",8), bg=SURFACE, fg=MUTED).pack(pady=(20,0))

        self.token_entry.bind("<Return>", lambda e: self._do_login())

        # ── GUIDE PANEL ────────────────────────────────────────────────────
        guide = tk.Frame(row, bg=SURFACE2, padx=28, pady=28, width=320, height=560)
        guide.pack(side="left", anchor="n", padx=(18, 0))
        guide.pack_propagate(False)

        # title row
        gh = tk.Frame(guide, bg=SURFACE2)
        gh.pack(fill="x", pady=(0, 14))
        tk.Label(gh, text="🔑", font=("Segoe UI Emoji", 16),
                 bg=SURFACE2).pack(side="left", padx=(0, 8))
        tk.Label(gh, text="How to get your token",
                 font=("Segoe UI", 11, "bold"), bg=SURFACE2, fg=WHITE).pack(side="left")

        # divider
        tk.Frame(guide, bg=SURFACE3, height=1).pack(fill="x", pady=(0, 14))

        steps = [
            ("1", "Open Discord in your\n web browser", "discord.com/app"),
            ("2", "Press  F12  to open\nDevTools"),
            ("3", "Go to the  Network  tab,\nthen press  Ctrl+R"),
            ("4", 'Click any request →\nopen  Headers  tab'),
            ("5", "Find  Authorization:\nand copy that value"),
            ("6", "Paste it into the\ntoken field on the left"),
        ]

        for num, desc, *hint in steps:
            row2 = tk.Frame(guide, bg=SURFACE2)
            row2.pack(fill="x", pady=4)

            # step circle
            circ = tk.Canvas(row2, width=24, height=24, bg=SURFACE2,
                             highlightthickness=0)
            circ.create_oval(1, 1, 23, 23, fill=ACCENT, outline="")
            circ.create_text(12, 12, text=num, fill=WHITE,
                             font=("Segoe UI", 8, "bold"))
            circ.pack(side="left", padx=(0, 10))

            col = tk.Frame(row2, bg=SURFACE2)
            col.pack(side="left", fill="x", expand=True)
            tk.Label(col, text=desc, font=("Segoe UI", 9),
                     bg=SURFACE2, fg=TEXT2, justify="left", anchor="w").pack(fill="x")
            if hint:
                tk.Label(col, text=hint[0], font=("Consolas", 8),
                         bg=SURFACE3, fg=ACCENT, padx=6, pady=2,
                         anchor="w").pack(fill="x", pady=(2, 0))

        # divider
        tk.Frame(guide, bg=SURFACE3, height=1).pack(fill="x", pady=(16, 12))

        # example token
        ex = tk.Frame(guide, bg=SURFACE3, padx=12, pady=10)
        ex.pack(fill="x", pady=(0, 10))
        tk.Label(ex, text="📋  Example token format",
                 font=("Segoe UI", 8, "bold"), bg=SURFACE3, fg=MUTED).pack(anchor="w")
        example_token = "MTExOTk4NzY1.Gh3kQa.xK9mZpW2nR7vLcYbDqEjFuAtNsOiHgPlTwUyVrXo"
        tok_box = tk.Frame(ex, bg=BG, padx=8, pady=6)
        tok_box.pack(fill="x", pady=(6, 0))
        tk.Label(tok_box, text=example_token,
                 font=("Consolas", 7), bg=BG, fg="#7983f5",
                 wraplength=255, justify="left", anchor="w").pack(fill="x")
        tk.Label(ex,
                 text="3 parts separated by dots  \u00b7  looks random  \u00b7  ~70 chars",
                 font=("Segoe UI", 7), bg=SURFACE3, fg=MUTED,
                 wraplength=260, justify="left").pack(anchor="w", pady=(5, 0))

        # divider
        tk.Frame(guide, bg=SURFACE3, height=1).pack(fill="x", pady=(4, 12))

        # security warning
        sec = tk.Frame(guide, bg="#1a0a0a", padx=12, pady=10)
        sec.pack(fill="x")
        tk.Label(sec, text="🔒  Keep your token private!",
                 font=("Segoe UI", 9, "bold"), bg="#1a0a0a", fg=RED).pack(anchor="w")
        tk.Label(sec,
                 text="Never share your token with anyone —\n"
                      "not friends, not support staff, not bots.\n"
                      "Anyone with it has full access to your account.",
                 font=("Segoe UI", 8), bg="#1a0a0a", fg="#e07070",
                 justify="left", wraplength=260).pack(anchor="w", pady=(4, 0))

    def _toggle_eye(self):
        show = self.token_entry.cget("show")
        self.token_entry.config(show="" if show == "•" else "•")
        self.eye_btn.config(text="🙈" if show == "•" else "👁")

    def _init_dots(self):
        import random
        for _ in range(18):
            x = random.randint(50, 1050)
            y = random.randint(50, 650)
            r = random.randint(3, 7)
            dx = random.choice([-1,1]) * random.uniform(0.3, 0.7)
            dy = random.choice([-1,1]) * random.uniform(0.3, 0.7)
            dot = self._dots_canvas.create_oval(x-r,y-r,x+r,y+r,
                                                 fill=SURFACE, outline="")
            self._dots.append([dot, x, y, r, dx, dy])
        self._animate_dots()

    def _animate_dots(self):
        if not self.login_frame.winfo_ismapped(): return
        W, H = self.winfo_width() or 1120, self.winfo_height() or 720
        for d in self._dots:
            dot, x, y, r, dx, dy = d
            x += dx; y += dy
            if x < r or x > W-r: dx *= -1
            if y < r or y > H-r: dy *= -1
            d[1]=x; d[2]=y; d[4]=dx; d[5]=dy
            self._dots_canvas.coords(dot, x-r, y-r, x+r, y+r)
        self.after(30, self._animate_dots)

    def _do_login(self):
        self.login_err.config(text="Connecting…", fg=MUTED)
        self.login_btn.config_text("Connecting…")
        self.update()
        t = self.token.get().strip()
        if not t:
            self.login_err.config(text="Token cannot be empty.", fg=RED)
            self.login_btn.config_text("Log In  →")
            return
        def worker():
            try:
                me = get_me(t)
                self.user_id  = me["id"]
                self.user_tag = me.get("global_name") or me.get("username","Unknown")
                av = me.get("avatar")
                if av:
                    data = fetch_image_bytes(f"{CDN}/avatars/{me['id']}/{av}.png?size=80")
                    if data: self.user_avatar = make_circle(data, 44)
                if not self.user_avatar:
                    self.user_avatar = make_initials(self.user_tag[0], 44)
                self.after(0, self._go_main)
            except Exception as e:
                self.after(0, lambda err=e: self.login_err.config(text=f"Login failed: {err}", fg=RED))
                self.after(0, lambda: self.login_btn.config_text("Log In  →"))
        threading.Thread(target=worker, daemon=True).start()

    def _go_main(self):
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self._load_data()

    # ── MAIN LAYOUT ───────────────────────────────────────────────────────

    def _build_main(self):
        self.main_frame = tk.Frame(self, bg=BG)
        self._build_topbar()

        # content area
        content = tk.Frame(self.main_frame, bg=BG)
        content.pack(fill="both", expand=True)

        # custom tab bar
        self.tabbar = TabBar(content,
                             tabs=[("  🏰  Servers", None), ("  💬  Direct Messages", None)],
                             on_change=self._on_tab_change)
        self.tabbar.pack(fill="x")

        # tab frames stacked
        self.tab_frames = tk.Frame(content, bg=BG)
        self.tab_frames.pack(fill="both", expand=True)

        self.server_frame = tk.Frame(self.tab_frames, bg=BG)
        self.dm_frame     = tk.Frame(self.tab_frames, bg=BG)

        self._build_server_tab()
        self._build_dm_tab()

        self.server_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.dm_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.server_frame.lift()

        # status bar
        sb = tk.Frame(self.main_frame, bg=SURFACE, height=28)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        self.statusbar = tk.Label(sb, text="Ready.", font=("Segoe UI",8),
                                   bg=SURFACE, fg=MUTED, anchor="w", padx=14)
        self.statusbar.pack(side="left", fill="y")
        tk.Label(sb, text="Made by Antor", font=("Segoe UI",8),
                 bg=SURFACE, fg=MUTED, padx=14).pack(side="right")

    def _on_tab_change(self, idx):
        if not hasattr(self, 'server_frame'): return
        if idx == 0:
            self.server_frame.lift()
        else:
            self.dm_frame.lift()

    def _build_topbar(self):
        bar = tk.Frame(self.main_frame, bg=SURFACE2, height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        left = tk.Frame(bar, bg=SURFACE2)
        left.pack(side="left", padx=14, fill="y")
        tk.Label(left, text="🧹", font=("Segoe UI Emoji",14),
                 bg=SURFACE2).pack(side="left", pady=10)
        tk.Label(left, text=" Discord Cleaner",
                 font=("Segoe UI",13,"bold"), bg=SURFACE2, fg=WHITE).pack(side="left")

        right = tk.Frame(bar, bg=SURFACE2)
        right.pack(side="right", padx=14, fill="y")

        logout = AnimButton(right, "Logout",
                             command=self._logout,
                             bg_normal=SURFACE3, bg_hover=SURFACE,
                             bg_press=BG, fg=TEXT2,
                             width=80, height=30,
                             font=("Segoe UI",9))
        logout.pack(side="right", pady=10, padx=(8,0))

        # name col
        nc = tk.Frame(right, bg=SURFACE2)
        nc.pack(side="right", padx=(0,10), fill="y")
        self.name_lbl = tk.Label(nc, text="", font=("Segoe UI",10,"bold"),
                                  bg=SURFACE2, fg=WHITE, anchor="e")
        self.name_lbl.pack(anchor="e", pady=(10,0))
        dot_row = tk.Frame(nc, bg=SURFACE2)
        dot_row.pack(anchor="e")
        c = tk.Canvas(dot_row, width=10, height=10, bg=SURFACE2, highlightthickness=0)
        c.create_oval(1,1,9,9, fill=ONLINE, outline="")
        c.pack(side="left")
        tk.Label(dot_row, text=" Online", font=("Segoe UI",8),
                 bg=SURFACE2, fg=ONLINE).pack(side="left")

        self.avatar_lbl = tk.Label(right, bg=SURFACE2)
        self.avatar_lbl.pack(side="right", pady=6)

    # ── SERVER TAB ────────────────────────────────────────────────────────

    def _build_server_tab(self):
        pw = tk.PanedWindow(self.server_frame, orient="horizontal",
                             bg=BG, sashwidth=1, sashrelief="flat",
                             sashpad=0)
        pw.pack(fill="both", expand=True)

        # servers
        s_panel = tk.Frame(pw, bg=SIDEBAR, width=220)
        pw.add(s_panel, minsize=180)
        tk.Label(s_panel, text="SERVERS", font=("Segoe UI",8,"bold"),
                 bg=SIDEBAR, fg=MUTED, anchor="w", padx=14, pady=10).pack(fill="x")
        self.s_spinner = Spinner(s_panel, size=20)
        self.s_spinner.pack()
        sc, sf = self._scrollable(s_panel, SIDEBAR)
        self.server_scroll_frame = sf

        # channels
        c_panel = tk.Frame(pw, bg=SURFACE, width=210)
        pw.add(c_panel, minsize=170)
        c_head = tk.Frame(c_panel, bg=SURFACE)
        c_head.pack(fill="x", padx=14, pady=(10,0))
        tk.Label(c_head, text="CHANNELS", font=("Segoe UI",8,"bold"),
                 bg=SURFACE, fg=MUTED, anchor="w").pack(side="left")
        self.chan_select_all_btn = tk.Label(
            c_head, text="Select all", font=("Segoe UI",8,"bold"),
            bg=SURFACE, fg=ACCENT, cursor="hand2")
        self.chan_select_all_btn.pack(side="right")
        self.chan_select_all_btn.bind("<Button-1>", lambda e: self._toggle_all_channels())
        tk.Frame(c_panel, bg=SURFACE, height=6).pack(fill="x")
        cc, cf = self._scrollable(c_panel, SURFACE)
        self.chan_scroll_frame = cf

        scan_s = AnimButton(c_panel, "🔍  Scan Selected",
                             command=lambda: self._scan("server"),
                             bg_normal=ACCENT, bg_hover=ACCENT_H,
                             width=180, height=36)
        scan_s.pack(padx=10, pady=10, fill="x")

        # msg panel
        right = tk.Frame(pw, bg=BG)
        pw.add(right, minsize=400)
        self._build_msg_panel(right, "server")

    def _build_dm_tab(self):
        pw = tk.PanedWindow(self.dm_frame, orient="horizontal",
                             bg=BG, sashwidth=1, sashrelief="flat",
                             sashpad=0)
        pw.pack(fill="both", expand=True)

        dm_panel = tk.Frame(pw, bg=SIDEBAR, width=260)
        pw.add(dm_panel, minsize=200)
        tk.Label(dm_panel, text="DIRECT MESSAGES", font=("Segoe UI",8,"bold"),
                 bg=SIDEBAR, fg=MUTED, anchor="w", padx=14, pady=10).pack(fill="x")
        self.d_spinner = Spinner(dm_panel, size=20)
        self.d_spinner.pack()
        dc, df = self._scrollable(dm_panel, SIDEBAR)
        self.dm_scroll_frame = df

        scan_d = AnimButton(dm_panel, "🔍  Scan Selected",
                             command=lambda: self._scan("dm"),
                             bg_normal=ACCENT, bg_hover=ACCENT_H,
                             width=220, height=36)
        scan_d.pack(padx=10, pady=10, fill="x")

        right = tk.Frame(pw, bg=BG)
        pw.add(right, minsize=400)
        self._build_msg_panel(right, "dm")

    def _scrollable(self, parent, bg):
        frame = tk.Frame(parent, bg=bg)
        frame.pack(fill="both", expand=True)
        c = tk.Canvas(frame, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=c.yview)
        c.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        c.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(c, bg=bg)
        win = c.create_window((0,0), window=inner, anchor="nw")

        # Windows / macOS scroll
        def _on_mousewheel(event):
            c.yview_scroll(-1 * (event.delta // 120), "units")

        # Linux scroll (Button-4 = up, Button-5 = down)
        def _on_mousewheel_linux(event):
            if event.num == 4:
                c.yview_scroll(-1, "units")
            elif event.num == 5:
                c.yview_scroll(1, "units")

        def _bind_tree(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>",   _on_mousewheel_linux)
            widget.bind("<Button-5>",   _on_mousewheel_linux)
            for child in widget.winfo_children():
                _bind_tree(child)

        def _on_inner_configure(e):
            c.config(scrollregion=c.bbox("all"))
            _bind_tree(inner)

        inner.bind("<Configure>", _on_inner_configure)
        c.bind("<Configure>", lambda e: c.itemconfig(win, width=e.width))
        _bind_tree(c)

        return c, inner

    # ── MSG PANEL ─────────────────────────────────────────────────────────

    def _build_msg_panel(self, parent, mode):
        # header strip
        hf = tk.Frame(parent, bg=SURFACE2, padx=14, pady=10)
        hf.pack(fill="x")
        tk.Label(hf, text="Messages", font=("Segoe UI",11,"bold"),
                 bg=SURFACE2, fg=WHITE).pack(side="left")
        count_lbl = tk.Label(hf, text="", font=("Segoe UI",9),
                              bg=SURFACE2, fg=MUTED)
        count_lbl.pack(side="left", padx=12)

        # scan spinner in header
        scan_spin = Spinner(hf, size=18)
        scan_spin.pack(side="left")

        # log
        log_frame = tk.Frame(parent, bg=SURFACE2)
        log_frame.pack(fill="both", expand=True)
        log = scrolledtext.ScrolledText(log_frame,
                                         bg=SURFACE2, fg=TEXT2,
                                         font=("Consolas",9),
                                         relief="flat", bd=0,
                                         state="disabled",
                                         wrap="word",
                                         highlightthickness=0,
                                         insertbackground=WHITE,
                                         selectbackground=ACCENT)
        log.pack(fill="both", expand=True, padx=0)
        log.tag_config("deleted", foreground=GREEN)
        log.tag_config("error",   foreground=RED)
        log.tag_config("info",    foreground=MUTED)
        log.tag_config("warn",    foreground=WARN)
        log.tag_config("head",    foreground=ACCENT, font=("Consolas",9,"bold"))

        # bottom
        bot = tk.Frame(parent, bg=BG, padx=14, pady=12)
        bot.pack(fill="x")

        # progress
        prog = SmoothProgress(bot, height=10)
        prog.pack(fill="x", pady=(0,10))

        # stats row
        sr = tk.Frame(bot, bg=BG)
        sr.pack(fill="x", pady=(0,10))

        pct_lbl  = tk.Label(sr, text="0%",    font=("Segoe UI",10,"bold"), bg=BG, fg=ACCENT)
        pct_lbl.pack(side="left")
        del_lbl  = tk.Label(sr, text="",      font=("Segoe UI",9), bg=BG, fg=GREEN)
        del_lbl.pack(side="left", padx=(12,0))
        rem_lbl  = tk.Label(sr, text="",      font=("Segoe UI",9), bg=BG, fg=MUTED)
        rem_lbl.pack(side="left", padx=(12,0))
        spd_lbl  = tk.Label(sr, text="",      font=("Segoe UI",9), bg=BG, fg=TEXT2)
        spd_lbl.pack(side="right")
        eta_lbl  = tk.Label(sr, text="",      font=("Segoe UI",9), bg=BG, fg=MUTED)
        eta_lbl.pack(side="right", padx=(0,14))

        # buttons
        br = tk.Frame(bot, bg=BG)
        br.pack(fill="x")

        del_btn = AnimButton(br, "🗑  Delete All Found",
                              command=lambda: self._confirm_delete(mode),
                              bg_normal=RED, bg_hover=RED_H, bg_press="#9b2226",
                              width=180, height=38)
        del_btn.pack(side="left")

        stop_btn = AnimButton(br, "⏹  Stop",
                               command=self._stop,
                               bg_normal=SURFACE3, bg_hover=SURFACE,
                               bg_press=SURFACE2, fg=TEXT2,
                               width=90, height=38,
                               font=("Segoe UI",9))
        stop_btn.pack(side="left", padx=(8,0))

        clear_btn = AnimButton(br, "🗒  Clear",
                                command=lambda: self._log_clear(mode),
                                bg_normal=SURFACE3, bg_hover=SURFACE,
                                bg_press=SURFACE2, fg=TEXT2,
                                width=80, height=38,
                                font=("Segoe UI",9))
        clear_btn.pack(side="left", padx=(8,0))

        if mode == "server":
            self.s_count = count_lbl; self.s_log = log; self.s_prog = prog
            self.s_pct = pct_lbl; self.s_del = del_lbl; self.s_rem = rem_lbl
            self.s_eta = eta_lbl; self.s_spd = spd_lbl
            self.s_scan_spin = scan_spin
        else:
            self.d_count = count_lbl; self.d_log = log; self.d_prog = prog
            self.d_pct = pct_lbl; self.d_del = del_lbl; self.d_rem = rem_lbl
            self.d_eta = eta_lbl; self.d_spd = spd_lbl
            self.d_scan_spin = scan_spin

    # ── LOAD DATA ─────────────────────────────────────────────────────────

    def _load_data(self):
        if self.user_avatar: self.avatar_lbl.config(image=self.user_avatar)
        self.name_lbl.config(text=self.user_tag)
        self.s_spinner.start()
        self.d_spinner.start()
        self._status("Fetching servers and DMs…")

        def worker():
            try:
                guilds = get_guilds(self.token.get())
                self.guilds = sorted(guilds, key=lambda g: g["name"].lower())
                dms = get_dm_channels(self.token.get())
                self.dm_channels = dms
                self.after(0, self._populate_servers)
                self.after(0, self._populate_dms)
                self.after(0, lambda: self._status(
                    f"Loaded {len(self.guilds)} servers · {len(dms)} DMs"))
            except Exception as e:
                self.after(0, lambda err=e: self._status(f"Error: {err}"))
        threading.Thread(target=worker, daemon=True).start()

    def _populate_servers(self):
        self.s_spinner.stop()
        for w in self.server_scroll_frame.winfo_children(): w.destroy()
        self.guild_rows.clear()

        for g in self.guilds:
            row = SidebarRow(self.server_scroll_frame,
                              label=g["name"],
                              on_click=lambda r, guild=g: self._on_server_click(r, guild))
            row.pack(fill="x", padx=6, pady=2)
            self.guild_rows.append((g, row))
            # load icon async
            def load_icon(guild=g, row=row):
                ih = guild.get("icon")
                img = None
                if ih:
                    data = fetch_image_bytes(f"{CDN}/icons/{guild['id']}/{ih}.png?size=64")
                    if data: img = make_circle(data, 34)
                if not img:
                    img = make_initials(guild["name"][0], 34, guild_color(guild["name"]))
                if img:
                    self.guild_icons[guild["id"]] = img
                    self.after(0, lambda r=row, i=img: r.set_icon(i))
            threading.Thread(target=load_icon, daemon=True).start()

    def _on_server_click(self, clicked_row, guild):
        # deselect all
        for _, row in self.guild_rows:
            row.select(False)
        clicked_row.select(True)
        self.selected_guild = guild
        self._load_channels(guild)

    def _populate_dms(self):
        self.d_spinner.stop()
        for w in self.dm_scroll_frame.winfo_children(): w.destroy()
        self.dm_rows.clear()

        self.dm_channels.sort(key=lambda dm: self._dm_label(dm).lower())

        for dm in self.dm_channels:
            name = self._dm_label(dm)
            row = SidebarRow(self.dm_scroll_frame,
                              label=name,
                              checkable=True)
            row.pack(fill="x", padx=6, pady=2)
            dm["_row"] = row
            self.dm_rows.append((dm, row))

            def load_dm_icon(dm_=dm, row=row):
                recs = dm_.get("recipients", [])
                img = None
                if recs:
                    av = recs[0].get("avatar"); uid2 = recs[0].get("id")
                    if av:
                        data = fetch_image_bytes(f"{CDN}/avatars/{uid2}/{av}.png?size=64")
                        if data: img = make_circle(data, 34)
                    if not img:
                        uname = recs[0].get("username","?")
                        img = make_initials(uname[0], 34, guild_color(uname))
                else:
                    img = make_initials("G", 34, ACCENT)
                if img: self.after(0, lambda r=row, i=img: r.set_icon(i))
            threading.Thread(target=load_dm_icon, daemon=True).start()

    def _dm_label(self, dm):
        if dm.get("type") == 3: return dm.get("name") or "Group DM"
        recs = dm.get("recipients", [])
        return recs[0].get("global_name") or recs[0].get("username","Unknown") if recs else "Unknown"

    # ── CHANNELS ──────────────────────────────────────────────────────────

    def _load_channels(self, guild):
        for w in self.chan_scroll_frame.winfo_children(): w.destroy()
        self._status(f"Loading channels for {guild['name']}…")

        def worker():
            try:
                chans = get_guild_channels(self.token.get(), guild["id"])
                text = sorted([c for c in chans if c.get("type") in (0,5,15)],
                               key=lambda c: c.get("position",0))
                self.guild_channels = text
                self.after(0, lambda: self._render_channels(text))
                self.after(0, lambda: self._status(f"{len(text)} channels — {guild['name']}"))
            except Exception as e:
                self.after(0, lambda err=e: self._status(f"Channel error: {err}"))
        threading.Thread(target=worker, daemon=True).start()

    def _render_channels(self, channels):
        for w in self.chan_scroll_frame.winfo_children(): w.destroy()
        self._chan_vars = []
        if hasattr(self, "chan_select_all_btn"):
            self.chan_select_all_btn.config(text="Select all")
        for c in channels:
            prefix = "📢" if c.get("type")==5 else "#"
            var = tk.BooleanVar()
            row = tk.Frame(self.chan_scroll_frame, bg=SURFACE, cursor="hand2")
            row.pack(fill="x", padx=6, pady=1)
            cb = tk.Checkbutton(row, variable=var, bg=SURFACE,
                                  selectcolor=ACCENT, activebackground=SURFACE,
                                  relief="flat", bd=0, fg=WHITE)
            cb.pack(side="left", padx=(8,2))
            lbl = tk.Label(row, text=f"{prefix} {c['name']}",
                            font=("Segoe UI",10), bg=SURFACE, fg=TEXT2, anchor="w")
            lbl.pack(side="left", fill="x", expand=True, pady=6)

            def toggle(r=row, v=var, l=lbl):
                v.set(not v.get())
                r.config(bg=SURFACE if not v.get() else SURFACE3)
                l.config(bg=SURFACE if not v.get() else SURFACE3)

            row.bind("<Button-1>", lambda e, f=toggle: f())
            lbl.bind("<Button-1>", lambda e, f=toggle: f())
            self._chan_vars.append((c, var, row, lbl))

    def _toggle_all_channels(self):
        chan_vars = getattr(self, "_chan_vars", [])
        if not chan_vars:
            return
        select = not all(v.get() for _, v, _, _ in chan_vars)
        for _, v, r, l in chan_vars:
            v.set(select)
            bg = SURFACE3 if select else SURFACE
            r.config(bg=bg)
            l.config(bg=bg)
        self.chan_select_all_btn.config(text="Deselect all" if select else "Select all")

    # ── SCAN ──────────────────────────────────────────────────────────────

    def _scan(self, mode):
        self._stop_flag = False
        if mode == "server":
            if not self.selected_guild:
                messagebox.showinfo("No Server", "Click a server first."); return
            sel = [c for c, v, r, l in getattr(self,"_chan_vars",[]) if v.get()]
            if not sel:
                messagebox.showinfo("No Channel", "Check at least one channel."); return
            channels = sel
            self._log_clear("server")
            self.s_count.config(text="Scanning…")
            self.s_scan_spin.start()
            threading.Thread(target=self._scan_server, args=(channels,), daemon=True).start()
        else:
            sel_dms = [dm for dm,row in self.dm_rows if row.get_checked()]
            if not sel_dms:
                messagebox.showinfo("No DM", "Check at least one DM."); return
            self._log_clear("dm")
            self.d_count.config(text="Scanning…")
            self.d_scan_spin.start()
            threading.Thread(target=self._scan_dms, args=(sel_dms,), daemon=True).start()

    def _scan_server(self, channels):
        token = self.token.get(); uid = self.user_id; gid = self.selected_guild["id"]
        msgs = []
        for chan in channels:
            if self._stop_flag: break
            cid = chan["id"]; cname = chan["name"]; offset = 0
            self._log("server", f"◆ #{cname}", "head")
            while not self._stop_flag:
                try:
                    data = search_guild(token, gid, cid, uid, offset)
                    batch = [{"id":m["id"],"channel_id":m["channel_id"],
                              "channel":cname,"content":m.get("content",""),
                              "ts":m.get("timestamp","")}
                             for ctx in data.get("messages",[])
                             for m in ctx if m.get("author",{}).get("id")==uid]
                    msgs.extend(batch)
                    total = data.get("total_results",0); offset += 25
                    self._log("server", f"  {len(msgs)} messages found so far…", "info")
                    if offset >= total or not batch: break
                    time.sleep(0.35)
                except Exception as e:
                    self._log("server", f"  Error: {e}", "error"); break
        self.found_msgs = msgs; c = len(msgs)
        self.after(0, self.s_scan_spin.stop)
        self.after(0, lambda: self.s_count.config(text=f"{c} message{'s' if c!=1 else ''} found"))
        self._log("server", f"\n✅  Scan complete — {c} messages found.", "info")

    def _scan_dms(self, dms):
        token = self.token.get(); uid = self.user_id; msgs = []
        for dm in dms:
            if self._stop_flag: break
            cid = dm["id"]; cname = self._dm_label(dm); offset = 0
            self._log("dm", f"◆ {cname}", "head")
            while not self._stop_flag:
                try:
                    data = search_dm(token, cid, uid, offset)
                    batch = [{"id":m["id"],"channel_id":cid,
                              "channel":cname,"content":m.get("content",""),
                              "ts":m.get("timestamp","")}
                             for ctx in data.get("messages",[])
                             for m in ctx if m.get("author",{}).get("id")==uid]
                    msgs.extend(batch)
                    total = data.get("total_results",0); offset += 25
                    self._log("dm", f"  {len(msgs)} messages found so far…", "info")
                    if offset >= total or not batch: break
                    time.sleep(0.35)
                except Exception as e:
                    self._log("dm", f"  Error: {e}", "error"); break
        self.found_msgs = msgs; c = len(msgs)
        self.after(0, self.d_scan_spin.stop)
        self.after(0, lambda: self.d_count.config(text=f"{c} message{'s' if c!=1 else ''} found"))
        self._log("dm", f"\n✅  Scan complete — {c} messages found.", "info")

    # ── DELETE ────────────────────────────────────────────────────────────

    def _confirm_delete(self, mode):
        c = len(self.found_msgs)
        if c == 0:
            messagebox.showinfo("Nothing to delete","Run a scan first."); return
        if not messagebox.askyesno("Confirm Delete",
            f"Permanently delete {c} message{'s' if c!=1 else ''}?\n\nThis CANNOT be undone.",
            icon="warning"): return
        self._stop_flag = False
        threading.Thread(target=self._delete_worker, args=(mode,), daemon=True).start()

    def _delete_worker(self, mode):
        token = self.token.get()
        msgs  = list(self.found_msgs)
        total = len(msgs)
        prog  = self.s_prog if mode=="server" else self.d_prog
        pct   = self.s_pct  if mode=="server" else self.d_pct
        dlbl  = self.s_del  if mode=="server" else self.d_del
        rlbl  = self.s_rem  if mode=="server" else self.d_rem
        elbl  = self.s_eta  if mode=="server" else self.d_eta
        slbl  = self.s_spd  if mode=="server" else self.d_spd

        self.after(0, prog.reset)
        deleted = 0; start = time.time()
        # adaptive delay — starts at 0.22, backs off on errors
        delay = 0.22

        for i, m in enumerate(msgs):
            if self._stop_flag:
                self._log(mode, "\n⏹  Stopped by user.", "warn"); break
            try:
                ok = delete_msg(token, m["channel_id"], m["id"])
                snippet = m["content"][:72].replace("\n"," ")
                ts = m["ts"][:19].replace("T"," ") if m["ts"] else ""
                if ok:
                    deleted += 1
                    delay = max(0.18, delay * 0.98)   # slowly speed up on success
                    self._log(mode, f"✓  [{m['channel']}]  {snippet}", "deleted")
                else:
                    delay = min(0.5, delay * 1.3)     # slow down on fail
                    self._log(mode, f"✗  Failed msg {m['id']}", "error")
            except Exception as e:
                delay = min(0.5, delay * 1.4)
                self._log(mode, f"  Error: {e}", "error")

            done = i + 1
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            remaining = total - done
            eta_sec = remaining / rate if rate > 0 else 0

            def fmt_eta(s):
                if s < 60:   return f"{int(s)}s"
                if s < 3600: return f"{int(s//60)}m {int(s%60)}s"
                return f"{int(s//3600)}h {int((s%3600)//60)}m"

            _p = int(done/total*100); _d=deleted; _r=remaining
            _e=fmt_eta(eta_sec); _rt=rate
            self.after(0, lambda v=done,mx=total,p=_p,d=_d,r=_r,e=_e,rt=_rt: [
                prog.set_value(v, mx),
                pct.config(text=f"{p}%"),
                dlbl.config(text=f"✓ {d} deleted"),
                rlbl.config(text=f"{r} remaining"),
                elbl.config(text=f"ETA {e}"),
                slbl.config(text=f"{rt:.1f}/s"),
            ])
            time.sleep(delay)

        self._log(mode, f"\n🏁  Done — {deleted}/{total} deleted.", "info")
        self.found_msgs = []
        self.after(0, lambda: [elbl.config(text="Done ✓"), slbl.config(text="")])

    # ── HELPERS ───────────────────────────────────────────────────────────

    def _log(self, mode, text, tag=""):
        w = self.s_log if mode=="server" else self.d_log
        def _do():
            w.config(state="normal")
            w.insert("end", text+"\n", tag)
            w.see("end")
            w.config(state="disabled")
        self.after(0, _do)

    def _log_clear(self, mode):
        w = self.s_log if mode=="server" else self.d_log
        w.config(state="normal"); w.delete("1.0","end"); w.config(state="disabled")
        self.found_msgs = []

    def _status(self, msg):
        self.after(0, lambda: self.statusbar.config(text=msg))

    def _stop(self):
        self._stop_flag = True; self._status("Stop requested…")

    def _logout(self):
        self.token.set(""); self.user_id=None; self.user_tag=None
        self.user_avatar=None; self.guilds=[]; self.dm_channels=[]
        self.found_msgs=[]; self.selected_guild=None
        for w in self.server_scroll_frame.winfo_children(): w.destroy()
        for w in self.dm_scroll_frame.winfo_children(): w.destroy()
        for w in self.chan_scroll_frame.winfo_children(): w.destroy()
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.login_err.config(text="")
        self.login_btn.config_text("Log In  →")
        self._animate_dots()


if __name__ == "__main__":
    App().mainloop()
