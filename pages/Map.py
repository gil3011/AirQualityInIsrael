import streamlit as st
import pandas as pd
import numpy as np
from pyproj import Transformer
import pydeck as pdk
from math import radians, sin, cos, sqrt, atan2
st.set_page_config(layout="wide")
df_cities = pd.read_csv("Data/cities.csv")
df_stations = pd.read_csv("Data/stations.csv")

# Clean column names
df_stations.columns = df_stations.columns.str.strip()
df_cities.columns = df_cities.columns.str.strip()

# Drop rows with missing coordinates
df_cities = df_cities.dropna(subset=["x", "y"])
df_stations = df_stations.dropna(subset=["X", "Y"])

# Coordinate transformer: ITM (EPSG:2039) → WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:2039", "EPSG:4326", always_xy=True)

def convert_coords(x, y):
    lon, lat = transformer.transform(x, y)
    return lat, lon

# Convert coordinates
df_cities[["lat", "lon"]] = df_cities.apply(lambda row: pd.Series(convert_coords(row["x"], row["y"])), axis=1)
df_stations[["lat", "lon"]] = df_stations.apply(lambda row: pd.Series(convert_coords(row["X"], row["Y"])), axis=1)

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# UI
st.title("מפת תחנות ויישובים")
st.markdown("""
    <style>
    body, .reportview-container, .main {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)
# Select city
city_names = df_cities["יישוב"].unique()
selected_city = st.selectbox("בחר יישוב", city_names)

# Get selected city coordinates
city_row = df_cities[df_cities["יישוב"] == selected_city].iloc[0]
city_lat, city_lon = city_row["lat"], city_row["lon"]

# Compute distances to stations
df_stations["distance_km"] = df_stations.apply(
    lambda row: haversine(city_lat, city_lon, row["lat"], row["lon"]), axis=1
)

nearby_stations = df_stations[df_stations["distance_km"] <= 20].copy()

# Prepare map data
city_point = pd.DataFrame([{
    "station": selected_city,
    "pollutant": "City",
    "lat": city_lat,
    "lon": city_lon,
    "color": [0, 0, 255, 160]  # Blue
}])
# Identify pollutants per station
pollutants = ["O3", "PM2.5", "PM10", "NOx", "SO2", "TEMP"]
def extract_pollutants(row):
    return ", ".join([p for p in pollutants if row.get(p) == 1])

df_stations["pollutants"] = df_stations.apply(extract_pollutants, axis=1)
all_stations = df_stations.copy()
all_stations["station"] = all_stations["שם התחנה החדש"]
all_stations["pollutant"] = all_stations["pollutants"]
all_stations["color"] = [[255, 0, 0, 80]] * len(all_stations)

nearby_stations["station"] = nearby_stations["שם התחנה החדש"]
nearby_stations["pollutant"] = "Nearby Station"
nearby_stations["color"] = [[255, 0, 0, 200]] * len(nearby_stations)  # Darker red

map_data = pd.concat([
    city_point,
    all_stations[["station", "pollutant", "lat", "lon", "color"]],
], ignore_index=True)

# Show map
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=city_lat,
        longitude=city_lon,
        zoom=10,
        pitch=0,
        tooltip={"text": "{station}\nPollutants: {pollutant}"}
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=600,
            pickable=True,
        )
    ],
    tooltip={"text": "{station}\n{pollutant}"}
))

st.subheader(f"📍 תחנות בטווח 20 ק\"מ מ־{selected_city}")
st.dataframe(nearby_stations[["שם התחנה החדש", "distance_km", "lat", "lon"]].sort_values("distance_km"))