import pandas as pd
import geopandas as gpd
from .config import CRIME_CSV, STREETLIGHT_CSV, CTA_BUS_SHP, CITY_LIMITS_SHP, DEFAULT_CRS

def load_crimes(primary_types=None):
    df = pd.read_csv(CRIME_CSV, low_memory=False)

    # Lowercase all columns
    df.columns = df.columns.str.lower()

    # Parse timestamps
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Your data is only 2025
    df = df[df["date"].dt.year == 2025]

    # Crime type filter (optional)
    if primary_types:
        df = df[df["primary_type"].isin(primary_types)]

    # Remove missing coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    # Time components for animation / filters
    df["month"] = df["date"].dt.to_period("M").astype(str)   # e.g. "2025-03"
    df["hour"] = df["date"].dt.hour                          # 0–23
    df["dow"] = df["date"].dt.dayofweek                      # 0=Mon, 6=Sun

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    ).to_crs(epsg=DEFAULT_CRS)

    return gdf

def load_streetlights():
    df = pd.read_csv(STREETLIGHT_CSV, parse_dates=["Creation Date"], low_memory=False)
    df = df.dropna(subset=["Latitude", "Longitude"])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326"
    )
    return gdf.to_crs(epsg=DEFAULT_CRS)

def load_bus_stops():
    gdf = gpd.read_file(CTA_BUS_SHP)
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    return gdf.to_crs(epsg=DEFAULT_CRS)

def load_boundary():
    gdf = gpd.read_file(CITY_LIMITS_SHP)
    return gdf.to_crs(epsg=DEFAULT_CRS)