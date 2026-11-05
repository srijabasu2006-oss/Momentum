"""
MOMENTUM // v2.4  —  Productivity Analytics Dashboard
Standard-mode desktop app built with tkinter + matplotlib.

Install:  pip install matplotlib
Run:      python main.py
"""
import random
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ───────────────────────── DESIGN TOKENS ─────────────────────────
CANVAS, SURFACE, SIDEBAR = "#F8F9FC", "#FFFFFF", "#F1F5F9"
BORDER, INK, MUTED = "#E2E8F0", "#0F172A", "#64748B"
COBALT, COBALT_HOVER, COBALT_TINT = "#2563EB", "#1D4ED8", "#DBEAFE"
EMERALD, AMBER = "#10B981", "#D97706"

TAG_STYLES = {  # type -> (background tint, text colour)
    "Deep Work": ("#EFF6FF", COBALT),
    "Planning": ("#ECFDF5", "#047857"),
    "Review": ("#FFFBEB", AMBER),
    "Shallow": ("#F1F5F9", MUTED),
}

NAV_ITEMS = ["Dashboard", "Deep Work", "Analytics", "Flow State", "Settings"]

WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEK_CUR = [62, 71, 68, 84, 79, 91, 88]
WEEK_PREV = [55, 60, 66, 70, 68, 74, 72]
_rng = random.Random(11)
MONTH_CUR = [round(60 + i * 0.9 + _rng.uniform(-6, 6)) for i in range(30)]
MONTH_PREV = [round(52 + i * 0.7 + _rng.uniform(-6, 6)) for i in range(30)]

SEED_FEED = [
    ("API Schema Refactor", "Backend", "Deep Work", "1h 45m", "09:12"),
    ("Q4 Roadmap Draft", "Strategy", "Planning", "50m", "11:05"),
    ("Design Token Audit", "Frontend", "Deep Work", "1h 30m", "13:40"),
    ("Inbox Zero Sweep", "Ops", "Shallow", "25m", "14:22"),
    ("Data Pipeline Review", "Analytics", "Deep Work", "2h 00m", "16:10"),
    ("Sprint Retro Notes", "Team", "Review", "35m", "17:05"),
]


def pick_font(root):
    available = set(tkfont.families(root))
    for name in ("Inter", "Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"):
        if name in available:
            return name
    return "TkDefaultFont"


def card(parent, **kw):
    return tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                    highlightthickness=1, **kw)


class MomentumApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg=CANVAS)
        self.title("MOMENTUM // v2.4")
        self.geometry("1320x840")
        self.minsize(1120, 720)

        fam = pick_font(self)
        self.F = lambda size, weight="normal": tkfont.Font(family=fam, size=size, weight=weight)
        self.mono = tkfont.Font(family="Consolas" if "Consolas" in set(tkfont.families(self))
                                else "Courier New", size=10)

        # state
        self.jobs = {}
        self.feed = list(SEED_FEED)
        self.deep_minutes = 402          # 6h 42m
        self.focus_score = 94.2
        self.total = 25 * 60
        self.remaining = self.total
        self.running = False
        self.session_no = 1
        self.active_nav = "Dashboard"
        self.active_range = "7D"
        self.active_duration = "25 min"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages()
        self._show_page("Dashboard")
        self._log("MOMENTUM online. Sensors calibrated.")
        self._schedule_live_metrics()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ───────────────────────── SIDEBAR ─────────────────────────
    def _build_sidebar(self):
        side = tk.Frame(self, bg=SIDEBAR, width=232)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)

        brand = tk.Frame(side, bg=SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(28, 22))
        lbl_b = tk.Label(brand, text="MOMENTUM", font=self.F(16, "bold"), bg=SIDEBAR, fg=INK)
        lbl_b.pack(side="left")
        lbl_v = tk.Label(brand, text="  // v2.4", font=self.F(10), bg=SIDEBAR, fg=MUTED)
        lbl_v.pack(side="left", pady=(3, 0))

        tk.Label(side, text="WORKSPACE", font=self.F(9, "bold"), bg=SIDEBAR, fg=MUTED,
                 anchor="w").pack(fill="x", padx=22, pady=(0, 6))

        self.nav_buttons = {}
        for i, name in enumerate(NAV_ITEMS):
            btn = tk.Button(
                side, text=f"0{i + 1}    {name}", anchor="w", height=2, relief="flat",
                bg=SIDEBAR, activebackground=BORDER, fg=MUTED, activeforeground=INK,
                font=self.F(11), bd=0, command=lambda n=name: self._show_page(n))
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[name] = btn

        status = tk.Frame(side, bg=SIDEBAR)
        status.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Label(status, text="●", fg=EMERALD, bg=SIDEBAR, font=self.F(10)).pack(side="left")
        tk.Label(status, text="  Sync active", fg=MUTED, bg=SIDEBAR, font=self.F(10)).pack(side="left")

        tk.Frame(self, bg=BORDER, width=1).grid(row=0, column=0, sticky="nse")

    # ───────────────────────── PAGES ─────────────────────────
    def _build_pages(self):
        self.content = tk.Frame(self, bg=CANVAS)
        self.content.grid(row=0, column=1, sticky="nsew", padx=32, pady=26)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        head = tk.Frame(self.content, bg=CANVAS)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        head.grid_columnconfigure(0, weight=1)
        
        self.title_lbl = tk.Label(head, text="Dashboard", font=self.F(20, "bold"),
                                  bg=CANVAS, fg=INK, anchor="w")
        self.title_lbl.grid(row=0, column=0, sticky="w")
        
        current_date_str = datetime.now().strftime("%A, %d %B %Y").upper()
        self.date_lbl = tk.Label(head, text=current_date_str,
                                 font=self.F(10, "bold"), bg=CANVAS, fg=MUTED)
        self.date_lbl.grid(row=0, column=1, sticky="e")

        self.pages = {}
        self.pages["Dashboard"] = tk.Frame(self.content, bg=CANVAS)
        self.pages["Dashboard"].grid_columnconfigure(0, weight=1)
        self.pages["Dashboard"].grid_rowconfigure(1, weight=5)
        self.pages["Dashboard"].grid_rowconfigure(2, weight=3)
        self._build_stats(self.pages["Dashboard"])
        self._build_workspace(self.pages["Dashboard"])
        self._build_feed(self.pages["Dashboard"])

        self.pages["Deep Work"] = self._build_deep_work_page()
        self.pages["Analytics"] = self._build_analytics_page()
        self.pages["Flow State"] = self._build_flow_state_page()
        self.pages["Settings"] = self._build_settings_page()

    def _show_page(self, name):
        self.active_nav = name
        for n, b in self.nav_buttons.items():
            active = n == name
            b.configure(bg=SURFACE if active else SIDEBAR,
                        fg=COBALT if active else MUTED,
                        font=self.F(11, "bold" if active else "normal"))
        self.title_lbl.configure(text=name)
        
        for p_name, p_frame in self.pages.items():
            if p_name == name:
                p_frame.grid(row=1, column=0, sticky="nsew")
            else:
                p_frame.grid_remove()

    # ───────────────────────── STAT CARDS ─────────────────────────
    def _build_stats(self, parent):
        row = tk.Frame(parent, bg=CANVAS)
        row.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        specs = [
            ("focus", "FOCUS SCORE", "94.2%", "▲ 2.1 pts vs yesterday", EMERALD),
            ("deep", "DEEP WORK HOURS", "6h 42m", "▲ 38m above weekly avg", EMERALD),
            ("velocity", "TASK VELOCITY", "+18%", "vs last week", COBALT),
            ("load", "COGNITIVE LOAD INDEX", "Optimal", "Within sustainable range", EMERALD),
        ]
        self.stat = {}
        for i, (key, label, value, sub, colour) in enumerate(specs):
            row.grid_columnconfigure(i, weight=1, uniform="stat")
            c = card(row)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            tk.Label(c, text=label, font=self.F(9, "bold"), bg=SURFACE, fg=MUTED, anchor="w").pack(fill="x", padx=18, pady=(16, 0))
            v = tk.Label(c, text=value, font=self.F(22, "bold"), bg=SURFACE, fg=INK, anchor="w")
            v.pack(fill="x", padx=18, pady=(2, 0))
            s = tk.Label(c, text=sub, font=self.F(10), bg=SURFACE, fg=colour, anchor="w")
            s.pack(fill="x", padx=18, pady=(0, 16))
            self.stat[key] = (v, s)

    # ───────────────────────── WORKSPACE ─────────────────────────
    def _build_workspace(self, parent):
        ws = tk.Frame(parent, bg=CANVAS)
        ws.grid(row=1, column=0, sticky="nsew", pady=(0, 16))
        ws.grid_rowconfigure(0, weight=1)
        ws.grid_columnconfigure(0, weight=5, uniform="ws")
        ws.grid_columnconfigure(1, weight=3, uniform="ws", minsize=330)
        self._build_chart(ws)
        self._build_timer(ws)

    def _build_chart(self, parent):
        c = card(parent)
        c.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)

        top = tk.Frame(c, bg=SURFACE)
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        top.grid_columnconfigure(0, weight=1)
        titles = tk.Frame(top, bg=SURFACE)
        titles.grid(row=0, column=0, sticky="w")
        tk.Label(titles, text="Weekly Output Velocity", font=self.F(13, "bold"), bg=SURFACE, fg=INK, anchor="w").pack(anchor="w")
        tk.Label(titles, text="Composite output index · hover for values", font=self.F(9), bg=SURFACE, fg=MUTED, anchor="w").pack(anchor="w")
        
        seg_frame = tk.Frame(top, bg=SURFACE)
        seg_frame.grid(row=0, column=1, sticky="e")
        self.btn_7d = tk.Button(seg_frame, text="7D", font=self.F(10, "bold"), bg=COBALT_TINT, fg=COBALT, relief="flat", bd=0, width=5, command=lambda: self._set_chart_range("7D"))
        self.btn_7d.pack(side="left", padx=2)
        self.btn_30d = tk.Button(seg_frame, text="30D", font=self.F(10), bg=SIDEBAR, fg=INK, relief="flat", bd=0, width=5, command=lambda: self._set_chart_range("30D"))
        self.btn_30d.pack(side="left", padx=2)

        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor=SURFACE, constrained_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=c)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=SURFACE, highlightthickness=0)
        widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 10))
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.canvas.mpl_connect("axes_leave_event", lambda e: self._hide_tip())
        self._draw_chart("7D")

    def _set_chart_range(self, rng):
        self.active_range = rng
        if rng == "7D":
            self.btn_7d.configure(bg=COBALT_TINT, fg=COBALT, font=self.F(10, "bold"))
            self.btn_30d.configure(bg=SIDEBAR, fg=INK, font=self.F(10))
        else:
            self.btn_30d.configure(bg=COBALT_TINT, fg=COBALT, font=self.F(10, "bold"))
            self.btn_7d.configure(bg=SIDEBAR, fg=INK, font=self.F(10))
        self._draw_chart(rng)

    def _draw_chart(self, rng="7D"):
        week = rng == "7D"
        cur, prev = (WEEK_CUR, WEEK_PREV) if week else (MONTH_CUR, MONTH_PREV)
        self.labels = WEEK if week else [f"Day {i + 1}" for i in range(30)]
        self.cur = cur
        x = list(range(len(cur)))
        ax = self.ax
        ax.clear()
        ax.set_facecolor(SURFACE)
        ax.plot(x, prev, color="#94A3B8", lw=1.4, ls="--", label="Previous period")
        ax.plot(x, cur, color=COBALT, lw=2.4, solid_capstyle="round", label="Current period")
        ax.fill_between(x, cur, 40, color=COBALT, alpha=0.07, lw=0)
        ax.set_ylim(40, 100)
        ax.set_xlim(-0.3, len(cur) - 0.7)
        ticks = x if week else x[::5]
        ax.set_xticks(ticks)
        ax.set_xticklabels([self.labels[i] if week else str(i + 1) for i in ticks])
        ax.set_yticks([40, 55, 70, 85, 100])
        ax.tick_params(colors=MUTED, labelsize=9, length=0, pad=6)
        ax.grid(axis="y", color=BORDER, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(BORDER)
        leg = ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=2)
        for t in leg.get_texts():
            t.set_color(MUTED)
        self.dot, = ax.plot([], [], "o", ms=8, mfc=SURFACE, mec=COBALT, mew=2.2, zorder=5)
        self.tip = ax.annotate("", xy=(0, 0), xytext=(0, 16), textcoords="offset points",
                               ha="center", fontsize=9, color=INK, visible=False,
                               bbox=dict(boxstyle="round,pad=0.4", fc=SURFACE, ec=BORDER, lw=1))
        self.canvas.draw_idle()

    def _on_hover(self, ev):
        if ev.inaxes is not self.ax or ev.xdata is None:
            return self._hide_tip()
        i = min(max(int(round(ev.xdata)), 0), len(self.cur) - 1)
        self.dot.set_data([i], [self.cur[i]])
        self.tip.xy = (i, self.cur[i])
        self.tip.set_text(f"{self.labels[i]} · {self.cur[i]} pts")
        self.tip.set_visible(True)
        self.canvas.draw_idle()

    def _hide_tip(self):
        if hasattr(self, 'tip') and self.tip.get_visible():
            self.tip.set_visible(False)
            self.dot.set_data([], [])
            self.canvas.draw_idle()

    # ───────────────────────── FOCUS TIMER ─────────────────────────
    def _build_timer(self, parent):
        c = card(parent)
        c.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(6, weight=1)

        hdr = tk.Frame(c, bg=SURFACE)
        hdr.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        hdr.grid_columnconfigure(0, weight=1)
        tk.Label(hdr, text="Focus Session", font=self.F(13, "bold"), bg=SURFACE, fg=INK, anchor="w").grid(row=0, column=0, sticky="w")
        self.status_lbl = tk.Label(hdr, text=" IDLE ", font=self.F(9, "bold"), fg=MUTED, bg=SIDEBAR)
        self.status_lbl.grid(row=0, column=1, sticky="e")

        dur_frame = tk.Frame(c, bg=SURFACE)
        dur_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(12, 0))
        dur_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.btn_25 = tk.Button(dur_frame, text="25 min", font=self.F(10), bg=COBALT_TINT, fg=COBALT, relief="flat", bd=0, command=lambda: self._set_duration("25 min"))
        self.btn_25.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_50 = tk.Button(dur_frame, text="50 min", font=self.F(10), bg=SIDEBAR, fg=INK, relief="flat", bd=0, command=lambda: self._set_duration("50 min"))
        self.btn_50.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_90 = tk.Button(dur_frame, text="90 min", font=self.F(10), bg=SIDEBAR, fg=INK, relief="flat", bd=0, command=lambda: self._set_duration("90 min"))
        self.btn_90.grid(row=0, column=2, sticky="ew", padx=2)

        self.time_lbl = tk.Label(c, text="25:00", font=self.F(38, "bold"), bg=SURFACE, fg=INK)
        self.time_lbl.grid(row=2, column=0, pady=(8, 0))
        
        self.progress = ttk.Progressbar(c, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=3, column=0, sticky="ew", padx=18, pady=(2, 12))

        btns = tk.Frame(c, bg=SURFACE)
        btns.grid(row=4, column=0, sticky="ew", padx=18)
        btns.grid_columnconfigure((0, 1), weight=1)
        self.start_btn = tk.Button(btns, text="Start Session", font=self.F(11, "bold"), bg=COBALT, fg="#FFFFFF", relief="flat", bd=0, height=2, command=self._toggle)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Button(btns, text="Reset", font=self.F(11), bg=SURFACE, fg=INK, highlightbackground=BORDER, highlightthickness=1, relief="flat", bd=0, height=2, command=self._reset).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.accel_var = tk.BooleanVar(value=False)
        accel_chk = tk.Checkbutton(c, text="Accelerated simulation (60×)", variable=self.accel_var, font=self.F(10), bg=SURFACE, fg=MUTED, activebackground=SURFACE, bd=0)
        accel_chk.grid(row=5, column=0, sticky="w", padx=18, pady=(10, 6))

        self.log_box = tk.Text(c, bg=CANVAS, fg=INK, highlightbackground=BORDER, highlightthickness=1, font=self.mono, height=5, wrap="word", bd=0)
        self.log_box.grid(row=6, column=0, sticky="nsew", padx=18, pady=(0, 16))
        self.log_box.configure(state="disabled")

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{datetime.now():%H:%M:%S}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, fg, bg):
        self.status_lbl.configure(text=f" {text} ", fg=fg, bg=bg)

    def _set_duration(self, value):
        self.active_duration = value
        for b, val in [(self.btn_25, "25 min"), (self.btn_50, "50 min"), (self.btn_90, "90 min")]:
            if val == value:
                b.configure(bg=COBALT_TINT, fg=COBALT, font=self.F(10, "bold"))
            else:
                b.configure(bg=SIDEBAR, fg=INK, font=self.F(10))
        self.total = int(value.split()[0]) * 60
        self.remaining = self.total
        self._update_display()
        self._log(f"Duration set to {value}.")

    def _toggle(self):
        if self.running:
            self.running = False
            self.after_cancel(self.jobs.pop("tick"))
            self.start_btn.configure(text="Resume", bg=COBALT)
            self._set_status("PAUSED", AMBER, "#FFFBEB")
            self._log(f"Paused at {self._fmt(self.remaining)}.")
            return
        if self.remaining <= 0:
            self.remaining = self.total
        self.running = True
        self.start_btn.configure(text="Pause", bg=AMBER)
        self._set_status("RUNNING", "#047857", "#ECFDF5")
        self._log(f"Session #{self.session_no} started ({self.total // 60} min).")
        self.jobs["tick"] = self.after(1000, self._tick)

    def _tick(self):
        self.remaining = max(0, self.remaining - (60 if self.accel_var.get() else 1))
        self._update_display()
        if self.remaining == 0:
            return self._complete()
        self.jobs["tick"] = self.after(1000, self._tick)

    def _complete(self):
        self.running = False
        self.jobs.pop("tick", None)
        mins = self.total // 60
        self.start_btn.configure(text="Start Session", bg=COBALT)
        self._set_status("COMPLETE", "#047857", "#ECFDF5")
        self._log(f"Session #{self.session_no} complete. +{mins}m deep work.")
        self.feed.insert(0, (f"Focus Block #{self.session_no}", "Session", "Deep Work",
                             f"{mins}m", datetime.now().strftime("%H:%M")))
        self.session_no += 1
        self.deep_minutes += mins
        h, m = divmod(self.deep_minutes, 60)
        self.stat["deep"][0].configure(text=f"{h}h {m:02d}m")
        self._render_feed()

    def _reset(self):
        if "tick" in self.jobs:
            self.after_cancel(self.jobs.pop("tick"))
        self.running = False
        self.remaining = self.total
        self.start_btn.configure(text="Start Session", bg=COBALT)
        self._set_status("IDLE", MUTED, SIDEBAR)
        self._update_display()
        self._log("Session reset.")

    @staticmethod
    def _fmt(sec):
        return f"{sec // 60:02d}:{sec % 60:02d}"

    def _update_display(self):
        self.time_lbl.configure(text=self._fmt(self.remaining))
        ratio = (1 - self.remaining / self.total) * 100
        self.progress['value'] = ratio
        load, sub = self.stat["load"]
        if self.running and (1 - self.remaining / self.total) > 0.8:
            load.configure(text="Elevated")
            sub.configure(text="Consider a recovery break", fg=AMBER)
        else:
            load.configure(text="Optimal")
            sub.configure(text="Within sustainable range", fg=EMERALD)

    # ───────────────────────── ACTIVITY FEED ─────────────────────────
    def _build_feed(self, parent):
        c = card(parent)
        c.grid(row=2, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)
        tk.Label(c, text="Recent Deep Work Blocks", font=self.F(13, "bold"), bg=SURFACE, fg=INK, anchor="w").grid(row=0, column=0, sticky="w", padx=18, pady=(14, 6))
        
        self.feed_frame = tk.Frame(c, bg=SURFACE)
        self.feed_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 10))
        for i, w in enumerate((5, 3, 2, 2, 2)):
            self.feed_frame.grid_columnconfigure(i, weight=w)
        self._render_feed()

    def _render_feed(self):
        f = self.feed_frame
        for w in f.winfo_children():
            w.destroy()
        heads = ["BLOCK", "PROJECT", "TYPE", "DURATION", "COMPLETED"]
        for i, h in enumerate(heads):
            tk.Label(f, text=h, font=self.F(9, "bold"), bg=SURFACE, fg=MUTED, anchor="w").grid(row=0, column=i, sticky="ew", padx=4, pady=(0, 6))
        for r, (block, project, kind, dur, ts) in enumerate(self.feed[:5], start=1):
            tk.Frame(f, bg=BORDER, height=1).grid(row=r * 2 - 1, column=0, columnspan=5, sticky="ew")
            gr = r * 2
            tk.Label(f, text=block, font=self.F(10, "bold"), bg=SURFACE, fg=INK, anchor="w").grid(row=gr, column=0, sticky="ew", padx=4, pady=6)
            tk.Label(f, text=project, font=self.F(10), bg=SURFACE, fg=MUTED, anchor="w").grid(row=gr, column=1, sticky="ew", padx=4)
            bg_col, fg_col = TAG_STYLES.get(kind, TAG_STYLES["Shallow"])
            lbl_tag = tk.Label(f, text=f" {kind} ", font=self.F(9, "bold"), bg=bg_col, fg=fg_col)
            lbl_tag.grid(row=gr, column=2, sticky="w", padx=4)
            tk.Label(f, text=dur, font=self.F(10), bg=SURFACE, fg=INK, anchor="w").grid(row=gr, column=3, sticky="ew", padx=4)
            tk.Label(f, text=ts, font=self.F(10), bg=SURFACE, fg=MUTED, anchor="w").grid(row=gr, column=4, sticky="ew", padx=4)

    # ───────────────────────── ADDITIONAL PAGES ─────────────────────────
    def _build_deep_work_page(self):
        p = tk.Frame(self.content, bg=CANVAS)
        p.grid_columnconfigure((0, 1), weight=1)
        p.grid_rowconfigure(0, weight=1)

        c_left = card(p)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c_left, text="Deep Work Allocation", font=self.F(14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(c_left, text="Manage daily allocation targets by project stream.", font=self.F(10), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        for proj, time_str, val in [("Backend Infrastructure", "3h 15m", 75), ("Frontend Architecture", "2h 00m", 50), ("API Schema Design", "1h 30m", 35)]:
            row = tk.Frame(c_left, bg=SURFACE)
            row.pack(fill="x", padx=20, pady=5)
            tk.Label(row, text=proj, font=self.F(11, "bold"), bg=SURFACE, fg=INK).pack(side="left")
            tk.Label(row, text=time_str, font=self.F(11), bg=SURFACE, fg=MUTED).pack(side="right")
            bar = ttk.Progressbar(c_left, orient="horizontal", length=100, mode="determinate", value=val)
            bar.pack(fill="x", padx=20, pady=(0, 15))

        c_right = card(p)
        c_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c_right, text="Distraction Shield", font=self.F(14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(c_right, text="Automated OS-level notification blocking during deep blocks.", font=self.F(10), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        for label, default in [("Block Slack & Mail Notifications", True), ("Mute Background Messengers", True), ("Enable Ambient Focus Soundscape", True)]:
            var = tk.BooleanVar(value=default)
            tk.Checkbutton(c_right, text=label, variable=var, font=self.F(11), bg=SURFACE, fg=INK, activebackground=SURFACE, bd=0).pack(anchor="w", padx=20, pady=10)

        return p

    def _build_analytics_page(self):
        p = tk.Frame(self.content, bg=CANVAS)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        c = card(p)
        c.grid(row=0, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)

        tk.Label(c, text="Deep Dive Performance Metrics", font=self.F(14, "bold"), bg=SURFACE, fg=INK).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        fig = Figure(figsize=(10, 4), dpi=100, facecolor=SURFACE, constrained_layout=True)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ax.bar(days, [4.5, 5.2, 3.8, 6.5, 5.9, 7.2, 6.8], color=COBALT, width=0.5, alpha=0.85)
        ax.set_ylabel("Deep Work Hours", color=MUTED, fontsize=10)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.grid(axis="y", color=BORDER, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_color(BORDER)
        ax.spines["bottom"].set_color(BORDER)

        canvas = FigureCanvasTkAgg(fig, master=c)
        widget = canvas.get_tk_widget()
        widget.configure(bg=SURFACE, highlightthickness=0)
        widget.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        return p

    def _build_flow_state_page(self):
        p = tk.Frame(self.content, bg=CANVAS)
        p.grid_columnconfigure((0, 1), weight=1)
        p.grid_rowconfigure(0, weight=1)

        c_left = card(p)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c_left, text="Flow State Telemetry", font=self.F(14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(c_left, text="Real-time neural and physiological synchronization.", font=self.F(10), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        for title, val, sub in [("Heart Rate Variability (HRV)", "78 ms", "Optimal variance"), ("Cognitive Tempo", "1.24 GHz-equiv", "High peak synchronization"), ("Alpha Wave Density", "64.2%", "Deep immersion zone")]:
            box = tk.Frame(c_left, bg=CANVAS, highlightbackground=BORDER, highlightthickness=1)
            box.pack(fill="x", padx=20, pady=6)
            tk.Label(box, text=title, font=self.F(9, "bold"), bg=CANVAS, fg=MUTED).pack(anchor="w", padx=12, pady=(8, 0))
            tk.Label(box, text=val, font=self.F(16, "bold"), bg=CANVAS, fg=INK).pack(anchor="w", padx=12, pady=2)
            tk.Label(box, text=sub, font=self.F(9), bg=CANVAS, fg=EMERALD).pack(anchor="w", padx=12, pady=(0, 8))

        c_right = card(p)
        c_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c_right, text="Acoustic Enclosures", font=self.F(14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(c_right, text="Select neural entrainment soundscape frequencies.", font=self.F(10), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        for title, desc in [("Brown Noise (Deep Focus)", "Optimized for sustained architectural tasks"), ("Alpha Binaural Beats (10 Hz)", "Enhances creative problem-solving output")]:
            row = tk.Frame(c_right, bg=SURFACE)
            row.pack(fill="x", padx=20, pady=10)
            lbl_frame = tk.Frame(row, bg=SURFACE)
            lbl_frame.pack(side="left", fill="x", expand=True)
            tk.Label(lbl_frame, text=title, font=self.F(11, "bold"), bg=SURFACE, fg=INK, anchor="w").pack(anchor="w")
            tk.Label(lbl_frame, text=desc, font=self.F(9), bg=SURFACE, fg=MUTED, anchor="w").pack(anchor="w")
            tk.Button(row, text="Activate", font=self.F(10, "bold"), bg=COBALT, fg="#FFFFFF", relief="flat", bd=0, width=8).pack(side="right")

        return p

    def _build_settings_page(self):
        p = tk.Frame(self.content, bg=CANVAS)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        c = card(p)
        c.grid(row=0, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)

        tk.Label(c, text="Application Preferences", font=self.F(14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(c, text="Customize appearance, telemetry sync frequency, and core system parameters.", font=self.F(10), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 20))

        for label, default in [("Start MOMENTUM on System Boot", True), ("Enable Hardware Acceleration via GPU", True), ("Automatic Cloud Telemetry Sync", False)]:
            var = tk.BooleanVar(value=default)
            tk.Checkbutton(c, text=label, variable=var, font=self.F(11), bg=SURFACE, fg=INK, activebackground=SURFACE, bd=0).pack(anchor="w", padx=20, pady=10)

        btn_row = tk.Frame(c, bg=SURFACE)
        btn_row.pack(anchor="w", padx=20, pady=30)
        tk.Button(btn_row, text="Save Preferences", font=self.F(11, "bold"), bg=COBALT, fg="#FFFFFF", relief="flat", bd=0, height=2, width=15).pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="Reset Defaults", font=self.F(11), bg=SURFACE, fg=INK, highlightbackground=BORDER, highlightthickness=1, relief="flat", bd=0, height=2, width=15).pack(side="left")

        return p

    # ───────────────────────── LIVE METRICS ─────────────────────────
    def _schedule_live_metrics(self):
        drift = random.uniform(-0.4, 0.4) + (0.15 if self.running else 0)
        self.focus_score = min(98.0, max(90.0, self.focus_score + drift))
        self.stat["focus"][0].configure(text=f"{self.focus_score:.1f}%")
        self.jobs["live"] = self.after(3500, self._schedule_live_metrics)

    def _on_close(self):
        for job in self.jobs.values():
            try:
                self.after_cancel(job)
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    MomentumApp().mainloop()