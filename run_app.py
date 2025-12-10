from dash import Dash
import dash_bootstrap_components as dbc

# Your files are named layout.py and callbacks.py
from app.layout import build_layout
from app.callbacks import register_callbacks

# Load crime types from gdf inside maps.py
from app.maps import gdf


# Extract crime types dynamically

def extract_crime_types():
    crime_cols = [c for c in gdf.columns if c.startswith("crime_")]
    crime_cols = [c for c in crime_cols if c != "crime_count_total"]
    crime_types = [c.replace("crime_", "").upper() for c in crime_cols]
    return sorted(crime_types)


crime_types = extract_crime_types()


# Create Dash app

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Chicago Crime Analysis 2025",
)

# Layout (lazy-loaded)
app.layout = lambda: build_layout(crime_types)

# Register callbacks
register_callbacks(app)


# Run Dash (Dash >3.0 uses app.run(), not run_server)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)