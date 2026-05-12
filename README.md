# Analiza e Vonesave të Fluturimeve

Projekt Python për analizimin dhe vizualizimin e të dhënave mbi vonesat e fluturimeve duke përdorur **Pandas** dhe **Matplotlib**.

## Dataset

Fajlli `data/flight_delays_dataset.csv` përmban të dhëna reale të mbërrirjeve të fluturimeve sipas operatorit dhe aeroportit, me kolonat kryesore:

| Kolona | Përshkrim |
|---|---|
| `month` | Muaji (1–12) |
| `carrier_name` | Emri i operatorit |
| `airport` | Kodi i aeroportit |
| `arr_delay` | Vonesa totale e mbërritjes (minuta) |
| `carrier_delay` | Vonesa nga operatori |
| `weather_delay` | Vonesa nga moti |
| `nas_delay` | Vonesa nga sistemi kombëtar ajror |
| `security_delay` | Vonesa nga siguria |
| `late_aircraft_delay` | Vonesa nga avioni i vonuar |
| `arr_cancelled` | Numri i fluturimeve të anuluara |

## Struktura

```
flight-delays-analysis/
├── analysis.py                  # Skripti kryesor (të gjitha 8 detyrat)
├── requirements.txt
├── data/
│   └── flight_delays_dataset.csv
└── output/                      # Grafikët e gjeneruar (.png)
```

## Si ta ekzekutosh

```bash
# 1. Instalo varësitë
pip install -r requirements.txt

# 2. Ekzekuto analizën
python analysis.py
```

## Detyrat e Implementuara

| # | Detyrë | Grafiku |
|---|---|---|
| 1 | Leximi i dataset-it – shfaqja e 10 rreshtave të parë | — |
| 2 | Pastrim: heqja e fluturimeve të anuluara | — |
| 3 | Bar chart – totali i vonesave sipas shkakut | `task3_bar_delay_causes.png` |
| 4 | Histogram – shpërndarja e ArrDelay | `task4_histogram_arrdelay.png` |
| 5 | Scatter plot – numri i fluturimeve vs ArrDelay | `task5_scatter_flights_vs_delay.png` |
| 6 | Line plot – vonesa mesatare mujore | `task6_line_monthly_delay.png` |
| 7 | Analiza: muaji me vonesën më të lartë, shkaku kryesor, korrelacioni | — |
| 8 | Grafik permbledhes i ruajtur si `.png` | `flight_delays_summary.png` |

> **Shënim detyrë 5:** Dataseti nuk përfshin kolonën `distance`. Kolona `arr_flights` (numri i fluturimeve) përdoret si variabël alternativ për të treguar lidhjen mes volumit të fluturimeve dhe vonesës.
