# 🌍 Air Quality Dashboard (Streamlit App)

This interactive Streamlit dashboard visualizes and analyzes air pollution data across different seasons, times, and monitoring stations in Israel. It supports Hebrew RTL layout and provides statistical insights and visualizations for pollutants like O₃, NOx, PM10, PM2.5, SO₂, and temperature.

---

## 📁 Project Structure

```
project/
│
├── Data/
│   ├── O3_raw_data.csv
│   ├── NOx_raw_data.csv
│   ├── PM10_raw_data.csv
│   ├── PM25_raw_data.csv
│   ├── SO2_raw_data.csv
│   ├── TEMP_raw_data.csv
│   ├── cities.csv
│   ├── stations.csv
│   ├── season_data.csv
├── Pages/
│   ├── Map.py              # Map of cities and nearby stations
│   ├── Pollutant comprihention.py        # Pollutant correlation and pairwise comparison
├── AirQuality.py              # Main dashboard page
└── README.md
```
---

## 🚀 Features

### 🔹 Page 1: **Main Dashboard**
- UI with pollutant selection.
- Seasonal analysis:
  - Boxplots and KDE plots by season.
  - Mann-Whitney U tests for seasonal distributions.
- Hourly & weekly patterns:
  - Heatmap of pollutant levels by hour and weekday.
- Station-based analysis:
  - Multi-station selection.
  - Monthly average and max trends.
  - KDE and boxplots for station-level distributions.
  - Date range filtering.

### 🔹 Page 2: **Station Map**
- Interactive map of cities and monitoring stations.
- Visualization using PyDeck:
  - City marked in blue.
  - Nearby stations in dark red.
  - All stations in light red.
- Table of stations within 20 km of selected city.

### 🔹 Page 3: **Pollutant Comparison**
- Correlation matrix between pollutants.
- Pairwise pollutant comparison (MinMax scaled):
  - KDE plots
  - Boxplots
  - Scatter plots with year-based hue
- Mann-Whitney U test for statistical significance between pollutant pairs.
---

## 📊 Visualizations

- 📦 Boxplots
- 🌈 KDE (Kernel Density Estimation)
- 🔥 Heatmaps
- 📈 Line plots (monthly trends)
- 🗺️ Interactive maps (PyDeck)
- 🧮 Correlation matrices
- 📉 Scatter plots

---

## 🛠️ Requirements

Install dependencies with:

```bash
pip install streamlit pandas seaborn matplotlib scipy pydeck pyproj scikit-learn
```

---

## ▶️ Running the App

```bash
streamlit run AirQuality.py         # Main dashboard - leads to the other pages
```

---

## 📷 Screenshots

<img width="811" height="576" alt="image" src="https://github.com/user-attachments/assets/d5fb137b-2e74-4822-8f2b-b2d26e7f9b33" />
<img width="596" height="680" alt="image" src="https://github.com/user-attachments/assets/0f3f0fbf-46e5-4e62-9b1f-7339fd12892b" />
<img width="594" height="595" alt="image" src="https://github.com/user-attachments/assets/d864a3d5-432f-4770-9ddd-1e2196c69dc6" />

---
