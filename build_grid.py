import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import geopandas as gpd
import numpy as np

from .config import GRID_FILE


def _hexagon(cx: float, cy: float, radius: float) -> Polygon:
    """
    Build a regular hexagon centred at (cx, cy) with given radius.
    Radius is distance from centre to any vertex (in CRS units, here metres).
    """
    angles = np.linspace(0, 2 * math.pi, 7)
    points = [
        (cx + radius * math.cos(a), cy + radius * math.sin(a))
        for a in angles
    ]
    return Polygon(points)


def build_hex_grid(boundary: gpd.GeoDataFrame, hex_diameter: float = 100.0) -> gpd.GeoDataFrame:
    """
    Build a hexagonal grid covering the city boundary, then clip to boundary.

    Parameters
    ----------
    boundary : GeoDataFrame
        City polygon(s) in a projected CRS (metres).
    hex_diameter : float
        Diameter of hexagon in CRS units (metres).

    Returns
    -------
    GeoDataFrame with columns: geometry, cell_id
    """
    boundary = boundary.to_crs(boundary.crs)  # no-op, just being explicit

    radius = hex_diameter / 2.0
    # horizontal spacing between centres
    w = 3 * radius
    # vertical spacing between rows (for pointy-top hexes)
    h = math.sqrt(3) * radius

    minx, miny, maxx, maxy = boundary.total_bounds

    hexes = []
    y = miny
    row = 0

    while y <= maxy + h:
        # Offset every other row
        x = minx + (0 if row % 2 == 0 else 1.5 * radius)
        while x <= maxx + w:
            hexes.append(_hexagon(x, y, radius))
            x += w
        y += h
        row += 1

    grid = gpd.GeoDataFrame({"geometry": hexes}, crs=boundary.crs)

    # Clip to the city boundary (dissolve multiple polygons first)
    boundary_union = unary_union(boundary.geometry)
    clip_gdf = gpd.GeoDataFrame(geometry=[boundary_union], crs=boundary.crs)
    grid = gpd.overlay(grid, clip_gdf, how="intersection")

    # Remove degenerate cells
    grid = grid[grid.geometry.is_valid & (grid.geometry.area > 0)].copy()

    grid.reset_index(drop=True, inplace=True)
    grid["cell_id"] = grid.index.astype(int)

    return grid


def build_and_save_grid(boundary: gpd.GeoDataFrame, hex_diameter: float = 100.0) -> gpd.GeoDataFrame:
    """
    Wrapper: build the hex grid and save to GRID_FILE.

    Returns the grid GeoDataFrame.
    """
    grid = build_hex_grid(boundary, hex_diameter=hex_diameter)

    GRID_FILE.parent.mkdir(parents=True, exist_ok=True)
    grid.to_file(GRID_FILE, driver="GPKG")

    print(f"[DEBUG] Built grid with rows: {len(grid)}")
    print(f"[DEBUG] Grid columns: {grid.columns}")
    print(f"[DEBUG] Saving grid to: {GRID_FILE}")
    print("[DEBUG] Grid saved successfully.")
    return grid