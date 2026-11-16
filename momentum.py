import math
import random
import sqlite3
import time
import tkinter as tk
from tkinter import messagebox, ttk

# ==============================================================================
# 1. PERSISTENT DATABASE LAYER (JDBC / SQLite Backend Schema)
# ==============================================================================
DB_FILE = "momentum_telemetry_pro.db"

def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            priority TEXT NOT NULL,
            progress INTEGER NOT NULL,
            assignee TEXT NOT NULL,
            status TEXT DEFAULT 'Active'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            module TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        sample_tasks = [
            ("Compression & planting", "High", 85, "Srija Basu", "Active"),
            ("Task A penetration", "High", 65, "A. Roy", "Active"),
            ("Task appointment track", "Medium", 40, "K. Das", "Moving"),
            ("Task managementes", "Low", 20, "M. Sen", "Idle"),
            ("Task in-competohalt", "High", 90, "Srija Basu", "Active"),
            ("Task rootsts", "Now", 55, "R. Nair", "Active"),
            ("Task loops", "Rich", 30, "D. Bose", "Offline"),
            ("Task iterate", "Rice", 75, "P. Paul", "Active"),
            ("Sprint management", "Now", 100, "Srija Basu", "Done"),
            ("Design meeting sync", "New", 45, "K. Das", "Active"),
        ]
        cursor.executemany(
            "INSERT INTO tasks (task_name, priority, progress, assignee, status) VALUES (?, ?, ?, ?, ?)",
            sample_tasks
        )

    cursor.execute("SELECT COUNT(*) FROM system_logs")
    if cursor.fetchone()[0] == 0:
        sample_logs = [
            ("13:40:12.04", "INFO", "CORE_SYNC", "JDBC connection pool initialized at 9.8 GHz velocity."),
            ("13:41:05.88", "OK", "AUTH_GATE", "Operator Srija Basu authenticated via quantum session token."),
            ("13:42:19.31", "WARN", "MEM_ALLOC", "Node-04 buffer reached 78% threshold; auto-balancing triggered."),
            ("13:43:50.12", "INFO", "PREDICT_ML", "Cognitive flow model updated with 1,420 new telemetry vectors."),
            ("13:44:22.76", "OK", "WORKFLOW", "Automated sprint deliverable pipeline executed in 14ms."),
        ]
        cursor.executemany(
            "INSERT INTO system_logs (timestamp, level, module, message) VALUES (?, ?, ?, ?)",
            sample_logs
        )
    
    conn.commit()
    conn.close()

def log_event(level, module, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    ts = time.strftime("%H:%M:%S") + f".{random.randint(10, 99)}"
    cursor.execute("INSERT INTO system_logs (timestamp, level, module, message) VALUES (?, ?, ?, ?)",
                   (ts, level, module, message))
    conn.commit()
    conn.close()

init_database()


# ==============================================================================
# 2. DESIGN TOKENS & CYBER-CYAN THEME
# ==============================================================================
THEME = {
    "bg_main": "#f9f8f6",        # Off-White Canvas
    "bg_card": "#ffffff",        # Pure White Card Surface
    "bg_sidebar": "#f6f4f0",     # Sidebar Surface
    "bg_subtle": "#ece9e1",      # Input Field Fill
    "border": "#dfdad0",         # Hairline Border
    "text_primary": "#0f172a",   # Deep Slate Ink
    "text_secondary": "#475569", # Muted Slate
    "text_muted": "#94a3b8",     # Metadata Text
    "accent_cyan": "#06b6d4",    # Cyber Cyan
    "accent_cyan_glow": "#22d3ee",# Glowing Cyan
    "accent_cyan_dark": "#0e7490",# Deep Cyan
    "accent_blue": "#2563eb",    # Telemetry Blue
    "accent_purple": "#7c3aed",  # Purple Accent
    "accent_green": "#059669",   # Success Green
    "accent_amber": "#d97706",   # Amber Warning
    "accent_red": "#dc2626",     # Critical Red
    "nav_active_bg": "#cffafe",  # Cyan Active Pill
}


# ==============================================================================
# 3. MASTER MOVING BACKGROUND CANVAS (ACTIVE ON EVERY PAGE & VIEWPORT)
# ==============================================================================
def attach_moving_background(parent_widget):
    """Attaches a living, continuously moving background canvas to any container."""
    canvas = tk.Canvas(parent_widget, bg=THEME["bg_main"], highlightthickness=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    particles = []
    for _ in range(45):
        particles.append({
            "x": random.uniform(0, 1600),
            "y": random.uniform(0, 1000),
            "vx": random.uniform(-0.65, 0.65),
            "vy": random.uniform(-0.65, 0.65),
            "radius": random.uniform(2.0, 4.8),
            "color": random.choice(["#06b6d4", "#22d3ee", "#94a3b8", "#3b82f6"])
        })
    
    grid_offset = [0.0]
    pulse_angle = [0.0]
    is_running = [True]

    def update_animation():
        if not is_running[0]:
            return
        canvas.delete("master_bg")
        w = canvas.winfo_width() or 1300
        h = canvas.winfo_height() or 850

        # 1. Scrolling architectural grid lines
        grid_offset[0] = (grid_offset[0] + 0.45) % 55
        step = 55
        for x in range(int(grid_offset[0]) - step, w + step, step):
            canvas.create_line(x, 0, x, h, fill="#f0ede4", width=1, tags="master_bg")
        for y in range(int(grid_offset[0]) - step, h + step, step):
            canvas.create_line(0, y, w, y, fill="#f0ede4", width=1, tags="master_bg")

        # 2. Pulsing cyan radar rings
        pulse_angle[0] = (pulse_angle[0] + 0.05) % (2 * math.pi)
        r_radius = 135 + 20 * math.sin(pulse_angle[0])
        canvas.create_oval(w - 160 - r_radius, -40 - r_radius, w - 160 + r_radius, -40 + r_radius,
                           outline="#22d3ee", width=1, dash=(4, 4), tags="master_bg")

        # 3. Moving nodes and connecting mesh lines
        for i, p in enumerate(particles):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0 or p["x"] > w:
                p["vx"] *= -1
            if p["y"] < 0 or p["y"] > h:
                p["vy"] *= -1

            for j in range(i + 1, len(particles)):
                q = particles[j]
                dist = math.hypot(p["x"] - q["x"], p["y"] - q["y"])
                if dist < 140:
                    line_col = "#e2ded4" if dist > 90 else "#a5f3fc"
                    canvas.create_line(p["x"], p["y"], q["x"], q["y"], fill=line_col, width=1, tags="master_bg")

            canvas.create_oval(
                p["x"] - p["radius"], p["y"] - p["radius"],
                p["x"] + p["radius"], p["y"] + p["radius"],
                fill=p["color"], outline="", tags="master_bg"
            )

        canvas.tag_lower("master_bg")
        canvas.after(25, update_animation)

    update_animation()
    return canvas


# ==============================================================================
# 4. CUSTOM INTERACTIVE ANIMATED BUTTON WIDGET
# ==============================================================================
class CustomizedAnimatedButton(tk.Frame):
    """Custom button with smooth padding movement, color morph, and glowing cyan indicator."""
    def __init__(self, parent, text, icon, command, is_active=False):
        super().__init__(parent, bg=THEME["bg_sidebar"], cursor="hand2", height=44)
        self.pack_propagate(False)
        self.command = command
        self.is_active = is_active
        self.pad_left = 16
        self.target_pad = 22 if is_active else 16

        self.indicator = tk.Frame(self, width=4, bg=THEME["accent_cyan"] if is_active else THEME["bg_sidebar"])
        self.indicator.pack(side="left", fill="y", pady=6)

        self.container = tk.Frame(self, bg=THEME["nav_active_bg"] if is_active else THEME["bg_sidebar"])
        self.container.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=2)

        self.lbl = tk.Label(
            self.container,
            text=f"{icon}   {text}",
            font=("Segoe UI", 10, "bold" if is_active else "normal"),
            fg=THEME["accent_cyan_dark"] if is_active else THEME["text_secondary"],
            bg=THEME["nav_active_bg"] if is_active else THEME["bg_sidebar"],
            anchor="w"
        )
        self.lbl.pack(fill="both", expand=True, padx=(self.pad_left, 8))

        for w in (self, self.container, self.lbl):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

        self._smooth_slide()

    def set_active(self, active: bool):
        self.is_active = active
        bg = THEME["nav_active_bg"] if active else THEME["bg_sidebar"]
        fg = THEME["accent_cyan_dark"] if active else THEME["text_secondary"]
        font = ("Segoe UI", 10, "bold") if active else ("Segoe UI", 10)
        ind = THEME["accent_cyan"] if active else THEME["bg_sidebar"]
        self.container.config(bg=bg)
        self.lbl.config(bg=bg, fg=fg, font=font)
        self.indicator.config(bg=ind)
        self.target_pad = 24 if active else 16

    def _on_enter(self, e):
        self.target_pad = 26
        if not self.is_active:
            self.container.config(bg="#e0f2fe")
            self.lbl.config(bg="#e0f2fe", fg=THEME["accent_cyan_dark"])
            self.indicator.config(bg=THEME["accent_cyan_glow"])

    def _on_leave(self, e):
        self.target_pad = 24 if self.is_active else 16
        if not self.is_active:
            self.container.config(bg=THEME["bg_sidebar"])
            self.lbl.config(bg=THEME["bg_sidebar"], fg=THEME["text_secondary"])
            self.indicator.config(bg=THEME["bg_sidebar"])

    def _on_click(self, e):
        if self.command:
            self.command()

    def _smooth_slide(self):
        if self.pad_left != self.target_pad:
            step = 1 if self.target_pad > self.pad_left else -1
            self.pad_left += step
            self.lbl.pack_configure(padx=(self.pad_left, 8))
        self.after(15, self._smooth_slide)


# ==============================================================================
# 5. AUTHENTICATION PORTAL WITH MOVING BACKGROUND
# ==============================================================================
class MomentumLoginPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Momentum // Quantum Operator Authentication")
        self.root.geometry("980x640")
        self.root.configure(bg=THEME["bg_main"])
        self._center_window(980, 640)

        attach_moving_background(self.root)

        card = tk.Frame(self.root, bg=THEME["bg_card"], bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=470)

        tk.Frame(card, bg=THEME["accent_cyan"], height=5).pack(fill="x")

        header = tk.Frame(card, bg=THEME["bg_card"])
        header.pack(pady=(26, 10))
        tk.Label(header, text="ℳ", font=("Segoe UI", 32, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_card"]).pack()
        tk.Label(header, text="MOMENTUM", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card"]).pack()
        tk.Label(header, text="// High-Performance Telemetry Suite", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack()

        form = tk.Frame(card, bg=THEME["bg_card"])
        form.pack(fill="x", padx=44, pady=12)

        tk.Label(form, text="OPERATOR IDENTITY", font=("Segoe UI", 8, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(anchor="w")
        self.user_var = tk.StringVar(value="Srija Basu")
        tk.Entry(
            form, textvariable=self.user_var, font=("Segoe UI", 11),
            bg=THEME["bg_subtle"], fg=THEME["text_primary"], relief="flat",
            highlightbackground=THEME["border"], highlightthickness=1
        ).pack(fill="x", pady=(4, 14), ipady=7)

        tk.Label(form, text="TELEMETRY ACCESS KEY", font=("Segoe UI", 8, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(anchor="w")
        self.pass_var = tk.StringVar(value="momentum2026")
        tk.Entry(
            form, textvariable=self.pass_var, font=("Segoe UI", 11), show="•",
            bg=THEME["bg_subtle"], fg=THEME["text_primary"], relief="flat",
            highlightbackground=THEME["border"], highlightthickness=1
        ).pack(fill="x", pady=(4, 20), ipady=7)

        self.btn = tk.Button(
            form, text="INITIALIZE TELEMETRY SESSION  →",
            font=("Segoe UI", 10, "bold"), bg=THEME["accent_cyan"], fg="#0f172a",
            activebackground=THEME["accent_cyan_glow"], activeforeground="#0f172a",
            relief="flat", cursor="hand2", command=self.login
        )
        self.btn.pack(fill="x", ipady=10)
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=THEME["accent_cyan_glow"]))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=THEME["accent_cyan"]))

        tk.Label(card, text="JDBC Local Cluster: Connected  •  9.8 GHz Optimal", font=("Segoe UI", 8), fg=THEME["accent_cyan_dark"], bg=THEME["bg_card"]).pack(side="bottom", pady=14)

    def _center_window(self, w, h):
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def login(self):
        operator = self.user_var.get().strip()
        if not operator:
            messagebox.showwarning("Validation", "Please enter an Operator Identity.")
            return
        log_exit = log_event("OK", "AUTH_GATE", f"Operator '{operator}' authenticated.")
        self.root.destroy()
        app_root = tk.Tk()
        MomentumSuiteApp(app_root, operator)
        app_root.mainloop()


# ==============================================================================
# 6. MAIN MULTI-PAGE TELEMETRY SUITE APPLICATION
# ==============================================================================
class MomentumSuiteApp:
    def __init__(self, root, operator_name="Srija Basu"):
        self.root = root
        self.operator_name = operator_name
        self.root.title("Momentum // High-Performance Telemetry Suite")
        self.root.geometry("1440x880")
        self.root.configure(bg=THEME["bg_main"])
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.current_page = "Dashboard"
        self.nav_buttons = {}
        self.velocity = 9.8

        self._build_top_bar()
        self._build_layout()
        self.switch_page("Dashboard")
        self._start_live_telemetry_pulse()

    def _build_top_bar(self):
        top = tk.Frame(self.root, bg=THEME["bg_card"], height=48, highlightbackground=THEME["border"], highlightthickness=1)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)

        dots = tk.Frame(top, bg=THEME["bg_card"])
        dots.pack(side="left", padx=16)
        for col in ("#ef4444", "#f59e0b", "#10b981"):
            tk.Label(dots, text="●", fg=col, bg=THEME["bg_card"], font=("Segoe UI", 11)).pack(side="left", padx=2)

        tk.Label(
            top,
            text="Momentum // High-Performance Telemetry Suite",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"]
        ).pack(side="left", padx=24)

        self.status_lbl = tk.Label(
            top,
            text=f"Welcome, {self.operator_name} | Live Session Velocity: 9.8 GHz (Optimal)",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["accent_cyan_dark"],
            bg="#cffafe",
            padx=12,
            pady=4
        )
        self.status_lbl.pack(side="right", padx=18)

    def _build_layout(self):
        body = tk.Frame(self.root, bg=THEME["bg_main"])
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg=THEME["bg_sidebar"], width=260, highlightbackground=THEME["border"], highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=THEME["bg_sidebar"], height=84)
        brand.pack(fill="x", padx=18, pady=(14, 10))
        tk.Label(brand, text="ℳ", font=("Segoe UI", 28, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_sidebar"]).pack(side="left")
        b_txt = tk.Frame(brand, bg=THEME["bg_sidebar"])
        b_txt.pack(side="left", padx=10)
        tk.Label(b_txt, text="MOMENTUM", font=("Segoe UI", 13, "bold"), fg=THEME["text_primary"], bg=THEME["bg_sidebar"]).pack(anchor="w")
        tk.Label(b_txt, text="// Telemetry", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_sidebar"]).pack(anchor="w")

        pages = [
            ("Dashboard", "⊞"),
            ("Data Management", "🗄"),
            ("Analytics Hub", "📈"),
            ("Navigation Console", ">_"),
            ("Workflow Automation", "⚙"),
            ("System Logs", "📋"),
        ]

        for page_name, icon in pages:
            btn = CustomizedAnimatedButton(
                sidebar,
                text=page_name,
                icon=icon,
                command=lambda p=page_name: self.switch_page(p),
                is_active=(page_name == "Dashboard")
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page_name] = btn

        footer_card = tk.Frame(sidebar, bg=THEME["bg_subtle"], highlightbackground=THEME["border"], highlightthickness=1)
        footer_card.pack(side="bottom", fill="x", padx=14, pady=16)
        tk.Label(footer_card, text="OPERATOR ONLINE", font=("Segoe UI", 7, "bold"), fg=THEME["accent_cyan_dark"], bg=THEME["bg_subtle"]).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(footer_card, text=self.operator_name, font=("Segoe UI", 10, "bold"), fg=THEME["text_primary"], bg=THEME["bg_subtle"]).pack(anchor="w", padx=10)
        tk.Label(footer_card, text="JDBC Local Cluster: Active", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["bg_subtle"]).pack(anchor="w", padx=10, pady=(0, 8))

        viewport_holder = tk.Frame(body, bg=THEME["bg_main"])
        viewport_holder.pack(side="right", fill="both", expand=True)

        # Universal moving background attached behind EVERY page viewport
        attach_moving_background(viewport_holder)

        self.scroll_canvas = tk.Canvas(viewport_holder, bg=THEME["bg_main"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(viewport_holder, orient="vertical", command=self.scroll_canvas.yview)
        self.page_container = tk.Frame(self.scroll_canvas, bg=THEME["bg_main"])

        self.page_container.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.page_container, anchor="nw")
        self.scroll_canvas.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.itemconfig(self.canvas_window, width=e.width)
        )
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_canvas.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.scrollbar.pack(side="right", fill="y")

        self.root.bind_all("<MouseWheel>", lambda e: self.scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _start_live_telemetry_pulse(self):
        delta = random.choice([-0.1, 0.0, 0.1, 0.2])
        self.velocity = round(max(9.4, min(10.2, self.velocity + delta)), 1)
        self.status_lbl.config(
            text=f"Welcome, {self.operator_name} | Live Session Velocity: {self.velocity} GHz (Optimal)"
        )
        self.root.after(2200, self._start_live_telemetry_pulse)

    def switch_page(self, page_name):
        self.current_page = page_name
        for name, btn in self.nav_buttons.items():
            btn.set_active(name == page_name)

        for widget in self.page_container.winfo_children():
            widget.destroy()

        self.scroll_canvas.yview_moveto(0)

        builders = {
            "Dashboard": self.build_dashboard_page,
            "Data Management": self.build_data_management_page,
            "Analytics Hub": self.build_analytics_hub_page,
            "Navigation Console": self.build_navigation_console_page,
            "Workflow Automation": self.build_workflow_automation_page,
            "System Logs": self.build_system_logs_page,
        }
        builders[page_name]()

    def _make_card(self, parent, title=None, subtitle=None, right_badge=None):
        card = tk.Frame(parent, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        if title:
            hdr = tk.Frame(card, bg=THEME["bg_card"])
            hdr.pack(fill="x", padx=18, pady=(14, 8))
            tk.Label(hdr, text=title, font=("Segoe UI", 12, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side="left")
            if subtitle:
                tk.Label(hdr, text=f"  •  {subtitle}", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(side="left")
            if right_badge:
                tk.Label(hdr, text=right_badge, font=("Segoe UI", 8, "bold"), fg=THEME["accent_cyan_dark"], bg="#cffafe", padx=10, pady=3).pack(side="right")
        return card

    # ==========================================================================
    # PAGE 1: DASHBOARD
    # ==========================================================================
    def build_dashboard_page(self):
        top_hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        top_hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(top_hdr, text="Dashboard", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")
        tk.Label(top_hdr, text="Real-time operational telemetry & sprint execution stream", font=("Segoe UI", 10), fg=THEME["text_secondary"], bg=THEME["bg_main"]).pack(side="left", padx=16)

        split = tk.Frame(self.page_container, bg=THEME["bg_main"])
        split.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        split.columnconfigure(0, weight=5)
        split.columnconfigure(1, weight=6)

        task_card = self._make_card(split, title="Task Stream", right_badge="⟳ Live Sync")
        task_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        th = tk.Frame(task_card, bg=THEME["bg_subtle"], height=32)
        th.pack(fill="x", padx=16, pady=(4, 6))
        for col, w in [("Task", 24), ("Priority", 10), ("Progress", 14), ("Assign", 10)]:
            tk.Label(th, text=col, font=("Segoe UI", 8, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_subtle"], width=w, anchor="w").pack(side="left", padx=4)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name, priority, progress, assignee FROM tasks LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        for tid, tname, prio, prog, assign in rows:
            row = tk.Frame(task_card, bg=THEME["bg_card"], height=38)
            row.pack(fill="x", padx=16, pady=2)

            var = tk.IntVar(value=1 if prog == 100 else 0)
            tk.Checkbutton(row, variable=var, bg=THEME["bg_card"], activebackground=THEME["bg_card"],
                           command=lambda t=tname: log_event("INFO", "TASK_STREAM", f"Toggled '{t}'")).pack(side="left")

            tk.Label(row, text=tname, font=("Segoe UI", 9), fg=THEME["text_primary"], bg=THEME["bg_card"], width=22, anchor="w").pack(side="left")

            p_col = THEME["accent_green"] if prio in ("High", "Now") else THEME["accent_amber"]
            tk.Label(row, text=f"✓ {prio}", font=("Segoe UI", 8, "bold"), fg=p_col, bg=THEME["bg_card"], width=9, anchor="w").pack(side="left")

            p_bar = tk.Canvas(row, width=95, height=8, bg="#cbd5e1", highlightthickness=0)
            p_bar.pack(side="left", padx=6)
            p_bar.create_rectangle(0, 0, int(95 * prog / 100), 8, fill=THEME["accent_cyan"], outline="")

            tk.Label(row, text=assign, font=("Segoe UI", 8, "bold"), fg=THEME["text_secondary"], bg="#f1f5f9", padx=6, pady=2).pack(side="right", padx=6)

            row.bind("<Enter>", lambda e, r=row: r.config(bg="#f8fafc"))
            row.bind("<Leave>", lambda e, r=row: r.config(bg=THEME["bg_card"]))

        right_col = tk.Frame(split, bg=THEME["bg_main"])
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        op_card = self._make_card(right_col, title="Operational Overview", right_badge="● Cognitive Flow   ● Deliverables   ● Energy")
        op_card.pack(fill="x", pady=(0, 14))

        chart = tk.Canvas(op_card, height=195, bg=THEME["bg_card"], highlightthickness=0)
        chart.pack(fill="x", padx=18, pady=(4, 14))
        self._draw_operational_spline(chart)

        pic_card = self._make_card(right_col, title="Live Optic Sensor Snapshot // Node-01 Feed", right_badge="4K Feed • Active")
        pic_card.pack(fill="x", pady=(0, 14))
        
        pic_canv = tk.Canvas(pic_card, height=130, bg="#0f172a", highlightthickness=0)
        pic_canv.pack(fill="x", padx=18, pady=(4, 14))
        pic_canv.create_line(0, 65, 560, 65, fill="#1e293b", width=1)
        pic_canv.create_line(280, 0, 280, 130, fill="#1e293b", width=1)
        pic_canv.create_rectangle(40, 30, 220, 100, outline=THEME["accent_cyan"], width=1.5, dash=(4, 2))
        pic_canv.create_text(130, 65, text="OPTIC_FEED // SRIJA_NODE", font=("Consolas", 9, "bold"), fill=THEME["accent_cyan_glow"])
        pic_canv.create_text(420, 65, text="Status: Optimal\nLatency: 2.1ms\nTarget: Locked", font=("Segoe UI", 9), fill="#94a3b8", justify="left")

        sub_grid = tk.Frame(right_col, bg=THEME["bg_main"])
        sub_grid.pack(fill="both", expand=True)
        sub_grid.columnconfigure(0, weight=1)
        sub_grid.columnconfigure(1, weight=1)

        c1 = self._make_card(sub_grid, title="1. Sprint deliverable tracking")
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=(0, 7))
        tk.Label(c1, text="Sprint deliverable tracking          18/24   (75%)", font=("Segoe UI", 9, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(anchor="w", padx=18)
        dots_c = tk.Canvas(c1, height=46, bg=THEME["bg_card"], highlightthickness=0)
        dots_c.pack(fill="x", padx=18, pady=8)
        for i in range(6):
            fill = THEME["accent_cyan"] if i < 4 else "#cbd5e1"
            dots_c.create_oval(10 + i * 42, 8, 34 + i * 42, 32, fill=fill, outline="")
            if i < 5:
                dots_c.create_line(34 + i * 42, 20, 52 + i * 42, 20, fill=fill, width=2)

        c2 = self._make_card(sub_grid, title="2. Resource Allocation")
        c2.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=(0, 7))
        donut_row = tk.Frame(c2, bg=THEME["bg_card"])
        donut_row.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        d_canv = tk.Canvas(donut_row, width=90, height=90, bg=THEME["bg_card"], highlightthickness=0)
        d_canv.pack(side="left")
        segments = [(0, 122, THEME["accent_cyan"]), (122, 95, "#2563eb"), (217, 72, "#7c3aed"), (289, 71, "#10b981")]
        for start, extent, col in segments:
            d_canv.create_arc(8, 8, 82, 82, start=start, extent=extent, fill=col, outline="white", width=2)
        d_canv.create_oval(26, 26, 64, 64, fill=THEME["bg_card"], outline="")
        tk.Label(donut_row, text="• Research 34%\n• Dev 26%\n• Design 20%\n• Admin 20%", font=("Segoe UI", 8, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"], justify="left").pack(side="left", padx=10)

        c3 = self._make_card(sub_grid, title="3. Predictive Modeling", right_badge="Automated trend")
        c3.grid(row=1, column=0, sticky="nsew", padx=(0, 7), pady=(7, 0))
        pred_c = tk.Canvas(c3, height=78, bg=THEME["bg_card"], highlightthickness=0)
        pred_c.pack(fill="x", padx=16, pady=(0, 10))
        pred_c.create_line(10, 62, 60, 48, 110, 52, 165, 28, 225, 16, fill=THEME["accent_cyan"], width=2.5, smooth=True)
        pred_c.create_line(10, 68, 60, 58, 110, 44, 165, 36, 225, 22, fill=THEME["accent_purple"], width=2, smooth=True)

        c4 = self._make_card(sub_grid, title="4. Team Console Status")
        c4.grid(row=1, column=1, sticky="nsew", padx=(7, 0), pady=(7, 0))
        for dot_col, label in [(THEME["accent_green"], "Active (5/8)"), (THEME["text_muted"], "Idle (2/8)"), (THEME["accent_red"], "Offline (1/8)")]:
            r = tk.Frame(c4, bg=THEME["bg_card"])
            r.pack(anchor="w", padx=18, pady=2)
            tk.Label(r, text="●", fg=dot_col, bg=THEME["bg_card"], font=("Segoe UI", 10)).pack(side="left")
            tk.Label(r, text=f"  {label}", fg=THEME["text_primary"], bg=THEME["bg_card"], font=("Segoe UI", 9, "bold")).pack(side="left")

    def _draw_operational_spline(self, canvas):
        for idx, y in enumerate([25, 65, 105, 145]):
            val = 100 - idx * 25
            canvas.create_text(18, y, text=str(val), font=("Segoe UI", 8), fill=THEME["text_muted"])
            canvas.create_line(38, y, 560, y, fill="#f1f5f9", dash=(3, 3))

        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        for i, d in enumerate(days):
            x = 55 + i * 120
            canvas.create_text(x, 172, text=d, font=("Segoe UI", 8, "bold"), fill=THEME["text_secondary"])

        s1 = [55, 120, 115, 70, 175, 95, 235, 50, 295, 85, 355, 60, 415, 35, 475, 45, 535, 28]
        s2 = [55, 90, 115, 115, 175, 68, 235, 92, 295, 55, 355, 80, 415, 65, 475, 78, 535, 52]
        s3 = [55, 138, 115, 102, 175, 118, 235, 78, 295, 105, 355, 72, 415, 88, 475, 62, 535, 68]

        canvas.create_line(s1, fill=THEME["accent_cyan"], width=2.5, smooth=True)
        canvas.create_line(s2, fill=THEME["accent_purple"], width=2.2, smooth=True)
        canvas.create_line(s3, fill=THEME["accent_blue"], width=2.0, smooth=True)

        for i in range(0, len(s1), 2):
            canvas.create_oval(s1[i]-3.5, s1[i+1]-3.5, s1[i]+3.5, s1[i+1]+3.5, fill=THEME["accent_cyan"], outline="white", width=1.5)

    # ==========================================================================
    # PAGE 2: DATA MANAGEMENT
    # ==========================================================================
    def build_data_management_page(self):
        hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(hdr, text="Data Management // JDBC Task & Telemetry Repository", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")

        add_card = self._make_card(self.page_container, title="Insert New Operational Record", right_badge="SQLite / JDBC Direct Commit")
        add_card.pack(fill="x", padx=24, pady=(0, 16))

        form = tk.Frame(add_card, bg=THEME["bg_card"])
        form.pack(fill="x", padx=18, pady=(4, 16))

        tk.Label(form, text="Task Descriptor:", font=("Segoe UI", 9, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(side="left")
        t_entry = tk.Entry(form, font=("Segoe UI", 10), bg=THEME["bg_subtle"], relief="flat", width=28)
        t_entry.pack(side="left", padx=(6, 16), ipady=5)

        tk.Label(form, text="Priority:", font=("Segoe UI", 9, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(side="left")
        p_combo = ttk.Combobox(form, values=["High", "Medium", "Low", "Now"], width=10, state="readonly")
        p_combo.set("High")
        p_combo.pack(side="left", padx=(6, 16))

        tk.Label(form, text="Assignee:", font=("Segoe UI", 9, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(side="left")
        a_entry = tk.Entry(form, font=("Segoe UI", 10), bg=THEME["bg_subtle"], relief="flat", width=14)
        a_entry.insert(0, self.operator_name)
        a_entry.pack(side="left", padx=(6, 16), ipady=5)

        def insert_record():
            name = t_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Required", "Enter a task descriptor.")
                return
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tasks (task_name, priority, progress, assignee, status) VALUES (?, ?, ?, ?, ?)",
                        (name, p_combo.get(), 25, a_entry.get().strip() or "Srija Basu", "Active"))
            conn.commit()
            conn.close()
            log_event("OK", "DATA_MGMT", f"Inserted record '{name}'.")
            self.switch_page("Data Management")

        tk.Button(form, text="+ Commit Record", font=("Segoe UI", 9, "bold"), bg=THEME["accent_cyan"], fg="#0f172a",
                  relief="flat", padx=14, pady=5, cursor="hand2", command=insert_record).pack(side="left")

        table_card = self._make_card(self.page_container, title="Live Relational Records Table", right_badge="Table: momentum_telemetry_pro.tasks")
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tree = ttk.Treeview(table_card, columns=("ID", "Task Name", "Priority", "Progress", "Assignee", "Status"), show="headings", height=12)
        for col, w in [("ID", 60), ("Task Name", 340), ("Priority", 120), ("Progress", 120), ("Assignee", 160), ("Status", 120)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, task_name, priority, progress, assignee, status FROM tasks ORDER BY id DESC")
        for r in cur.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]}%", r[4], r[5]))
        conn.close()

        tree.pack(fill="both", expand=True, padx=18, pady=(4, 12))

        def delete_selected():
            sel = tree.selection()
            if not sel:
                return
            item_id = tree.item(sel[0])["values"][0]
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("DELETE FROM tasks WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            log_event("WARN", "DATA_MGMT", f"Deleted record ID #{item_id}.")
            self.switch_page("Data Management")

        tk.Button(table_card, text="Delete Selected Record", font=("Segoe UI", 9, "bold"), bg="#fee2e2", fg=THEME["accent_red"],
                  relief="flat", padx=12, pady=5, cursor="hand2", command=delete_selected).pack(anchor="e", padx=18, pady=(0, 14))

    # ==========================================================================
    # PAGE 3: ANALYTICS HUB
    # ==========================================================================
    def build_analytics_hub_page(self):
        hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(hdr, text="Analytics Hub // Cognitive Productivity & Throughput Intelligence", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")

        kpi_row = tk.Frame(self.page_container, bg=THEME["bg_main"])
        kpi_row.pack(fill="x", padx=24, pady=(0, 16))
        for idx in range(4):
            kpi_row.columnconfigure(idx, weight=1)

        kpis = [
            ("DEEP FOCUS INDEX", "94.2%", "+6.4% vs last week", THEME["accent_cyan_dark"]),
            ("SPRINT VELOCITY", "48.5 pts", "Optimal cadence", THEME["accent_green"]),
            ("AVG LATENCY", "11.4 ms", "-2.1 ms improvement", THEME["accent_purple"]),
            ("ENERGY EFFICIENCY", "98.1%", "Peak cognitive zone", THEME["accent_cyan"]),
        ]
        for i, (label, val, sub, col) in enumerate(kpis):
            c = self._make_card(kpi_row)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            tk.Label(c, text=label, font=("Segoe UI", 8, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", padx=16, pady=(14, 2))
            tk.Label(c, text=val, font=("Segoe UI", 22, "bold"), fg=col, bg=THEME["bg_card"]).pack(anchor="w", padx=16)
            tk.Label(c, text=sub, font=("Segoe UI", 8), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(anchor="w", padx=16, pady=(2, 14))

        chart_card = self._make_card(self.page_container, title="Hourly Cognitive Output vs. Task Completion Rate", right_badge="24-Hour Telemetry Cycle")
        chart_card.pack(fill="x", padx=24, pady=(0, 24))

        bar_canvas = tk.Canvas(chart_card, height=260, bg=THEME["bg_card"], highlightthickness=0)
        bar_canvas.pack(fill="x", padx=20, pady=(6, 18))

        hours = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
        values = [62, 78, 94, 98, 72, 68, 86, 92, 89, 76, 84, 70]
        for i, (hr, val) in enumerate(zip(hours, values)):
            x0 = 45 + i * 82
            x1 = x0 + 44
            y1 = 220
            y0 = 220 - int(val * 1.8)
            col = THEME["accent_cyan"] if val >= 85 else "#a5f3fc"
            bar_canvas.create_rectangle(x0, y0, x1, y1, fill=col, outline="")
            bar_canvas.create_text((x0 + x1) // 2, y0 - 10, text=f"{val}%", font=("Segoe UI", 8, "bold"), fill=THEME["text_primary"])
            bar_canvas.create_text((x0 + x1) // 2, 236, text=hr, font=("Segoe UI", 8), fill=THEME["text_secondary"])

    # ==========================================================================
    # PAGE 4: NAVIGATION CONSOLE
    # ==========================================================================
    def build_navigation_console_page(self):
        hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(hdr, text="Navigation Console // Smart Command & Telemetry Shell", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")

        console_card = self._make_card(self.page_container, title="Momentum Interactive CLI", right_badge="Type 'help', 'status', 'tasks', or 'clear'")
        console_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        output = tk.Text(console_card, height=18, bg="#0f172a", fg="#22d3ee", font=("Consolas", 10), relief="flat", padx=14, pady=14)
        output.pack(fill="both", expand=True, padx=18, pady=(6, 10))
        output.insert("end", f"Momentum Telemetry Shell v4.2 [Operator: {self.operator_name}]\n")
        output.insert("end", "Type 'help' for available smart navigation & diagnostic commands.\n\n> ")

        cmd_bar = tk.Frame(console_card, bg=THEME["bg_card"])
        cmd_bar.pack(fill="x", padx=18, pady=(0, 16))

        cmd_entry = tk.Entry(cmd_bar, font=("Consolas", 11), bg=THEME["bg_subtle"], fg=THEME["text_primary"], relief="flat")
        cmd_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

        def run_cmd(event=None):
            cmd = cmd_entry.get().strip().lower()
            cmd_entry.delete(0, "end")
            if not cmd:
                return
            output.insert("end", f"{cmd}\n")
            if cmd == "help":
                output.insert("end", "  Commands: status | tasks | goto <page> | clear\n")
            elif cmd == "status":
                output.insert("end", f"  [OK] Velocity: {self.velocity} GHz | DB: Connected | Threads: 8 Active\n")
            elif cmd == "tasks":
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM tasks")
                cnt = cur.fetchone()[0]
                conn.close()
                output.insert("end", f"  [DB] Total active tasks in JDBC store: {cnt}\n")
            elif cmd == "clear":
                output.delete("1.0", "end")
            elif cmd.startswith("goto "):
                target = cmd.replace("goto ", "").title()
                if target in self.nav_buttons:
                    self.switch_page(target)
                    return
                output.insert("end", f"  [ERR] Unknown module '{target}'\n")
            else:
                output.insert("end", f"  Executed telemetry directive: '{cmd}' -> ACK (12ms)\n")
            output.insert("end", "> ")
            output.see("end")

        cmd_entry.bind("<Return>", run_cmd)
        tk.Button(cmd_bar, text="Execute", font=("Segoe UI", 9, "bold"), bg=THEME["accent_cyan"], fg="#0f172a",
                  relief="flat", padx=16, pady=6, cursor="hand2", command=run_cmd).pack(side="right")

    # ==========================================================================
    # PAGE 5: WORKFLOW AUTOMATION
    # ==========================================================================
    def build_workflow_automation_page(self):
        hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(hdr, text="Workflow Automation // Autonomous Telemetry Pipelines", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")

        pipelines = [
            ("JDBC Real-Time Sync", "Continuously replicates task updates to local SQLite persistence layer every 500ms.", True),
            ("Predictive Anomaly Guard", "Monitors cognitive velocity dips and automatically rebalances sprint priorities.", True),
            ("Automated Sprint Digest", "Compiles daily deliverable metrics and archives completion logs at 18:00 IST.", False),
            ("Zero-Latency Cache Warmup", "Pre-loads analytical spline vectors into memory prior to session start.", True),
        ]

        for title, desc, enabled in pipelines:
            card = self._make_card(self.page_container, title=title, right_badge="ACTIVE PIPELINE" if enabled else "STANDBY")
            card.pack(fill="x", padx=24, pady=(0, 12))
            row = tk.Frame(card, bg=THEME["bg_card"])
            row.pack(fill="x", padx=18, pady=(0, 14))
            tk.Label(row, text=desc, font=("Segoe UI", 9), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(side="left")

            state_var = tk.BooleanVar(value=enabled)
            tk.Checkbutton(
                row, text="Enabled", variable=state_var, font=("Segoe UI", 9, "bold"),
                fg=THEME["accent_cyan_dark"], bg=THEME["bg_card"],
                command=lambda t=title, v=state_var: log_event("INFO", "WORKFLOW", f"Pipeline '{t}' set to {v.get()}")
            ).pack(side="right")

    # ==========================================================================
    # PAGE 6: SYSTEM LOGS
    # ==========================================================================
    def build_system_logs_page(self):
        hdr = tk.Frame(self.page_container, bg=THEME["bg_main"])
        hdr.pack(fill="x", padx=24, pady=(16, 12))
        tk.Label(hdr, text="System Logs // Immutable Telemetry Audit Trail", font=("Segoe UI", 18, "bold"), fg=THEME["text_primary"], bg=THEME["bg_main"]).pack(side="left")

        log_card = self._make_card(self.page_container, title="Kernel & JDBC Event Stream", right_badge="Live Audit Feed")
        log_card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tree = ttk.Treeview(log_card, columns=("Timestamp", "Level", "Module", "Message"), show="headings", height=16)
        for col, w in [("Timestamp", 130), ("Level", 90), ("Module", 150), ("Message", 620)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, level, module, message FROM system_logs ORDER BY id DESC LIMIT 40")
        for r in cur.fetchall():
            tree.insert("", "end", values=r)
        conn.close()

        tree.pack(fill="both", expand=True, padx=18, pady=(6, 16))


# ==============================================================================
# 7. APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#0f172a", rowheight=28, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background="#e2e8f0", foreground="#475569", font=("Segoe UI", 9, "bold"))

    app = MomentumLoginPortal(root)
    root.mainloop()