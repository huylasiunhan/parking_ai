"""Visualize dataset images with bounding boxes and parking slot polygons.

References:
- docs/03_DATASET_SPEC.md (Section 6: Quality checks / Visualizer)
"""

import argparse
import json
import random
from pathlib import Path
from PIL import Image, ImageDraw


CLASS_COLORS = {
    0: "red",     # car
    1: "blue",    # truck
    2: "orange",  # bus
    3: "purple",  # motorcycle
}


def load_slots(slots_file: Path) -> list[dict]:
    if not slots_file.exists():
        return []
    with open(slots_file, "r") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("slots", [])


def draw_annotations(
    image_path: Path,
    label_path: Path | None,
    slots: list[dict],
    output_path: Path,
) -> None:
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Draw slots first (dashed / semi-transparent green polygons)
    for slot in slots:
        poly = slot.get("polygon", [])
        if len(poly) >= 3:
            pts = [(int(p[0]), int(p[1])) for p in poly]
            draw.polygon(pts, outline="green", width=2)
            # Label slot ID
            cx = sum(p[0] for p in pts) // len(pts)
            cy = sum(p[1] for p in pts) // len(pts)
            draw.text((cx, cy), f"#{slot.get('slot_id')}", fill="green")

    # Draw vehicle bounding boxes
    if label_path and label_path.exists():
        with open(label_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    xc, yc, bw, bh = [float(x) for x in parts[1:5]]
                    xmin = int((xc - bw / 2) * w)
                    ymin = int((yc - bh / 2) * h)
                    xmax = int((xc + bw / 2) * w)
                    ymax = int((yc + bh / 2) * h)
                    color = CLASS_COLORS.get(cls_id, "yellow")
                    draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=3)
                    draw.text((xmin, max(0, ymin - 10)), f"cls:{cls_id}", fill=color)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize parking dataset samples.")
    parser.add_argument("--data-dir", type=str, default="datasets/parking_v1")
    parser.add_argument("--num-samples", type=int, default=10)
    parser.add_argument("--output-dir", type=str, default="datasets/parking_v1/samples")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    images_dir = data_dir / "images"
    labels_dir = data_dir / "labels"
    slots_dir = data_dir / "slots"
    output_dir = Path(args.output_dir)

    all_images = list(images_dir.glob("**/*.[jJ][pP][gG]")) + list(images_dir.glob("**/*.[pP][nN][gG]"))
    if not all_images:
        print(f"No images found in {images_dir}.")
        return

    slots = []
    if slots_dir.exists():
        for sf in slots_dir.glob("*.json"):
            slots.extend(load_slots(sf))

    random.seed(args.seed)
    selected = random.sample(all_images, min(args.num_samples, len(all_images)))

    print(f"Visualizing {len(selected)} samples into {output_dir}...")
    for idx, img_path in enumerate(selected, start=1):
        rel = img_path.relative_to(images_dir)
        label_path = labels_dir / rel.with_suffix(".txt")
        out_file = output_dir / f"sample_{idx}_{img_path.name}"
        draw_annotations(img_path, label_path if label_path.exists() else None, slots, out_file)

    print("✅ Visualization complete.")


if __name__ == "__main__":
    main()
