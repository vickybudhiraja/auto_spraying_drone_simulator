import rasterio
import numpy as np
from PIL import Image
from rasterio.warp import transform_bounds


INPUT_TIF = "myworld/terrain_AW3D30.tif"
OUTPUT_PNG = "myworld/terrain_AW3D30_preview.png"

with rasterio.open(INPUT_TIF) as src:
    dem = src.read(1).astype(np.float32)

    dem_min = np.nanmin(dem)
    dem_max = np.nanmax(dem)

    norm = (dem - dem_min) / (dem_max - dem_min + 1e-8)
    img = (norm * 255).astype(np.uint8)

    Image.fromarray(img).save(OUTPUT_PNG)

    print("Saved preview:", OUTPUT_PNG)
    print("Min elevation:", dem_min)
    print("Max elevation:", dem_max)


with rasterio.open(INPUT_TIF) as src:
    print("CRS:", src.crs)
    print("Original bounds:", src.bounds)

    bounds_wgs84 = transform_bounds(src.crs, "EPSG:4326",
                                    src.bounds.left, src.bounds.bottom,
                                    src.bounds.right, src.bounds.top)

    min_lon, min_lat, max_lon, max_lat = bounds_wgs84

    center_lon = (min_lon + max_lon) / 2.0
    center_lat = (min_lat + max_lat) / 2.0

    print("WGS84 bounds:")
    print("  min_lat:", min_lat)
    print("  min_lon:", min_lon)
    print("  max_lat:", max_lat)
    print("  max_lon:", max_lon)

    print("Center:")
    print("  lat:", center_lat)
    print("  lon:", center_lon)