import geopandas as gpd
import pandas as pd
from geopandas.tools import sjoin

from .load_data import (
    load_crimes,
    load_streetlights,
    load_bus_stops
)
from .config import GRID_FILE, FEATURES_FILE, MONTHLY_FILE

DEFAULT_CRIME_TYPES = ["BURGLARY", "ROBBERY", "ASSAULT"]


def count_points(points_gdf, grid_gdf):
    """
    Spatial join: count how many point features fall inside each grid cell.
    """
    joined = sjoin(
        points_gdf,
        grid_gdf[["cell_id", "geometry"]],
        how="left",
        predicate="within",
    )
    return joined.groupby("cell_id").size().rename("count")


def aggregate_features(primary_types=None):

    if primary_types is None:
        primary_types = DEFAULT_CRIME_TYPES

    # LOAD GRID (and FIX pyogrio/GPKG hidden-FID bug)

    grid = gpd.read_file(GRID_FILE)

    grid = grid.copy()
    grid = gpd.GeoDataFrame(grid, geometry="geometry")
    grid.reset_index(drop=True, inplace=True)
    grid.columns = grid.columns.astype(str)

    print("\n[AGGREGATE DEBUG] Loaded grid from disk:")
    print("[AGGREGATE DEBUG] Columns:", grid.columns)
    print("[AGGREGATE DEBUG] Rows:", len(grid))

    # LOAD CRIMES + CONTEXT FEATURES

    crimes = load_crimes(primary_types=None)   # all crimes for temporal stats
    lights = load_streetlights()
    bus = load_bus_stops()

    # filter crimes for the selected types
    crimes_sel = crimes[crimes["primary_type"].isin(primary_types)]

    # AGGREGATE COUNTS (WITHOUT EVER SETTING INDEX)

    grid["crime_count_total"] = (
        count_points(crimes_sel, grid)
        .reindex(grid["cell_id"])
        .fillna(0)
        .astype(int)
    )

    grid["streetlight_count"] = (
        count_points(lights, grid)
        .reindex(grid["cell_id"])
        .fillna(0)
        .astype(int)
    )

    grid["bus_count"] = (
        count_points(bus, grid)
        .reindex(grid["cell_id"])
        .fillna(0)
        .astype(int)
    )

    # per-crime-type counts
    for ctype in primary_types:
        subset = crimes[crimes["primary_type"] == ctype]
        grid[f"crime_{ctype.lower()}"] = (
            count_points(subset, grid)
            .reindex(grid["cell_id"])
            .fillna(0)
            .astype(int)
        )

    # TEMPORAL CRIME TABLE

    # grid with both geometry + id for joins
    grid_reset = grid[["cell_id", "geometry"]].copy()

    crimes_with_cell = sjoin(
        crimes,
        grid_reset,
        how="left",
        predicate="within",
    )

    crimes_with_cell = crimes_with_cell.dropna(subset=["cell_id"])
    crimes_with_cell["cell_id"] = crimes_with_cell["cell_id"].astype(int)

    # ensure hour & dow
    crimes_with_cell["hour"] = crimes_with_cell["date"].dt.hour
    crimes_with_cell["dow"] = crimes_with_cell["date"].dt.dayofweek

    monthly = (
        crimes_with_cell
        .groupby(["cell_id", "month", "hour", "dow", "primary_type"])
        .size()
        .rename("crime_count")
        .reset_index()
    )

    # SAVE OUTPUTS
    
    FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)
    grid.to_parquet(FEATURES_FILE)

    MONTHLY_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_FILE)

    return grid, monthly, primary_types