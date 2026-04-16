import rasterio
import numpy as np
from PIL import Image

INPUT_TIF = "myworld/output_AW3D30.tif"
OUTPUT_PNG = "myworld/output_AW3D30_preview.png"

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