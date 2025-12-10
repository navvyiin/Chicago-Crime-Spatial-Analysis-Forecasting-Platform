import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression

try:
    # mgwr is optional; we guard usage in the pipeline
    from mgwr.gwr import GWR
    from mgwr.sel_bw import Sel_BW
    MGWR_AVAILABLE = True
except Exception:
    MGWR_AVAILABLE = False


# Random Forest

def fit_rf(features_gdf: pd.DataFrame):
    """
    Fit a RandomForest model to predict crime_count_total from
    environmental and crime-type features.
    """
    df = features_gdf.copy()
    df = df[df["crime_count_total"].notna()]

    candidate_cols = [
        "streetlight_count",
        "bus_count",
        "crime_burglary",
        "crime_robbery",
        "crime_assault",
    ]
    X_cols = [c for c in candidate_cols if c in df.columns]

    if not X_cols:
        raise ValueError("No predictor columns available for Random Forest.")

    X = df[X_cols].values
    y = df["crime_count_total"].values

    rf = RandomForestRegressor(
        n_estimators=250,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X, y)

    preds = rf.predict(features_gdf[X_cols].fillna(0).values)
    features_gdf["pred_rf"] = preds

    print("Random Forest fitted.")
    return rf, features_gdf


# MGWR (for smaller grids)

def fit_gwr(features_gdf):
    """
    Fit a GWR model only when grid size is modest (< ~6000 cells).
    Assumes CRS is projected (metres).
    """
    if not MGWR_AVAILABLE:
        raise RuntimeError("MGWR is not available in this environment.")

    df = features_gdf.copy()
    df = df[df["crime_count_total"].notna()].copy()

    # Predictors we use in GWR: keep it lean
    X_cols = [c for c in ["streetlight_count", "bus_count"] if c in df.columns]
    if not X_cols:
        raise ValueError("No predictors available for GWR.")

    # Coordinates in projected CRS
    centroids = df.geometry.centroid
    coords = np.column_stack([centroids.x.values, centroids.y.values])

    y = df["crime_count_total"].values.reshape(-1, 1)
    X = df[X_cols].values

    bw = Sel_BW(coords, y, X).search()
    gwr_model = GWR(coords, y, X, bw=bw).fit()

    betas = gwr_model.params  # shape (n, k+1) intercept + slopes

    # Map betas back into original features_gdf
    df = df.copy()
    df["coef_intercept"] = betas[:, 0]
    if len(X_cols) >= 1:
        df["coef_streetlight"] = betas[:, 1]
    if len(X_cols) >= 2:
        df["coef_bus"] = betas[:, 2]

    # Merge coefficients back into main GeoDataFrame
    features_gdf = features_gdf.merge(
        df[["cell_id", "coef_intercept"] + [c for c in ["coef_streetlight", "coef_bus"] if c in df.columns]],
        on="cell_id",
        how="left",
    )

    # Use fitted values as a "GWR prediction"
    features_gdf["pred_gwr"] = np.nan
    features_gdf.loc[df.index, "pred_gwr"] = gwr_model.predy.ravel()

    print("GWR model fitted successfully.")
    return gwr_model, features_gdf


# Local Linear Fallback (for large grids)

def fit_local_linear(features_gdf, k: int = 60):
    """
    Lightweight local linear regression as a GWR fallback
    for large grids where MGWR is too slow/unstable.

    For each cell, fit a linear model on its k nearest neighbours
    using (streetlight_count, bus_count) to predict crime_count_total.
    """
    df = features_gdf.copy()
    df = df[df["crime_count_total"].notna()].copy()

    X_cols = [c for c in ["streetlight_count", "bus_count"] if c in df.columns]
    if not X_cols:
        raise ValueError("No predictors available for local linear model.")

    # Coordinates from centroids
    centroids = df.geometry.centroid
    coords = np.column_stack([centroids.x.values, centroids.y.values])

    X = df[X_cols].values
    y = df["crime_count_total"].values

    k = min(k, len(df))
    nn = NearestNeighbors(n_neighbors=k).fit(coords)
    neigh_idx = nn.kneighbors(coords, return_distance=False)

    preds = np.zeros(len(df), dtype=float)

    for i in range(len(df)):
        idx = neigh_idx[i]
        Xi = X[idx]
        yi = y[idx]
        lr = LinearRegression().fit(Xi, yi)
        preds[i] = lr.predict(X[i].reshape(1, -1))[0]

    df["pred_llm"] = preds

    # Merge back to main GeoDataFrame
    features_gdf = features_gdf.merge(
        df[["cell_id", "pred_llm"]],
        on="cell_id",
        how="left",
    )
    # Use pred_llm as pred_gwr-style column
    features_gdf["pred_gwr"] = features_gdf["pred_llm"]

    print("Local Linear model fitted as GWR fallback.")
    return features_gdf