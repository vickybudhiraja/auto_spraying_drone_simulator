from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

# Input DEM (your cropped DEM)
INPUT_TIF = "myworld/terrain_AW3D30_crop.tif"
OUT_DIR = "myworld"

# Stable output names from now on
COLLISION_TIF = "terrain_collision.tif"
OBJ_NAME = "terrain.obj"
MTL_NAME = "terrain.mtl"
TEXTURE_NAME = "terrain_texture.png"
SDF_NAME = "real_terrain.sdf"

WORLD_NAME = "real_terrain"
WIDTH_M = 1500.0
HEIGHT_M = 1500.0
PAD_RADIUS_M = 50.0
CONTOUR_INTERVAL_M = 2.0


def flatten_center_pad(z: np.ndarray, width_m: float, height_m: float, pad_radius_m: float):
    rows, cols = z.shape
    xs = np.linspace(-width_m / 2.0, width_m / 2.0, cols)
    ys = np.linspace(height_m / 2.0, -height_m / 2.0, rows)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X * X + Y * Y)
    mask = R <= pad_radius_m

    z2 = z.copy()
    valid = np.isfinite(z2)
    pad_valid = mask & valid
    if np.any(pad_valid):
        pad_height = float(np.median(z2[pad_valid]))
        z2[mask] = pad_height
    return z2


def make_texture(z: np.ndarray, out_path: Path):
    valid = np.isfinite(z)
    z_valid = z[valid]
    z_min = float(z_valid.min())
    z_max = float(z_valid.max())
    z_range = max(z_max - z_min, 1e-8)

    zn = (z - z_min) / z_range
    zn[~valid] = 0

    dy, dx = np.gradient(z)
    slope = np.pi / 2.0 - np.arctan(np.sqrt(dx * dx + dy * dy))
    aspect = np.arctan2(-dx, dy)
    az = np.radians(315)
    alt = np.radians(45)
    shade = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
    shade = np.clip(shade, 0, 1)

    # More natural terrain-like colors
    r = 95 + 75 * zn
    g = 110 + 65 * (1 - np.abs(zn - 0.4))
    b = 70 + 35 * (1 - zn)
    rgb = np.stack([r, g, b], axis=-1)
    rgb = rgb * (0.35 + 0.65 * shade[..., None])

    contours = ((z - z_min) % CONTOUR_INTERVAL_M) < 0.12
    rgb[contours] = [35, 30, 25]
    rgb[~valid] = [220, 220, 220]

    # rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    # Image.fromarray(rgb).save(out_path)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    img = Image.fromarray(rgb)
    img = img.resize((2048, 2048), Image.Resampling.BICUBIC)
    img.save(out_path)
    print(f"Saved texture: {out_path}")


def compute_normals(z_local: np.ndarray, dx_m: float, dy_m: float):
    dz_dy, dz_dx = np.gradient(z_local, dy_m, dx_m)
    nx = -dz_dx
    ny = -dz_dy
    nz = np.ones_like(z_local)
    normals = np.stack([nx, ny, nz], axis=-1)
    norm = np.linalg.norm(normals, axis=-1, keepdims=True)
    norm[norm == 0] = 1.0
    return normals / norm


def write_obj_yup(z: np.ndarray, obj_path: Path, mtl_path: Path, texture_name: str):
    rows, cols = z.shape
    valid = np.isfinite(z)
    z_valid = z[valid]
    z_min = float(z_valid.min())
    z_local = z - z_min
    z_local[~valid] = 0.0

    dx_m = WIDTH_M / (cols - 1)
    dy_m = HEIGHT_M / (rows - 1)
    normals = compute_normals(z_local, dx_m, dy_m)

    with obj_path.open("w", encoding="utf-8") as f:
        f.write(f"mtllib {mtl_path.name}\n")
        f.write("o terrain\n")
        f.write("usemtl terrain_material\n")

        # Export in Y-up convention so Gazebo mesh rendering lies flat.
        for r in range(rows):
            y = HEIGHT_M / 2.0 - r * dy_m
            for c in range(cols):
                x = -WIDTH_M / 2.0 + c * dx_m
                z_val = float(z_local[r, c])
                f.write(f"v {x:.6f} {z_val:.6f} {-y:.6f}\n")

        for r in range(rows):
            v = 1.0 - (r / (rows - 1))
            for c in range(cols):
                u = c / (cols - 1)
                f.write(f"vt {u:.6f} {v:.6f}\n")

        # Rotate normals the same way: (nx, nz, -ny)
        for r in range(rows):
            for c in range(cols):
                nx, ny, nz = normals[r, c]
                f.write(f"vn {nx:.6f} {nz:.6f} {-ny:.6f}\n")

        def idx(rr, cc):
            return rr * cols + cc + 1

        for r in range(rows - 1):
            for c in range(cols - 1):
                v1 = idx(r, c)
                v2 = idx(r, c + 1)
                v3 = idx(r + 1, c + 1)
                v4 = idx(r + 1, c)
                f.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                f.write(f"f {v1}/{v1}/{v1} {v3}/{v3}/{v3} {v4}/{v4}/{v4}\n")

    with mtl_path.open("w", encoding="utf-8") as f:
        f.write("newmtl terrain_material\n")
        f.write("Ka 1.0 1.0 1.0\n")
        f.write("Kd 1.0 1.0 1.0\n")
        f.write("Ks 0.0 0.0 0.0\n")
        f.write("d 1.0\n")
        f.write(f"map_Kd {texture_name}\n")

    print(f"Saved OBJ: {obj_path}")
    print(f"Saved MTL: {mtl_path}")
    print(f"Mesh size: rows={rows}, cols={cols}, width={WIDTH_M}m, height={HEIGHT_M}m")
    print(f"Height range: 0 .. {float(z_local.max()):.3f} m")


def write_sdf(out_path: Path):
    sdf = f'''<?xml version="1.0" ?>
<sdf version="1.9">
  <world name="{WORLD_NAME}">
    <physics name="1ms" type="ignored">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <scene>
      <ambient>1 1 1 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>false</shadows>
    </scene>

    <light type="directional" name="sun">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 1000 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.3 0.1 -0.95</direction>
    </light>

    <model name="terrain_model">
      <static>true</static>
      <link name="terrain_link">
        <collision name="terrain_collision">
          <geometry>
            <heightmap>
              <uri>{COLLISION_TIF}</uri>
              <size>{WIDTH_M:.0f} {HEIGHT_M:.0f} 41</size>
              <pos>0 0 0</pos>
              <use_terrain_paging>false</use_terrain_paging>
              <sampling>1</sampling>
            </heightmap>
          </geometry>
        </collision>

        <visual name="terrain_visual">
          <geometry>
            <mesh>
              <uri>{OBJ_NAME}</uri>
            </mesh>
          </geometry>
        </visual>
      </link>
    </model>
  </world>
</sdf>
'''
    out_path.write_text(sdf, encoding="utf-8")
    print(f"Saved SDF: {out_path}")


def main():
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(INPUT_TIF) as src:
        z = src.read(1).astype(np.float32)
        profile = src.profile.copy()

    if not np.any(np.isfinite(z)):
        raise ValueError("DEM has no valid values")

    z_flat = flatten_center_pad(z, WIDTH_M, HEIGHT_M, PAD_RADIUS_M)

    collision_path = out_dir / COLLISION_TIF
    profile.update(dtype="float32", count=1)
    with rasterio.open(collision_path, "w", **profile) as dst:
        dst.write(z_flat.astype(np.float32), 1)
    print(f"Saved collision DEM: {collision_path}")

    texture_path = out_dir / TEXTURE_NAME
    obj_path = out_dir / OBJ_NAME
    mtl_path = out_dir / MTL_NAME
    sdf_path = out_dir / SDF_NAME

    make_texture(z_flat, texture_path)
    write_obj_yup(z_flat, obj_path, mtl_path, TEXTURE_NAME)
    write_sdf(sdf_path)

    valid = z_flat[np.isfinite(z_flat)]
    print(f"Relief after flattening: {float(valid.max() - valid.min()):.3f} m")


if __name__ == "__main__":
    main()
