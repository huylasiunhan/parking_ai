"""Phase 1: Deterministic Classical Slot Baseline Demo Script.

Demonstrates parking slot geometry, vehicle-to-slot assignment,
and EMPTY/OCCUPIED rendering without requiring deep learning inference.

References:
- docs/08_ROADMAP.md (Phase 1 --- Classical slot baseline)
- docs/01_PROJECT_SPEC.md (FR-03, FR-05)
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

from app.ml.geometry import BoundingBox, ParkingSlot, Point
from app.services.occupancy_service import OccupancyEngine, SlotStatus


def load_slots_and_vehicles(
    label_path: Path,
    image_width: int,
    image_height: int,
) -> tuple[list[ParkingSlot], list[BoundingBox]]:
    """Parse PKLot YOLO labels into ParkingSlots and simulated vehicle detections."""
    slots: list[ParkingSlot] = []
    vehicles: list[BoundingBox] = []

    with open(label_path) as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cls_id = int(parts[0])
        xc, yc, w, h = (float(x) for x in parts[1:5])

        # Convert normalized coordinates [0.0..1.0] to pixel coordinates
        abs_xc = xc * image_width
        abs_yc = yc * image_height
        abs_w = w * image_width
        abs_h = h * image_height

        x1 = abs_xc - abs_w / 2.0
        y1 = abs_yc - abs_h / 2.0
        x2 = abs_xc + abs_w / 2.0
        y2 = abs_yc + abs_h / 2.0

        # Define 4-point polygon for the parking slot
        polygon = [
            Point(x1, y1),
            Point(x2, y1),
            Point(x2, y2),
            Point(x1, y2),
        ]
        slots.append(ParkingSlot(id=idx, polygon=polygon))

        # If PKLot label indicates space-occupied (class 1), simulate vehicle detection
        if cls_id == 1:
            vehicles.append(
                BoundingBox(
                    x_min=x1,
                    y_min=y1,
                    x_max=x2,
                    y_max=y2,
                    confidence=0.95,
                )
            )

    return slots, vehicles


def render_occupancy_overlay(
    image: np.ndarray,
    slots: list[ParkingSlot],
    results: list,
    vehicles: list[BoundingBox],
) -> np.ndarray:
    """Render semi-transparent slot polygons, vehicle boxes, and top status HUD."""
    overlay = image.copy()
    output = image.copy()

    occupied_count = 0
    empty_count = 0

    results_by_id = {r.slot_id: r for r in results}

    # 1. Draw parking slot polygons
    for slot in slots:
        res = results_by_id.get(slot.id)
        is_occupied = res is not None and res.status == SlotStatus.OCCUPIED

        if is_occupied:
            occupied_count += 1
            color = (0, 0, 220)  # Red (BGR)
        else:
            empty_count += 1
            color = (0, 200, 0)  # Green (BGR)

        # OpenCV needs int32 points for polygon drawing
        pts = slot.to_numpy().astype(np.int32)
        cv2.fillPoly(overlay, [pts], color)
        cv2.polylines(output, [pts], isClosed=True, color=color, thickness=2)

    # Blend overlay with original image (alpha = 0.35 for semi-transparent fill)
    alpha = 0.35
    cv2.addWeighted(overlay, alpha, output, 1.0 - alpha, 0, output)

    # 2. Draw vehicle bounding boxes
    for v in vehicles:
        cv2.rectangle(
            output,
            (int(v.top_left.x), int(v.top_left.y)),
            (int(v.bot_right.x), int(v.bot_right.y)),
            (255, 180, 0),  # Cyan / Orange
            1,
        )

    # 3. Draw Top HUD Banner
    total = len(slots)
    occ_rate = (occupied_count / total * 100.0) if total > 0 else 0.0

    hud_h = 42
    hud_bg = np.zeros((hud_h, output.shape[1], 3), dtype=np.uint8)
    cv2.rectangle(hud_bg, (0, 0), (output.shape[1], hud_h), (25, 25, 25), -1)
    output[:hud_h, :] = cv2.addWeighted(output[:hud_h, :], 0.2, hud_bg, 0.8, 0)

    hud_text = (
        f"PARKING AI [Phase 1 Baseline] | "
        f"Total: {total} | Occupied: {occupied_count} | Empty: {empty_count} | "
        f"Occupancy Rate: {occ_rate:.1f}%"
    )
    cv2.putText(
        output,
        hud_text,
        (12, 27),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 1: Classical Slot Baseline Demo"
    )
    parser.add_argument(
        "--image",
        type=str,
        default="datasets/parking_v1/images/test/2012-09-11_15_53_00_jpg.rf.8282544a640a23df05bd245a9210e663.jpg",
        help="Path to test parking image",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/phase1_baseline_demo.jpg",
        help="Path to save output rendered image",
    )
    parser.add_argument(
        "--ios-threshold",
        type=float,
        default=0.3,
        help="Intersection over Slot threshold",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        return

    # Derive matching YOLO label path from image path
    label_path = Path(str(image_path).replace("/images/", "/labels/")).with_suffix(
        ".txt"
    )
    if not label_path.exists():
        print(f"Error: Label file not found: {label_path}")
        return

    # 1. Read Image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return
    h, w = image.shape[:2]
    print(f"Loaded image: {image_path.name} ({w}x{h})")

    # 2. Parse Slots and Vehicles
    slots, vehicles = load_slots_and_vehicles(label_path, w, h)
    print(f"Loaded {len(slots)} slots and simulated {len(vehicles)} vehicles.")

    # 3. Run Occupancy Engine (using the code you built!)
    engine = OccupancyEngine(ios_threshold=args.ios_threshold)
    results = engine.compute_instantaneous_occupancy(slots, vehicles)

    occupied_count = sum(1 for r in results if r.status == SlotStatus.OCCUPIED)
    empty_count = sum(1 for r in results if r.status == SlotStatus.EMPTY)
    print(f"Occupancy Engine Result: {occupied_count} OCCUPIED, {empty_count} EMPTY")

    # 4. Render Visual Overlay
    output_image = render_occupancy_overlay(image, slots, results, vehicles)

    # 5. Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), output_image)
    print(f"✅ Demo image successfully saved to: {output_path}")


if __name__ == "__main__":
    main()
