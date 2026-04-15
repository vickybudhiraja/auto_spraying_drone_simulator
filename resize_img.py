from PIL import Image
import os

INPUT_PATH = "/home/vicky/Pictures/Screenshots/Screenshot from 2026-04-15 20-24-08.png"
OUTPUT_PATH = "myworld/sat_patch.png"
OUTPUT_SIZE = 2048

def crop_center_square(img: Image.Image) -> Image.Image:
    width, height = img.size
    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2
    right = left + side
    bottom = top + side

    return img.crop((left, top, right, bottom))

def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input image not found: {INPUT_PATH}")

    img = Image.open(INPUT_PATH).convert("RGB")
    square = crop_center_square(img)
    resized = square.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
    resized.save(OUTPUT_PATH)

    print(f"Saved: {OUTPUT_PATH}")
    print(f"Original size: {img.size}")
    print(f"Square crop size: {square.size}")
    print(f"Output size: {resized.size}")

if __name__ == "__main__":
    main()