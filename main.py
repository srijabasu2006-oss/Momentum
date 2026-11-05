"""
MOMENTUM // v2.4  —  Productivity Analytics Dashboard
Light-mode desktop app built with customtkinter + matplotlib.

Install:  pip install customtkinter matplotlib
Run:      python main.py
"""
import random
import tkinter.font as tkfont
from datetime import datetime

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ───────────────────────── DESIGN TOKENS ─────────────────────────
CANVAS, SURFACE, SIDEBAR = "#F8F9FC", "#FFFFFF", "#F1F5F9"
BORDER, INK, MUTED = "#E2E8F0", "#0F172A", "#64748B"
COBALT, COBALT_HOVER, COBALT_TINT = "#2563EB", "#1D4ED8", "#DBEAFE"
EMERALD, AMBER, AMBER_HOVER = "#10B981", "#D97706", "#B45309"

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
    return ctk.CTkFrame(parent, fg_color=SURFACE, border_color=BORDER,
                        border_width=1, corner_radius=10, **kw)


class MomentumApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=CANVAS)
        self.title("MOMENTUM // v2.4")
        self.geometry("1320x840")
        self.minsize(1120, 720)

        fam = pick_font(self)
        self.F = lambda size, weight="normal": ctk.CTkFont(family=fam, size=size, weight=weight)
        self.mono = ctk.CTkFont(family="Consolas" if "Consolas" in set(tkfont.families(self))
                                else "Courier New", size=12)

        # state
        self.jobs = {}
        self.feed = list(SEED_FEED)
        self.deep_minutes = 402          # 6h 42m
        self.focus_score = 94.2
        self.total = 25 * 60
        self.remaining = self.total
        self.running = False
        self.session_no = 1

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
        side = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=0, width=232)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)
        side.grid_rowconfigure(8, weight=1)

        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 22))
        ctk.CTkLabel(brand, text="MOMENTUM", font=self.F(18, "bold"),
                     text_color=INK).pack(side="left")
        ctk.CTkLabel(brand, text="  // v2.4", font=self.F(12),
                     text_color=MUTED).pack(side="left", pady=(3, 0))

        ctk.CTkLabel(side, text="WORKSPACE", font=self.F(10, "bold"), text_color=MUTED,
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 6))

        self.nav_buttons = {}
        for i, name in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                side, text=f"0{i + 1}    {name}", anchor="w", height=38, corner_radius=8,
                fg_color="transparent", hover_color=BORDER, text_color=MUTED,
                border_width=0, border_color=BORDER, font=self.F(13),
                command=lambda n=name: self._show_page(n))
            btn.grid(row=2 + i, column=0, sticky="ew", padx=12, pady=2)
            self.nav_buttons[name] = btn

        status = ctk.CTkFrame(side, fg_color="transparent")
        status.grid(row=9, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(status, text="●", text_color=EMERALD, font=self.F(11)).pack(side="left")
        ctk.CTkLabel(status, text="  Sync active", text_color=MUTED,
                     font=self.F(12)).pack(side="left")

        ctk.CTkFrame(self, fg_color=BORDER, width=1, corner_radius=0).grid(
            row=0, column=0, sticky="nse")

    # ───────────────────────── PAGES ─────────────────────────
    def _build_pages(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=32, pady=26)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(self.content, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        head.grid_columnconfigure(0, weight=1)
        
        self.title_lbl = ctk.CTkLabel(head, text="Dashboard", font=self.F(24, "bold"),
                                     text_color=INK, anchor="w")
        self.title_lbl.grid(row=0, column=0, sticky="w")
        
        # Dynamic, aesthetic date indicator
        current_date_str = datetime.now().strftime("%A, %d %B %Y").upper()
        self.date_lbl = ctk.CTkLabel(head, text=current_date_str,
                                     font=self.F(11, "bold"), text_color=MUTED)
        self.date_lbl.grid(row=0, column=1, sticky="e")

        # Container for pages
        self.pages = {}

        # 1. Dashboard Page
        self.pages["Dashboard"] = ctk.CTkFrame(self.content, fg_color="transparent")
        self.pages["Dashboard"].grid_columnconfigure(0, weight=1)
        self.pages["Dashboard"].grid_rowconfigure(1, weight=5, minsize=300)
        self.pages["Dashboard"].grid_rowconfigure(2, weight=3, minsize=190)
        self._build_stats(self.pages["Dashboard"])
        self._build_workspace(self.pages["Dashboard"])
        self._build_feed(self.pages["Dashboard"])

        # 2. Deep Work Page
        self.pages["Deep Work"] = self._build_deep_work_page()

        # 3. Analytics Page
        self.pages["Analytics"] = self._build_analytics_page()

        # 4. Flow State Page
        self.pages["Flow State"] = self._build_flow_state_page()

        # 5. Settings Page
        self.pages["Settings"] = self._build_settings_page()

    def _show_page(self, name):
        for n, b in self.nav_buttons.items():
            active = n == name
            b.configure(fg_color=SURFACE if active else "transparent",
                        text_color=COBALT if active else MUTED,
                        border_width=1 if active else 0,
                        font=self.F(13, "bold" if active else "normal"))
        self.title_lbl.configure(text=name)
        
        for p_name, p_frame in self.pages.items():
            if p_name == name:
                p_frame.grid(row=1, column=0, sticky="nsew")
            else:
                p_frame.grid_remove()

    # ───────────────────────── STAT CARDS ─────────────────────────
    def _build_stats(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
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
            ctk.CTkLabel(c, text=label, font=self.F(10, "bold"), text_color=MUTED,
                         anchor="w").pack(fill="x", padx=18, pady=(16, 0))
            v = ctk.CTkLabel(c, text=value, font=self.F(28, "bold"),
                           text_color=INK, anchor="w")
            v.pack(fill="x", padx=18, pady=(2, 0))
            s = ctk.CTkLabel(c, text=sub, font=self.F(12), text_color=colour, anchor="w")
            s.pack(fill="x", padx=18, pady=(0, 16))
            self.stat[key] = (v, s)

    # ───────────────────────── WORKSPACE ─────────────────────────
    def _build_workspace(self, parent):
        ws = ctk.CTkFrame(parent, fg_color="transparent")
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

        top = ctk.CTkFrame(c, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        top.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(top, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="Weekly Output Velocity", font=self.F(15, "bold"),
                     text_color=INK, anchor="w").pack(anchor="w")
        ctk.CTkLabel(titles, text="Composite output index · hover for values",
                     font=self.F(11), text_color=MUTED, anchor="w").pack(anchor="w")
        self.range_seg = ctk.CTkSegmentedButton(
            top, values=["7D", "30D"], command=self._draw_chart, height=28,
            selected_color=COBALT_TINT, selected_hover_color=COBALT_TINT,
            unselected_color=SIDEBAR, unselected_hover_color=BORDER,
            text_color=INK, fg_color=SIDEBAR, font=self.F(12, "bold"))
        self.range_seg.set("7D")
        self.range_seg.grid(row=0, column=1, sticky="e")

        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor=SURFACE, constrained_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=c)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=SURFACE, highlightthickness=0)
        widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 10))
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.canvas.mpl_connect("axes_leave_event", lambda e: self._hide_tip())
        self._draw_chart("7D")

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
        if self.tip.get_visible():
            self.tip.set_visible(False)
            self.dot.set_data([], [])
            self.canvas.draw_idle()

    # ───────────────────────── FOCUS TIMER ─────────────────────────
    def _build_timer(self, parent):
        c = card(parent)
        c.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(6, weight=1)

        hdr = ctk.CTkFrame(c, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Focus Session", font=self.F(15, "bold"),
                     text_color=INK, anchor="w").grid(row=0, column=0, sticky="w")
        self.status_lbl = ctk.CTkLabel(hdr, text=" IDLE ", font=self.F(10, "bold"),
                                       text_color=MUTED, fg_color=SIDEBAR,
                                       corner_radius=4, height=20)
        self.status_lbl.grid(row=0, column=1, sticky="e")

        self.dur_seg = ctk.CTkSegmentedButton(
            c, values=["25 min", "50 min", "90 min"], command=self._set_duration, height=28,
            selected_color=COBALT_TINT, selected_hover_color=COBALT_TINT,
            unselected_color=SIDEBAR, unselected_hover_color=BORDER,
            text_color=INK, fg_color=SIDEBAR, font=self.F(12))
        self.dur_seg.set("25 min")
        self.dur_seg.grid(row=1, column=0, sticky="ew", padx=18, pady=(12, 0))

        self.time_lbl = ctk.CTkLabel(c, text="25:00", font=self.F(46, "bold"), text_color=INK)
        self.time_lbl.grid(row=2, column=0, pady=(8, 0))
        self.progress = ctk.CTkProgressBar(c, height=6, corner_radius=3, fg_color=BORDER,
                                           progress_color=COBALT)
        self.progress.set(0)
        self.progress.grid(row=3, column=0, sticky="ew", padx=18, pady=(2, 12))

        btns = ctk.CTkFrame(c, fg_color="transparent")
        btns.grid(row=4, column=0, sticky="ew", padx=18)
        btns.grid_columnconfigure((0, 1), weight=1, uniform="b")
        self.start_btn = ctk.CTkButton(btns, text="Start Session", height=38, corner_radius=8,
                                       fg_color=COBALT, hover_color=COBALT_HOVER,
                                       text_color="#FFFFFF", font=self.F(13, "bold"),
                                       command=self._toggle)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(btns, text="Reset", height=38, corner_radius=8, fg_color=SURFACE,
                      hover_color=SIDEBAR, text_color=INK, border_width=1,
                      border_color=BORDER, font=self.F(13), command=self._reset
                      ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.accel = ctk.CTkSwitch(c, text="Accelerated simulation (60×)", font=self.F(11),
                                   text_color=MUTED, progress_color=COBALT, height=18,
                                   switch_width=34, switch_height=16)
        self.accel.grid(row=5, column=0, sticky="w", padx=18, pady=(10, 6))

        self.log_box = ctk.CTkTextbox(c, fg_color=CANVAS, text_color=INK, border_width=1,
                                      border_color=BORDER, corner_radius=8, font=self.mono,
                                      height=70, state="disabled", wrap="word")
        self.log_box.grid(row=6, column=0, sticky="nsew", padx=18, pady=(0, 16))

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{datetime.now():%H:%M:%S}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, fg, bg):
        self.status_lbl.configure(text=f" {text} ", text_color=fg, fg_color=bg)

    def _set_duration(self, value):
        self.total = int(value.split()[0]) * 60
        self.remaining = self.total
        self._update_display()
        self._log(f"Duration set to {value}.")

    def _toggle(self):
        if self.running:
            self.running = False
            self.after_cancel(self.jobs.pop("tick"))
            self.start_btn.configure(text="Resume", fg_color=COBALT, hover_color=COBALT_HOVER)
            self._set_status("PAUSED", AMBER, "#FFFBEB")
            self._log(f"Paused at {self._fmt(self.remaining)}.")
            return
        if self.remaining <= 0:
            self.remaining = self.total
        self.running = True
        self.dur_seg.configure(state="disabled")
        self.start_btn.configure(text="Pause", fg_color=AMBER, hover_color=AMBER_HOVER)
        self._set_status("RUNNING", "#047857", "#ECFDF5")
        self._log(f"Session #{self.session_no} started ({self.total // 60} min).")
        self.jobs["tick"] = self.after(1000, self._tick)

    def _tick(self):
        self.remaining = max(0, self.remaining - (60 if self.accel.get() else 1))
        self._update_display()
        if self.remaining == 0:
            return self._complete()
        self.jobs["tick"] = self.after(1000, self._tick)

    def _complete(self):
        self.running = False
        self.jobs.pop("tick", None)
        mins = self.total // 60
        self.dur_seg.configure(state="normal")
        self.start_btn.configure(text="Start Session", fg_color=COBALT, hover_color=COBALT_HOVER)
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
        self.dur_seg.configure(state="normal")
        self.start_btn.configure(text="Start Session", fg_color=COBALT, hover_color=COBALT_HOVER)
        self._set_status("IDLE", MUTED, SIDEBAR)
        self._update_display()
        self._log("Session reset.")

    @staticmethod
    def _fmt(sec):
        return f"{sec // 60:02d}:{sec % 60:02d}"

    def _update_display(self):
        self.time_lbl.configure(text=self._fmt(self.remaining))
        ratio = 1 - self.remaining / self.total
        self.progress.set(ratio)
        load, sub = self.stat["load"]
        if self.running and ratio > 0.8:
            load.configure(text="Elevated")
            sub.configure(text="Consider a recovery break", text_color=AMBER)
        else:
            load.configure(text="Optimal")
            sub.configure(text="Within sustainable range", text_color=EMERALD)

    # ───────────────────────── ACTIVITY FEED ─────────────────────────
    def _build_feed(self, parent):
        c = card(parent)
        c.grid(row=2, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(c, text="Recent Deep Work Blocks", font=self.F(15, "bold"),
                     text_color=INK, anchor="w").grid(row=0, column=0, sticky="w",
                                                      padx=18, pady=(14, 6))
        self.feed_frame = ctk.CTkScrollableFrame(
            c, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color="#CBD5E1")
        self.feed_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=(0, 10))
        for i, w in enumerate((5, 3, 2, 2, 2)):
            self.feed_frame.grid_columnconfigure(i, weight=w)
        self._render_feed()

    def _render_feed(self):
        f = self.feed_frame
        for w in f.winfo_children():
            w.destroy()
        heads = ["BLOCK", "PROJECT", "TYPE", "DURATION", "COMPLETED"]
        for i, h in enumerate(heads):
            ctk.CTkLabel(f, text=h, font=self.F(10, "bold"), text_color=MUTED,
                         anchor="w").grid(row=0, column=i, sticky="ew", padx=8, pady=(0, 6))
        for r, (block, project, kind, dur, ts) in enumerate(self.feed[:30], start=1):
            ctk.CTkFrame(f, fg_color=BORDER, height=1, corner_radius=0).grid(
                row=r * 2 - 1, column=0, columnspan=5, sticky="ew")
            gr = r * 2
            ctk.CTkLabel(f, text=block, font=self.F(13, "bold"), text_color=INK,
                         anchor="w").grid(row=gr, column=0, sticky="ew", padx=8, pady=7)
            ctk.CTkLabel(f, text=project, font=self.F(13), text_color=MUTED,
                         anchor="w").grid(row=gr, column=1, sticky="ew", padx=8)
            bg, fg = TAG_STYLES.get(kind, TAG_STYLES["Shallow"])
            ctk.CTkLabel(f, text=f" {kind} ", font=self.F(11, "bold"), text_color=fg,
                         fg_color=bg, corner_radius=4, height=22).grid(
                row=gr, column=2, sticky="w", padx=8)
            ctk.CTkLabel(f, text=dur, font=self.F(13), text_color=INK,
                         anchor="w").grid(row=gr, column=3, sticky="ew", padx=8)
            ctk.CTkLabel(f, text=ts, font=self.F(13), text_color=MUTED,
                         anchor="w").grid(row=gr, column=4, sticky="ew", padx=8)

    # ───────────────────────── ADDITIONAL PAGES ─────────────────────────
    def _build_deep_work_page(self):
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        p.grid_columnconfigure((0, 1), weight=1, uniform="dw")
        p.grid_rowconfigure(0, weight=1)

        c_left = card(p)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        c_left.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(c_left, text="Deep Work Allocation", font=self.F(16, "bold"), text_color=INK).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(c_left, text="Manage daily allocation targets by project stream.", font=self.F(12), text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        projects = [("Backend Infrastructure", "3h 15m", 0.75), ("Frontend Architecture", "2h 00m", 0.50), ("API Schema Design", "1h 30m", 0.35)]
        for proj, time_str, val in projects:
            row = ctk.CTkFrame(c_left, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(row, text=proj, font=self.F(13, "bold"), text_color=INK).pack(side="left")
            ctk.CTkLabel(row, text=time_str, font=self.F(13), text_color=MUTED).pack(side="right")
            
            bar = ctk.CTkProgressBar(c_left, height=8, corner_radius=4, fg_color=BORDER, progress_color=COBALT)
            bar.set(val)
            bar.pack(fill="x", padx=20, pady=(0, 10))

        c_right = card(p)
        c_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        c_right.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(c_right, text="Distraction Shield", font=self.F(16, "bold"), text_color=INK).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(c_right, text="Automated OS-level notification blocking during deep blocks.", font=self.F(12), text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        switches = [
            ("Block Slack & Mail Notifications", True),
            ("Mute Background Messengers", True),
            ("Lock Secondary Browser Profiles", False),
            ("Enable Ambient Focus Soundscape", True)
        ]
        for label, state in switches:
            sw = ctk.CTkSwitch(c_right, text=label, font=self.F(13), text_color=INK, progress_color=COBALT)
            if state:
                sw.select()
            sw.pack(anchor="w", padx=20, pady=12)

        return p

    def _build_analytics_page(self):
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        c = card(p)
        c.grid(row=0, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(c, text="Deep Dive Performance Metrics", font=self.F(16, "bold"), text_color=INK).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
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
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        p.grid_columnconfigure((0, 1), weight=1, uniform="fs")
        p.grid_rowconfigure(0, weight=1)

        c_left = card(p)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        ctk.CTkLabel(c_left, text="Flow State Telemetry", font=self.F(16, "bold"), text_color=INK).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(c_left, text="Real-time neural and physiological synchronization.", font=self.F(12), text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        metrics = [
            ("Heart Rate Variability (HRV)", "78 ms", "Optimal variance"),
            ("Cognitive Tempo", "1.24 GHz-equiv", "High peak synchronization"),
            ("Alpha Wave Density", "64.2%", "Deep immersion zone")
        ]
        for title, val, sub in metrics:
            box = ctk.CTkFrame(c_left, fg_color=CANVAS, corner_radius=8, border_width=1, border_color=BORDER)
            box.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(box, text=title, font=self.F(11, "bold"), text_color=MUTED).pack(anchor="w", padx=14, pady=(10, 0))
            ctk.CTkLabel(box, text=val, font=self.F(20, "bold"), text_color=INK).pack(anchor="w", padx=14, pady=2)
            ctk.CTkLabel(box, text=sub, font=self.F(11), text_color=EMERALD).pack(anchor="w", padx=14, pady=(0, 10))

        c_right = card(p)
        c_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        ctk.CTkLabel(c_right, text="Acoustic Enclosures", font=self.F(16, "bold"), text_color=INK).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(c_right, text="Select neural entrainment soundscape frequencies.", font=self.F(12), text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 20))
        
        soundscapes = [
            ("Brown Noise (Deep Focus)", "Optimized for sustained architectural tasks"),
            ("Alpha Binaural Beats (10 Hz)", "Enhances creative problem-solving output"),
            ("Isochronic Pink Waves", "Reduces cognitive fatigue latency")
        ]
        for title, desc in soundscapes:
            row = ctk.CTkFrame(c_right, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            
            lbl_frame = ctk.CTkFrame(row, fg_color="transparent")
            lbl_frame.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(lbl_frame, text=title, font=self.F(13, "bold"), text_color=INK).pack(anchor="w")
            ctk.CTkLabel(lbl_frame, text=desc, font=self.F(11), text_color=MUTED).pack(anchor="w")
            
            ctk.CTkButton(row, text="Activate", width=80, height=30, fg_color=COBALT, hover_color=COBALT_HOVER, font=self.F(11, "bold"), corner_radius=6).pack(side="right")

        return p

    def _build_settings_page(self):
        p = ctk.CTkFrame(self.content, fg_color="transparent")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        c = card(p)
        c.grid(row=0, column=0, sticky="nsew")
        c.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(c, text="Application Preferences", font=self.F(16, "bold"), text_color=INK).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(c, text="Customize appearance, telemetry sync frequency, and core system parameters.", font=self.F(12), text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 20))

        settings_items = [
            ("Start MOMENTUM on System Boot", True),
            ("Enable Hardware Acceleration via GPU", True),
            ("Automatic Cloud Telemetry Sync", False),
            ("Advanced Developer Logging Mode", True)
        ]
        for label, state in settings_items:
            sw = ctk.CTkSwitch(c, text=label, font=self.F(13), text_color=INK, progress_color=COBALT)
            if state:
                sw.select()
            sw.pack(anchor="w", padx=20, pady=12)

        btn_row = ctk.CTkFrame(c, fg_color="transparent")
        btn_row.pack(anchor="w", padx=20, pady=30)
        ctk.CTkButton(btn_row, text="Save Preferences", fg_color=COBALT, hover_color=COBALT_HOVER, font=self.F(13, "bold"), height=38, corner_radius=8).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Reset Defaults", fg_color=SURFACE, border_width=1, border_color=BORDER, text_color=INK, hover_color=SIDEBAR, font=self.F(13), height=38, corner_radius=8).pack(side="left")

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
        self.quit()
        self.destroy()


if __name__ == "__main__":
    MomentumApp().mainloop()