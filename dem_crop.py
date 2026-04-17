import math
import numpy as np
import rasterio
from rasterio.windows import from_bounds

INPUT_TIF = "myworld/terrain_AW3D30.tif"
OUTPUT_TIF = "myworld/terrain_AW3D30_crop.tif"

CENTER_LAT = 28.613333333325453
CENTER_LON = 77.27694444448068
SIDE_M = 1500.0

def meters_to_deg_lat(m):
    return m / 111320.0

def meters_to_deg_lon(m, lat_deg):
    return m / (111320.0 * math.cos(math.radians(lat_deg)))

with rasterio.open(INPUT_TIF) as src:
    if str(src.crs) != "EPSG:4326":
        raise ValueError(f"This minimal script only supports EPSG:4326 DEMs. Found: {src.crs}")

    print("Bounds:", src.bounds)

    if not (src.bounds.bottom <= CENTER_LAT <= src.bounds.top and src.bounds.left <= CENTER_LON <= src.bounds.right):
        raise ValueError("CENTER_LAT / CENTER_LON is outside the DEM bounds")

    half = SIDE_M / 2.0
    dlat = meters_to_deg_lat(half)
    dlon = meters_to_deg_lon(half, CENTER_LAT)

    min_lon = CENTER_LON - dlon
    max_lon = CENTER_LON + dlon
    min_lat = CENTER_LAT - dlat
    max_lat = CENTER_LAT + dlat

    if min_lon < src.bounds.left or max_lon > src.bounds.right or min_lat < src.bounds.bottom or max_lat > src.bounds.top:
        raise ValueError("Requested crop goes outside the DEM. Use a smaller SIDE_M or a different center.")

    window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
    window = window.round_offsets().round_lengths()

    data = src.read(1, window=window).astype(np.float32)
    transform_out = src.window_transform(window)

    profile = src.profile.copy()
    profile.update({
        "height": data.shape[0],
        "width": data.shape[1],
        "transform": transform_out,
        "dtype": "float32",
        "count": 1,
    })

    with rasterio.open(OUTPUT_TIF, "w", **profile) as dst:
        dst.write(data, 1)

    valid = data[np.isfinite(data)]
    dem_min = float(valid.min())
    dem_max = float(valid.max())
    relief = dem_max - dem_min

    print(f"Saved cropped DEM: {OUTPUT_TIF}")
    print(f"Cropped shape: {data.shape}")
    print(f"Min elevation: {dem_min:.3f} m")
    print(f"Max elevation: {dem_max:.3f} m")
    print(f"Relief: {relief:.3f} m")
    print(f"Suggested SDF size tag: <size>{SIDE_M:.3f} {SIDE_M:.3f} {relief:.3f}</size>")