from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def to_int_tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)


# Bounding Box for car
class BoundingBox:
    def __init__(
        self,
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float,
        confidence: float = 1.0,
    ):
        self.top_left = Point(x_min, y_min)
        self.bot_right = Point(x_max, y_max)
        self.width = max(0.0, x_max - x_min)
        self.height = max(0.0, y_max - y_min)
        self.area = self.width * self.height
        self.center = Point((x_min + x_max) / 2.0, (y_min + y_max) / 2.0)
        self.bottom_center = Point((x_min + x_max) / 2.0, y_max)
        self.confidence = confidence

    @property
    def polygon(self):
        """
        Returns the polygon representation of the bounding box
        """
        return [
            Point(self.top_left.x, self.top_left.y),
            Point(self.bot_right.x, self.top_left.y),
            Point(self.bot_right.x, self.bot_right.y),
            Point(self.top_left.x, self.bot_right.y),
        ]


# Representation of parking spot
class ParkingSlot:
    def __init__(self, id: int, polygon: list[Point], is_available: bool = False):
        self.id = id
        self.polygon = polygon
        self.is_available = is_available

    @property
    def center(self):
        x_coords = [p.x for p in self.polygon]
        y_coords = [p.y for p in self.polygon]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return Point(center_x, center_y)

    def to_numpy(self):
        return np.array([[p.x, p.y] for p in self.polygon], dtype=np.float32)

    @property
    def area(self):
        points = self.to_numpy()
        return cv2.contourArea(points)


# Functions for math operations


def is_point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    # Convert list of Point to numpy array of shape (N, 1, 2) for OpenCV
    polygon_pts = np.array([[p.x, p.y] for p in polygon], dtype=np.float32)
    # Check if point is inside polygon
    return cv2.pointPolygonTest(polygon_pts, (point.x, point.y), False) >= 0


def calculate_ios(box: BoundingBox, slot: ParkingSlot) -> float:
    if slot.area <= 0:
        return 0.0

    box_points = np.array([[p.x, p.y] for p in box.polygon], dtype=np.float32)
    slot_points = slot.to_numpy()

    intersection_area, _ = cv2.intersectConvexConvex(box_points, slot_points, True)

    return min(1.0, intersection_area / slot.area)
