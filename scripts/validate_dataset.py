"""Dataset validation and quality check script.

References:
- docs/03_DATASET_SPEC.md (Section 6: Quality checks)
"""

import argparse
import json
from pathlib import Path
from PIL import Image


def validate_yolo_labels(label_path: Path, num_classes: int = 4) -> list[str]:
    """Validate YOLO format text file: class_id x_center y_center width height."""
    errors = []
    if not label_path.exists():
        return [f"Missing label file: {label_path}"]

    with open(label_path, "r") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 5:
            errors.append(f"{label_path}:{idx} has fewer than 5 elements ({parts})")
            continue
        try:
            cls_id = int(parts[0])
            coords = [float(x) for x in parts[1:5]]
        except ValueError:
            errors.append(f"{label_path}:{idx} invalid float/int values")
            continue

        if not (0 <= cls_id < num_classes):
            errors.append(f"{label_path}:{idx} class_id {cls_id} out of range [0, {num_classes-1}]")

        for c_idx, c in enumerate(coords):
            if not (0.0 <= c <= 1.0):
                errors.append(f"{label_path}:{idx} coord #{c_idx} ({c}) out of range [0.0, 1.0]")

    return errors


def validate_slot_polygons(slots_file: Path) -> list[str]:
    """Validate parking slot polygons JSON."""
    errors = []
    if not slots_file.exists():
        return [f"Slots file not found: {slots_file}"]

    try:
        with open(slots_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        return [f"Failed to parse JSON {slots_file}: {e}"]

    slots = data if isinstance(data, list) else data.get("slots", [])
    if not slots:
        errors.append(f"No slots found in {slots_file}")

    for s in slots:
        slot_id = s.get("slot_id")
        polygon = s.get("polygon")
        if slot_id is None:
            errors.append(f"Slot missing 'slot_id': {s}")
        if not polygon or len(polygon) < 3:
            errors.append(f"Slot {slot_id} has invalid polygon (fewer than 3 vertices)")

    return errors


def validate_image_file(image_path: Path) -> tuple[bool, str, tuple[int, int] | None]:
    """Verify image readability and integrity using Pillow."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        # Verify only reads header; reopen to ensure full decompression is clean
        with Image.open(image_path) as img:
            size = img.size
            img.load()
        return True, "", size
    except Exception as e:
        return False, str(e), None


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate parking dataset integrity.")
    parser.add_argument("--data-dir", type=str, default="datasets/parking_v1")
    parser.add_argument("--num-classes", type=int, default=4)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    print(f"--- Validating dataset in {data_dir} ---")

    images_dir = data_dir / "images"
    labels_dir = data_dir / "labels"
    slots_dir = data_dir / "slots"

    if not images_dir.exists():
        print(f"Warning: {images_dir} does not exist yet.")
        return

    image_files = list(images_dir.glob("**/*.[jJ][pP][gG]")) + list(images_dir.glob("**/*.[pP][nN][gG]"))
    print(f"Found {len(image_files)} image files.")

    corrupt_count = 0
    label_error_count = 0

    for img_path in image_files:
        ok, err_msg, size = validate_image_file(img_path)
        if not ok:
            print(f"[CORRUPT] {img_path}: {err_msg}")
            corrupt_count += 1
            continue

        # Corresponding label check
        rel_path = img_path.relative_to(images_dir)
        label_path = labels_dir / rel_path.with_suffix(".txt")
        if label_path.exists():
            lbl_errors = validate_yolo_labels(label_path, num_classes=args.num_classes)
            if lbl_errors:
                for le in lbl_errors:
                    print(f"[LABEL ERROR] {le}")
                label_error_count += len(lbl_errors)

    if slots_dir.exists():
        for slot_file in slots_dir.glob("*.json"):
            slot_errors = validate_slot_polygons(slot_file)
            if slot_errors:
                for se in slot_errors:
                    print(f"[SLOT ERROR] {se}")
            else:
                print(f"[OK] Slot file {slot_file.name} is valid.")

    print("\n--- Summary ---")
    print(f"Total images checked: {len(image_files)}")
    print(f"Corrupted images: {corrupt_count}")
    print(f"Label errors: {label_error_count}")
    if corrupt_count == 0 and label_error_count == 0:
        print("✅ Dataset validation PASSED.")
    else:
        print("❌ Dataset validation FAILED with issues.")


if __name__ == "__main__":
    main()
