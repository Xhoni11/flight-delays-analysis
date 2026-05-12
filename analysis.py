import sys
import os

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. Lexo dataset-in dhe shfaq 10 rreshtat e parë ──────────────────────────
print("=" * 60)
print("TASK 1 – Leximi i dataset-it (10 rreshtat e parë)")
print("=" * 60)

df = pd.read_csv("data/flight_delays_dataset.csv")
print(df.head(10).to_string())
print(f"\nDimensionet: {df.shape[0]} rreshta × {df.shape[1]} kolona")

# ── 2. Pastrim minimal i të dhënave ──────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 2 – Pastrim: hiqen fluturimet e anuluara")
print("=" * 60)

before = len(df)
df_clean = df[df["arr_cancelled"] == 0].copy()
print(f"Para pastrimit : {before:,} rreshta")
print(f"Pas pastrimit  : {len(df_clean):,} rreshta")
print(f"Hequr          : {before - len(df_clean):,} rreshta (arr_cancelled > 0)")

delay_cols = ["carrier_delay", "weather_delay", "nas_delay",
              "security_delay", "late_aircraft_delay"]
df_clean[delay_cols] = df_clean[delay_cols].fillna(0)
df_clean["arr_delay"] = df_clean["arr_delay"].fillna(0)

# ── 3. Bar chart – shkaqet e vonesave ────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 3 – Bar chart: totali i çdo shkaku vonese")
print("=" * 60)

totals = df_clean[delay_cols].sum()
labels = ["Carrier", "Weather", "NAS", "Security", "Late Aircraft"]
colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974"]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(labels, totals / 1e6, color=colors, edgecolor="white", linewidth=0.6)
ax.set_title("Totali i Vonesave sipas Shkakut", fontsize=14, fontweight="bold")
ax.set_xlabel("Shkaku i Vonesës")
ax.set_ylabel("Vonesa totale (miliona minuta)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}M"))
for bar, val in zip(bars, totals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"{val/1e6:.1f}M", ha="center", va="bottom", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/task3_bar_delay_causes.png", dpi=150)
plt.show()
print("Grafiku i ruajtur: output/task3_bar_delay_causes.png")
for lbl, val in zip(labels, totals):
    print(f"  {lbl:<15}: {val:>12,.0f} min")

# ── 4. Histogram – ArrDelay ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 4 – Histogram: shpërndarja e ArrDelay")
print("=" * 60)

arr = df_clean["arr_delay"].dropna()
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(arr, bins=40, color="#4C72B0", edgecolor="white", linewidth=0.5)
ax.set_title("Shpërndarja e Vonesave të Mbërritjes (ArrDelay)", fontsize=14, fontweight="bold")
ax.set_xlabel("Vonesa totale (minuta)")
ax.set_ylabel("Numri i grupeve")
ax.axvline(arr.mean(), color="crimson", linestyle="--", linewidth=1.4,
           label=f"Mesatare: {arr.mean():.1f} min")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/task4_histogram_arrdelay.png", dpi=150)
plt.show()
print(f"Vonesa mesatare: {arr.mean():.1f} min | Mediana: {arr.median():.1f} min")

# ── 5. Scatter plot – arr_flights vs arr_delay ────────────────────────────────
print("\n" + "=" * 60)
print("TASK 5 – Scatter plot: Numri i Fluturimeve vs ArrDelay")
print("=" * 60)
print("(Dataseti nuk ka kolonë 'distance'; përdoret arr_flights si proxy)")

scatter_df = df_clean[["arr_flights", "arr_delay"]].dropna()
fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(scatter_df["arr_flights"], scatter_df["arr_delay"],
           alpha=0.3, s=15, color="#4C72B0", edgecolors="none")
ax.set_title("Numri i Fluturimeve vs Vonesa Totale (ArrDelay)", fontsize=14, fontweight="bold")
ax.set_xlabel("Numri i fluturimeve (arr_flights)")
ax.set_ylabel("Vonesa totale (minuta)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/task5_scatter_flights_vs_delay.png", dpi=150)
plt.show()

# ── 6. Line plot – vonesa mesatare mujore ────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 6 – Line plot: vonesa mesatare sipas muajit")
print("=" * 60)

monthly = df_clean.groupby("month")["arr_delay"].mean().reset_index()
month_names = {1:"Jan", 2:"Shk", 3:"Mar", 4:"Pri", 5:"Maj", 6:"Qer",
               7:"Kor", 8:"Gus", 9:"Sht", 10:"Tet", 11:"Nën", 12:"Dhj"}
monthly["month_name"] = monthly["month"].map(month_names)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["month"], monthly["arr_delay"], marker="o",
        color="#4C72B0", linewidth=2, markersize=6)
ax.set_title("Vonesa Mesatare e Mbërritjes sipas Muajit", fontsize=14, fontweight="bold")
ax.set_xlabel("Muaji")
ax.set_ylabel("Vonesa mesatare (min)")
ax.set_xticks(monthly["month"])
ax.set_xticklabels(monthly["month_name"])
ax.spines[["top", "right"]].set_visible(False)
ax.fill_between(monthly["month"], monthly["arr_delay"], alpha=0.1, color="#4C72B0")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/task6_line_monthly_delay.png", dpi=150)
plt.show()

# ── 7. Analiza statistikore ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 7 – Analiza statistikore")
print("=" * 60)

# Muaji me vonesën më të lartë
worst_month_row = monthly.loc[monthly["arr_delay"].idxmax()]
worst_month_num = int(worst_month_row["month"])
print(f"\n>> Muaji me vonesen me te larte:")
print(f"   Muaji {worst_month_num} ({month_names[worst_month_num]}) - "
      f"{worst_month_row['arr_delay']:.1f} min mesatarisht")

# Shkaku me i zakonshëm
cause_totals = df_clean[delay_cols].sum()
top_cause = cause_totals.idxmax()
top_cause_label = top_cause.replace("_delay", "").replace("_", " ").title()
print(f"\n>> Shkaku me i zakonshëm i vonesës:")
print(f"   {top_cause_label} - {cause_totals[top_cause]:,.0f} min total")
for col, lbl in zip(delay_cols, ["Carrier", "Weather", "NAS", "Security", "Late Aircraft"]):
    print(f"   {lbl:<15}: {cause_totals[col]:>12,.0f} min")

# Lidhja mes numrit te fluturimeve dhe vonesës
corr = df_clean["arr_flights"].corr(df_clean["arr_delay"])
print(f"\n>> Lidhja mes numrit te fluturimeve dhe vonesës:")
print(f"   Koeficienti i korrelacionit Pearson: {corr:.3f}")
if corr > 0.3:
    print("   -> Lidhje pozitive: rrutet me me shume fluturime priren te kene me shume vonesa.")
elif corr < -0.3:
    print("   -> Lidhje negative e moderuar.")
else:
    print("   -> Lidhje e dobet ose e parendësishme.")

# ── 8. Ruaj grafik si .png ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 8 – Grafiku kryesor i ruajtur si .png")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Analiza e Vonesave të Fluturimeve", fontsize=16, fontweight="bold", y=1.01)

# Panel 1 – Bar chart
axes[0, 0].bar(labels, totals / 1e6, color=colors, edgecolor="white", linewidth=0.6)
axes[0, 0].set_title("Totali sipas Shkakut")
axes[0, 0].set_ylabel("Miliona minuta")
axes[0, 0].tick_params(axis="x", labelsize=8)
axes[0, 0].spines[["top", "right"]].set_visible(False)

# Panel 2 – Histogram
axes[0, 1].hist(arr, bins=30, color="#4C72B0", edgecolor="white", linewidth=0.4)
axes[0, 1].axvline(arr.mean(), color="crimson", linestyle="--", linewidth=1.2)
axes[0, 1].set_title("Shpërndarja e ArrDelay")
axes[0, 1].set_xlabel("Minuta")
axes[0, 1].spines[["top", "right"]].set_visible(False)

# Panel 3 – Line plot
axes[1, 0].plot(monthly["month"], monthly["arr_delay"], marker="o",
                color="#4C72B0", linewidth=2)
axes[1, 0].fill_between(monthly["month"], monthly["arr_delay"], alpha=0.1, color="#4C72B0")
axes[1, 0].set_title("Vonesa Mesatare Mujore")
axes[1, 0].set_xlabel("Muaji")
axes[1, 0].set_ylabel("Minuta")
axes[1, 0].set_xticks(monthly["month"])
axes[1, 0].set_xticklabels([str(m) for m in monthly["month"]], fontsize=8)
axes[1, 0].spines[["top", "right"]].set_visible(False)

# Panel 4 – Scatter
axes[1, 1].scatter(scatter_df["arr_flights"], scatter_df["arr_delay"],
                   alpha=0.25, s=10, color="#4C72B0", edgecolors="none")
axes[1, 1].set_title("Fluturime vs Vonesa")
axes[1, 1].set_xlabel("arr_flights")
axes[1, 1].set_ylabel("ArrDelay (min)")
axes[1, 1].spines[["top", "right"]].set_visible(False)

plt.tight_layout()
main_png = f"{OUTPUT_DIR}/flight_delays_summary.png"
plt.savefig(main_png, dpi=150, bbox_inches="tight")
plt.show()
print(f"Grafiku kryesor i ruajtur: {main_png}")
print("\n✓ Të gjitha 8 detyrat u kryen me sukses!")
