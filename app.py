import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinterdnd2 import TkinterDnD, DND_FILES


df_global = None   # holds the loaded dataframe


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def load_file(path: str) -> pd.DataFrame:
    path = path.strip().strip("{}")   # tkdnd sometimes wraps in {}
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df[df["arr_cancelled"] == 0].copy()
    delay_cols = ["carrier_delay", "weather_delay", "nas_delay",
                  "security_delay", "late_aircraft_delay", "arr_delay"]
    for c in delay_cols:
        if c in df2.columns:
            df2[c] = df2[c].fillna(0)
    return df2


DELAY_COLS  = ["carrier_delay", "weather_delay", "nas_delay",
               "security_delay", "late_aircraft_delay"]
DELAY_LBLS  = ["Carrier", "Weather", "NAS", "Security", "Late Aircraft"]
MONTH_NAMES = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
               7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}


def fig_bar(df):
    totals = df[DELAY_COLS].sum()
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PANEL)
    ax.set_facecolor(PANEL)
    bars = ax.bar(DELAY_LBLS, totals / 1e6, color=BAR_COLS,
                  edgecolor=BG, linewidth=0.8)
    for bar, val in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val/1e6:.1f}M", ha="center", va="bottom",
                fontsize=8, color=TEXT)
    ax.set_title("Total Delay by Cause", color=TEXT, fontsize=12, fontweight="bold")
    ax.set_ylabel("Minutes (millions)", color=SUBTEXT)
    ax.tick_params(colors=SUBTEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}M"))
    fig.tight_layout()
    return fig


def fig_hist(df):
    arr = df["arr_delay"].dropna()
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PANEL)
    ax.set_facecolor(PANEL)
    ax.hist(arr, bins=40, color=ACCENT, edgecolor=BG, linewidth=0.4)
    ax.axvline(arr.mean(), color="#f59e0b", linestyle="--", linewidth=1.4,
               label=f"Mean: {arr.mean():.0f} min")
    ax.set_title("ArrDelay Distribution", color=TEXT, fontsize=12, fontweight="bold")
    ax.set_xlabel("Total delay (min)", color=SUBTEXT)
    ax.set_ylabel("Count", color=SUBTEXT)
    ax.tick_params(colors=SUBTEXT)
    ax.legend(facecolor=PANEL, labelcolor=TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    fig.tight_layout()
    return fig


def fig_scatter(df):
    s = df[["arr_flights", "arr_delay"]].dropna()
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PANEL)
    ax.set_facecolor(PANEL)
    ax.scatter(s["arr_flights"], s["arr_delay"],
               alpha=0.35, s=14, color=ACCENT2, edgecolors="none")
    ax.set_title("Flights Volume vs Arrival Delay", color=TEXT,
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("Number of flights (arr_flights)", color=SUBTEXT)
    ax.set_ylabel("Total delay (min)", color=SUBTEXT)
    ax.tick_params(colors=SUBTEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    fig.tight_layout()
    return fig


def fig_line(df):
    """
    Group by year+month so we get one point per period.
    If only one month exists across years, still shows a meaningful trend.
    """
    has_year = "year" in df.columns
    if has_year and df["year"].nunique() > 1:
        grp = df.groupby("year")["arr_delay"].mean().reset_index()
        x_vals = grp["year"].astype(str)
        y_vals = grp["arr_delay"]
        xlabel = "Year"
    elif df["month"].nunique() > 1:
        grp = df.groupby("month")["arr_delay"].mean().reset_index()
        x_vals = grp["month"].map(MONTH_NAMES)
        y_vals = grp["arr_delay"]
        xlabel = "Month"
    else:
        # Single period — show by carrier (top 10)
        grp = (df.groupby("carrier_name")["arr_delay"]
                 .mean()
                 .nlargest(10)
                 .reset_index())
        x_vals = grp["carrier_name"]
        y_vals = grp["arr_delay"]
        xlabel = "Carrier (top 10 by avg delay)"

    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PANEL)
    ax.set_facecolor(PANEL)
    x_idx = range(len(x_vals))
    ax.plot(list(x_idx), list(y_vals), marker="o", color=ACCENT,
            linewidth=2, markersize=7, markerfacecolor=ACCENT2)
    ax.fill_between(list(x_idx), list(y_vals), alpha=0.12, color=ACCENT)
    ax.set_xticks(list(x_idx))
    ax.set_xticklabels(list(x_vals), rotation=20, ha="right", fontsize=8)
    ax.set_title("Average Arrival Delay Trend", color=TEXT,
                 fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel, color=SUBTEXT)
    ax.set_ylabel("Avg delay (min)", color=SUBTEXT)
    ax.tick_params(colors=SUBTEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    fig.tight_layout()
    return fig


def get_stats(df):
    cause_totals = df[DELAY_COLS].sum()
    top_cause = DELAY_LBLS[cause_totals.values.argmax()]

    has_year = "year" in df.columns and df["year"].nunique() > 1
    if has_year:
        grp = df.groupby("year")["arr_delay"].mean()
        worst_lbl = f"Year {int(grp.idxmax())}"
        worst_val = grp.max()
    elif df["month"].nunique() > 1:
        grp = df.groupby("month")["arr_delay"].mean()
        worst_lbl = MONTH_NAMES.get(int(grp.idxmax()), str(grp.idxmax()))
        worst_val = grp.max()
    else:
        grp = df.groupby("carrier_name")["arr_delay"].mean()
        worst_lbl = grp.idxmax()
        worst_val = grp.max()

    corr = df["arr_flights"].corr(df["arr_delay"])

    lines = [
        f"Period with highest avg delay : {worst_lbl}  ({worst_val:.1f} min)",
        f"Top delay cause               : {top_cause}  ({cause_totals.max():,.0f} min total)",
        "",
        "Delay breakdown (total minutes):",
    ]
    for lbl, col in zip(DELAY_LBLS, DELAY_COLS):
        lines.append(f"  {lbl:<18}: {cause_totals[col]:>12,.0f} min")
    lines += [
        "",
        f"Pearson corr (flights vs delay): {corr:.3f}",
        ("-> Positive link: busier routes tend to have more delays."
         if corr > 0.3 else
         "-> Weak / no link between flight volume and delay.")
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════════════════════

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flight Delay Analyzer")
        self.configure(bg=BG)
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.df = None
        self._build_ui()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── header
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✈  Flight Delay Analyzer",
                 bg=ACCENT, fg="white", font=("Segoe UI", 16, "bold")).pack()
        tk.Label(hdr, text="Drop a CSV or Excel file to get started",
                 bg=ACCENT, fg="#ddd6fe", font=("Segoe UI", 9)).pack()

        # ── main content split
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # LEFT column
        left = tk.Frame(main, bg=BG, width=320)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        self._build_upload_box(left)
        self._build_buttons(left)
        self._build_stats(left)

        # RIGHT column
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_table(right)
        self._build_plot_area(right)

    # ── upload box ────────────────────────────────────────────────────────────
    def _build_upload_box(self, parent):
        frame = tk.Frame(parent, bg=PANEL, bd=0, relief="flat")
        frame.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(frame, bg=PANEL, highlightbackground=ACCENT,
                         highlightthickness=2)
        inner.pack(fill="x", padx=2, pady=2)

        tk.Label(inner, text="⬆", font=("Segoe UI", 28), bg=PANEL,
                 fg=ACCENT).pack(pady=(18, 4))
        self.upload_lbl = tk.Label(inner, text="Upload here",
                                   font=("Segoe UI", 13, "bold"),
                                   bg=PANEL, fg=TEXT)
        self.upload_lbl.pack()
        tk.Label(inner, text="Drag & drop  ·  CSV or Excel (.xlsx)",
                 font=("Segoe UI", 8), bg=PANEL, fg=SUBTEXT).pack(pady=(2, 4))

        btn = tk.Button(inner, text="Browse file…",
                        font=("Segoe UI", 9), bg=ACCENT, fg="white",
                        activebackground=ACCENT2, relief="flat", cursor="hand2",
                        padx=14, pady=5, bd=0,
                        command=self._browse)
        btn.pack(pady=(4, 18))

        # register drop target
        inner.drop_target_register(DND_FILES)
        inner.dnd_bind("<<Drop>>", self._on_drop)
        for child in inner.winfo_children():
            child.drop_target_register(DND_FILES)
            child.dnd_bind("<<Drop>>", self._on_drop)

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV / Excel", "*.csv *.xlsx *.xls"), ("All files", "*.*")])
        if path:
            self._load(path)

    def _on_drop(self, event):
        self._load(event.data)

    def _load(self, path):
        try:
            df_raw = load_file(path)
            self.df = clean_df(df_raw)
            self.upload_lbl.config(text="✓  File loaded!", fg=SUCCESS)
            self._populate_table(df_raw)
            self._clear_plot()
            self.stats_txt.config(state="normal")
            self.stats_txt.delete("1.0", "end")
            self.stats_txt.insert("end", f"Rows: {len(df_raw):,}  |  "
                                         f"After cleaning: {len(self.df):,}\n\n"
                                         "Run an analysis below ↓")
            self.stats_txt.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    # ── action buttons ────────────────────────────────────────────────────────
    def _build_buttons(self, parent):
        frame = tk.LabelFrame(parent, text=" Analysis Tasks ",
                              bg=PANEL, fg=ACCENT2,
                              font=("Segoe UI", 9, "bold"),
                              bd=1, relief="groove")
        frame.pack(fill="x", pady=(0, 10))

        tasks = [
            ("Task 3 – Bar: Delay Causes",   self._task3),
            ("Task 4 – Histogram: ArrDelay", self._task4),
            ("Task 5 – Scatter: Flights vs Delay", self._task5),
            ("Task 6 – Line: Delay Trend",   self._task6),
            ("Task 7 – Statistics",          self._task7),
            ("Task 8 – Save Summary PNG",    self._task8),
        ]
        for txt, cmd in tasks:
            b = tk.Button(frame, text=txt, command=cmd,
                          font=("Segoe UI", 9), bg=BG, fg=TEXT,
                          activebackground=ACCENT, activeforeground="white",
                          relief="flat", bd=0, padx=8, pady=6,
                          cursor="hand2", anchor="w")
            b.pack(fill="x", padx=8, pady=3)

    # ── stats panel ───────────────────────────────────────────────────────────
    def _build_stats(self, parent):
        frame = tk.LabelFrame(parent, text=" Results ",
                              bg=PANEL, fg=ACCENT2,
                              font=("Segoe UI", 9, "bold"),
                              bd=1, relief="groove")
        frame.pack(fill="both", expand=True)

        self.stats_txt = tk.Text(frame, bg=PANEL, fg=TEXT,
                                 font=("Consolas", 8), relief="flat",
                                 wrap="word", state="disabled",
                                 insertbackground=TEXT)
        self.stats_txt.pack(fill="both", expand=True, padx=6, pady=6)

    # ── table ─────────────────────────────────────────────────────────────────
    def _build_table(self, parent):
        lbl_frame = tk.Frame(parent, bg=BG)
        lbl_frame.pack(fill="x", pady=(0, 4))
        tk.Label(lbl_frame, text="First 10 rows",
                 bg=BG, fg=ACCENT2,
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        table_frame = tk.Frame(parent, bg=PANEL, height=190)
        table_frame.pack(fill="x")
        table_frame.pack_propagate(False)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Treeview",
                        background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=22,
                        font=("Consolas", 8))
        style.configure("Dark.Treeview.Heading",
                        background=ACCENT, foreground="white",
                        font=("Segoe UI", 8, "bold"), relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        self.tree = ttk.Treeview(table_frame, style="Dark.Treeview",
                                 show="headings", selectmode="browse")

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

    def _populate_table(self, df: pd.DataFrame):
        self.tree.delete(*self.tree.get_children())
        cols = list(df.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=max(80, len(c) * 8),
                             anchor="center", stretch=False)
        for _, row in df.head(10).iterrows():
            self.tree.insert("", "end",
                             values=[str(v) if pd.notna(v) else "" for v in row])

    # ── plot area ─────────────────────────────────────────────────────────────
    def _build_plot_area(self, parent):
        self.plot_frame = tk.Frame(parent, bg=PANEL, bd=0)
        self.plot_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.canvas_widget = None

    def _show_plot(self, fig):
        plt.rcParams.update({"text.color": TEXT, "axes.labelcolor": SUBTEXT,
                             "xtick.color": SUBTEXT, "ytick.color": SUBTEXT})
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas_widget = canvas
        plt.close(fig)

    def _clear_plot(self):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None

    # ── guard helper ──────────────────────────────────────────────────────────
    def _need_data(self) -> bool:
        if self.df is None:
            messagebox.showwarning("No data", "Please upload a file first.")
            return True
        return False

    # ── task handlers ─────────────────────────────────────────────────────────
    def _task3(self):
        if self._need_data(): return
        self._show_plot(fig_bar(self.df))

    def _task4(self):
        if self._need_data(): return
        self._show_plot(fig_hist(self.df))

    def _task5(self):
        if self._need_data(): return
        self._show_plot(fig_scatter(self.df))

    def _task6(self):
        if self._need_data(): return
        self._show_plot(fig_line(self.df))

    def _task7(self):
        if self._need_data(): return
        stats = get_stats(self.df)
        self.stats_txt.config(state="normal")
        self.stats_txt.delete("1.0", "end")
        self.stats_txt.insert("end", stats)
        self.stats_txt.config(state="disabled")

    def _task8(self):
        if self._need_data(): return
        os.makedirs("output", exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(14, 8), facecolor=BG)
        fig.suptitle("Flight Delay Analysis — Summary", color=TEXT,
                     fontsize=15, fontweight="bold", y=1.01)

        df = self.df
        totals = df[DELAY_COLS].sum()
        arr = df["arr_delay"].dropna()
        s   = df[["arr_flights", "arr_delay"]].dropna()

        for ax in axes.flat:
            ax.set_facecolor(PANEL)
            for sp in ax.spines.values():
                sp.set_edgecolor(BORDER)
            ax.tick_params(colors=SUBTEXT)

        # bar
        axes[0,0].bar(DELAY_LBLS, totals/1e6, color=BAR_COLS, edgecolor=BG)
        axes[0,0].set_title("Delay by Cause", color=TEXT, fontsize=10, fontweight="bold")
        axes[0,0].set_ylabel("Millions of min", color=SUBTEXT, fontsize=8)
        axes[0,0].tick_params(axis="x", labelsize=7)

        # histogram
        axes[0,1].hist(arr, bins=30, color=ACCENT, edgecolor=BG)
        axes[0,1].axvline(arr.mean(), color="#f59e0b", linestyle="--")
        axes[0,1].set_title("ArrDelay Distribution", color=TEXT,
                             fontsize=10, fontweight="bold")
        axes[0,1].set_xlabel("Minutes", color=SUBTEXT, fontsize=8)

        # line / trend
        has_year = "year" in df.columns and df["year"].nunique() > 1
        if has_year:
            grp = df.groupby("year")["arr_delay"].mean().reset_index()
            xv, yv = grp["year"].astype(str), grp["arr_delay"]
        elif df["month"].nunique() > 1:
            grp = df.groupby("month")["arr_delay"].mean().reset_index()
            xv = grp["month"].map(MONTH_NAMES)
            yv = grp["arr_delay"]
        else:
            grp = (df.groupby("carrier_name")["arr_delay"]
                     .mean().nlargest(10).reset_index())
            xv, yv = grp["carrier_name"], grp["arr_delay"]
        xi = range(len(xv))
        axes[1,0].plot(list(xi), list(yv), marker="o", color=ACCENT, linewidth=2)
        axes[1,0].fill_between(list(xi), list(yv), alpha=0.12, color=ACCENT)
        axes[1,0].set_xticks(list(xi))
        axes[1,0].set_xticklabels(list(xv), rotation=20, ha="right", fontsize=7)
        axes[1,0].set_title("Delay Trend", color=TEXT, fontsize=10, fontweight="bold")
        axes[1,0].set_ylabel("Avg delay (min)", color=SUBTEXT, fontsize=8)

        # scatter
        axes[1,1].scatter(s["arr_flights"], s["arr_delay"],
                          alpha=0.25, s=10, color=ACCENT2, edgecolors="none")
        axes[1,1].set_title("Flights vs Delay", color=TEXT,
                             fontsize=10, fontweight="bold")
        axes[1,1].set_xlabel("arr_flights", color=SUBTEXT, fontsize=8)
        axes[1,1].set_ylabel("ArrDelay (min)", color=SUBTEXT, fontsize=8)

        fig.tight_layout()
        out_path = os.path.join("output", "flight_delays_summary.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)

        self.stats_txt.config(state="normal")
        self.stats_txt.delete("1.0", "end")
        self.stats_txt.insert("end", f"Saved → {os.path.abspath(out_path)}")
        self.stats_txt.config(state="disabled")
        messagebox.showinfo("Saved", f"Summary chart saved to:\n{os.path.abspath(out_path)}")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
