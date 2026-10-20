"""Unit tests for geometry module (app/ml/geometry.py).

References:
- docs/09_TESTING_SPEC.md (Section 2: Geometry Unit tests)
- docs/01_PROJECT_SPEC.md (FR-03 & FR-05)
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from app.ml.geometry import (
    BoundingBox,
    ParkingSlot,
    Point,
    calculate_ios,
    is_point_in_polygon,
)


class TestPoint:
    """Test suite for Point dataclass."""

    def test_point_creation_and_attributes(self):
        p = Point(x=12.5, y=34.8)
        assert p.x == 12.5
        assert p.y == 34.8

    def test_point_immutability(self):
        p = Point(x=10.0, y=20.0)
        with pytest.raises(FrozenInstanceError):
            p.x = 99.0  # Point is frozen (immutable)

    def test_point_to_int_tuple(self):
        p = Point(x=15.9, y=42.1)
        assert p.to_int_tuple() == (15, 42)


class TestBoundingBox:
    """Test suite for BoundingBox class."""

    def test_box_properties(self):
        box = BoundingBox(
            x_min=10.0, y_min=20.0, x_max=50.0, y_max=80.0, confidence=0.88
        )
        assert box.width == 40.0
        assert box.height == 60.0
        assert box.area == 2400.0
        assert box.center == Point(30.0, 50.0)
        assert box.bottom_center == Point(30.0, 80.0)
        assert box.confidence == 0.88

    def test_box_defensive_negative_coords(self):
        # Inverted coordinates: x_min > x_max
        box = BoundingBox(x_min=50.0, y_min=80.0, x_max=10.0, y_max=20.0)
        assert box.width == 0.0
        assert box.height == 0.0
        assert box.area == 0.0

    def test_box_polygon_order(self):
        box = BoundingBox(x_min=0.0, y_min=0.0, x_max=100.0, y_max=50.0)
        poly = box.polygon
        assert len(poly) == 4
        assert poly[0] == Point(0.0, 0.0)  # Top-Left
        assert poly[1] == Point(100.0, 0.0)  # Top-Right
        assert poly[2] == Point(100.0, 50.0)  # Bottom-Right
        assert poly[3] == Point(0.0, 50.0)  # Bottom-Left


class TestParkingSlot:
    """Test suite for ParkingSlot representation."""

    def test_slot_properties_and_area(self):
        # 100x100 square slot
        poly = [
            Point(0.0, 0.0),
            Point(100.0, 0.0),
            Point(100.0, 100.0),
            Point(0.0, 100.0),
        ]
        slot = ParkingSlot(id=1, polygon=poly)
        assert slot.id == 1
        assert slot.area == pytest.approx(10000.0, rel=1e-3)
        assert slot.center == Point(50.0, 50.0)

    def test_slot_to_numpy_format(self):
        poly = [Point(1.0, 2.0), Point(3.0, 4.0), Point(5.0, 6.0)]
        slot = ParkingSlot(id=2, polygon=poly)
        arr = slot.to_numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.dtype == np.float32
        assert arr.shape == (3, 2)


class TestIsPointInPolygon:
    """Test suite for is_point_in_polygon function."""

    @pytest.fixture
    def square_polygon(self) -> list[Point]:
        return [
            Point(0.0, 0.0),
            Point(100.0, 0.0),
            Point(100.0, 100.0),
            Point(0.0, 100.0),
        ]

    def test_point_strictly_inside(self, square_polygon):
        assert is_point_in_polygon(Point(50.0, 50.0), square_polygon) is True

    def test_point_strictly_outside(self, square_polygon):
        assert is_point_in_polygon(Point(150.0, 50.0), square_polygon) is False
        assert is_point_in_polygon(Point(-10.0, 50.0), square_polygon) is False
        assert is_point_in_polygon(Point(50.0, 150.0), square_polygon) is False

    def test_point_on_boundary_edge(self, square_polygon):
        # On the top edge
        assert is_point_in_polygon(Point(50.0, 0.0), square_polygon) is True
        # On the vertex
        assert is_point_in_polygon(Point(0.0, 0.0), square_polygon) is True


class TestCalculateIoS:
    """Test suite for calculate_ios (Intersection over Slot)."""

    @pytest.fixture
    def target_slot(self) -> ParkingSlot:
        # 100x100 square from (0,0) to (100,100)
        return ParkingSlot(
            id=10,
            polygon=[
                Point(0.0, 0.0),
                Point(100.0, 0.0),
                Point(100.0, 100.0),
                Point(0.0, 100.0),
            ],
        )

    def test_complete_overlap(self, target_slot):
        # Vehicle box covers the slot entirely
        box = BoundingBox(x_min=0.0, y_min=0.0, x_max=100.0, y_max=100.0)
        ios = calculate_ios(box, target_slot)
        assert ios == pytest.approx(1.0, rel=1e-2)

    def test_partial_overlap(self, target_slot):
        # Box covers left half: (0, 0) to (50, 100) -> 50% of slot area
        box_half = BoundingBox(x_min=0.0, y_min=0.0, x_max=50.0, y_max=100.0)
        ios = calculate_ios(box_half, target_slot)
        assert ios == pytest.approx(0.5, rel=1e-2)

    def test_no_overlap_disjoint(self, target_slot):
        # Box completely far away
        box_far = BoundingBox(x_min=200.0, y_min=200.0, x_max=300.0, y_max=300.0)
        ios = calculate_ios(box_far, target_slot)
        assert ios == 0.0

    def test_zero_area_slot_defensive(self):
        # Degenerate slot with 0 area
        zero_slot = ParkingSlot(
            id=99,
            polygon=[Point(0.0, 0.0), Point(0.0, 0.0), Point(0.0, 0.0)],
        )
        box = BoundingBox(x_min=0.0, y_min=0.0, x_max=10.0, y_max=10.0)
        # Should return 0.0 without throwing exceptions
        assert calculate_ios(box, zero_slot) == 0.0
