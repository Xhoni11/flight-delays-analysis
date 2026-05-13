# Analiza e Vonesave të Fluturimeve

Ky projekt në Python analizon dhe vizualizon të dhënat mbi vonesat e fluturimeve, duke përdorur bibliotekat **Pandas** dhe **Matplotlib**.

Qëllimi i projektit është të kuptohet se cilët faktorë ndikojnë më shumë në vonesat e mbërritjes, si ndryshojnë vonesat sipas muajve dhe çfarë lidhjeje ka numri i fluturimeve me kohën e vonesës.

## Dataset

Fajlli `data/flight_delays_dataset.csv` përmban të dhëna mbi fluturimet, operatorët ajrorë, aeroportet dhe shkaqet kryesore të vonesave.

Kolonat kryesore të dataset-it janë:

| Kolona | Përshkrim |
|---|---|
| `month` | Muaji i fluturimit, nga 1 deri në 12 |
| `carrier_name` | Emri i operatorit ajror |
| `airport` | Kodi i aeroportit |
| `arr_delay` | Vonesa totale e mbërritjes në minuta |
| `carrier_delay` | Vonesa të shkaktuara nga operatori |
| `weather_delay` | Vonesa të shkaktuara nga kushtet atmosferike |
| `nas_delay` | Vonesa nga sistemi kombëtar ajror |
| `security_delay` | Vonesa të lidhura me sigurinë |
| `late_aircraft_delay` | Vonesa nga mbërritja me vonesë e avionit të mëparshëm |
| `arr_cancelled` | Numri i fluturimeve të anuluara |

## Struktura e Projektit

```text
flight-delays-analysis/
├── analysis.py                  # Skripti kryesor i analizës
├── requirements.txt             # Bibliotekat e nevojshme
├── data/
│   └── flight_delays_dataset.csv
└── output/                      # Grafikët e gjeneruar në format .png
