"""Unit tests for OccupancyEngine and SlotStateTracker.

References:
- docs/09_TESTING_SPEC.md (Occupancy state machine & Service tests)
- docs/01_PROJECT_SPEC.md (FR-05 Occupancy & FR-06 Temporal stability)
"""

import pytest

from app.ml.geometry import BoundingBox, ParkingSlot, Point
from app.services.occupancy_service import (
    OccupancyEngine,
    SlotStateTracker,
    SlotStatus,
)


@pytest.fixture
def sample_slots() -> list[ParkingSlot]:
    """Create 2 side-by-side square parking slots (100x100)."""
    # Slot 1: (0, 0) -> (100, 100)
    slot1 = ParkingSlot(
        id=1,
        polygon=[
            Point(0.0, 0.0),
            Point(100.0, 0.0),
            Point(100.0, 100.0),
            Point(0.0, 100.0),
        ],
    )
    # Slot 2: (120, 0) -> (220, 100)
    slot2 = ParkingSlot(
        id=2,
        polygon=[
            Point(120.0, 0.0),
            Point(220.0, 0.0),
            Point(220.0, 100.0),
            Point(120.0, 100.0),
        ],
    )
    return [slot1, slot2]


class TestSlotStateTracker:
    """Test suite for Temporal Smoothing State Machine (FR-06)."""

    def test_transient_positive_frame_rejected(self):
        tracker = SlotStateTracker(slot_id=1, current_status=SlotStatus.EMPTY)
        # 1 frame with OCCUPIED should be rejected
        status = tracker.update(SlotStatus.OCCUPIED, threshold_frame=3)
        assert status == SlotStatus.EMPTY

        # Return to EMPTY -> candidate reset
        status = tracker.update(SlotStatus.EMPTY, threshold_frame=3)
        assert status == SlotStatus.EMPTY

    def test_consecutive_positive_frames_accepted(self):
        tracker = SlotStateTracker(slot_id=1, current_status=SlotStatus.EMPTY)
        # Frame 1: Still EMPTY
        assert (
            tracker.update(SlotStatus.OCCUPIED, threshold_frame=3) == SlotStatus.EMPTY
        )
        # Frame 2: Still EMPTY
        assert (
            tracker.update(SlotStatus.OCCUPIED, threshold_frame=3) == SlotStatus.EMPTY
        )
        # Frame 3: Threshold reached (3 consecutive frames) -> Transitions to OCCUPIED!
        assert (
            tracker.update(SlotStatus.OCCUPIED, threshold_frame=3)
            == SlotStatus.OCCUPIED
        )

    def test_temporary_negative_frame_rejected(self):
        # Car is already confirmed OCCUPIED
        tracker = SlotStateTracker(slot_id=1, current_status=SlotStatus.OCCUPIED)
        # 1 frame with camera glitch / shadow (EMPTY) -> Stays OCCUPIED
        assert (
            tracker.update(SlotStatus.EMPTY, threshold_frame=3) == SlotStatus.OCCUPIED
        )
        # Next frame car is detected again -> Remains OCCUPIED
        assert (
            tracker.update(SlotStatus.OCCUPIED, threshold_frame=3)
            == SlotStatus.OCCUPIED
        )

    def test_consecutive_negative_frames_departure_accepted(self):
        tracker = SlotStateTracker(slot_id=1, current_status=SlotStatus.OCCUPIED)
        # 3 consecutive EMPTY frames -> Confirmed departure!
        assert (
            tracker.update(SlotStatus.EMPTY, threshold_frame=3) == SlotStatus.OCCUPIED
        )
        assert (
            tracker.update(SlotStatus.EMPTY, threshold_frame=3) == SlotStatus.OCCUPIED
        )
        assert tracker.update(SlotStatus.EMPTY, threshold_frame=3) == SlotStatus.EMPTY


class TestOccupancyEngine:
    """Test suite for OccupancyEngine."""

    def test_empty_slots_list(self):
        engine = OccupancyEngine(ios_threshold=0.3)
        detections = [BoundingBox(x_min=0, y_min=0, x_max=50, y_max=50)]
        results = engine.compute_instantaneous_occupancy(
            slots=[], detections=detections
        )
        assert results == []

    def test_no_vehicles_all_slots_empty(self, sample_slots):
        engine = OccupancyEngine(ios_threshold=0.3)
        results = engine.compute_instantaneous_occupancy(
            slots=sample_slots, detections=[]
        )
        assert len(results) == 2
        for r in results:
            assert r.status == SlotStatus.EMPTY
            assert r.match_box is None

    def test_vehicle_parked_in_slot1(self, sample_slots):
        engine = OccupancyEngine(ios_threshold=0.3)
        car_in_slot1 = BoundingBox(
            x_min=10.0, y_min=10.0, x_max=90.0, y_max=90.0, confidence=0.95
        )
        results = engine.compute_instantaneous_occupancy(
            slots=sample_slots, detections=[car_in_slot1]
        )

        assert len(results) == 2

        # Slot 1 must be OCCUPIED
        res1 = next(r for r in results if r.slot_id == 1)
        assert res1.status == SlotStatus.OCCUPIED
        assert res1.confidence == 0.95
        assert res1.match_box == car_in_slot1
        assert res1.ios_ratio > 0.5

        # Slot 2 must be EMPTY
        res2 = next(r for r in results if r.slot_id == 2)
        assert res2.status == SlotStatus.EMPTY
        assert res2.match_box is None

    def test_passing_car_below_threshold(self, sample_slots):
        engine = OccupancyEngine(ios_threshold=0.3)
        glancing_car = BoundingBox(
            x_min=90.0, y_min=90.0, x_max=150.0, y_max=150.0, confidence=0.9
        )
        results = engine.compute_instantaneous_occupancy(
            slots=sample_slots, detections=[glancing_car]
        )

        res1 = next(r for r in results if r.slot_id == 1)
        # 1% < 30% -> Should remain EMPTY
        assert res1.status == SlotStatus.EMPTY

    def test_smoothed_occupancy_pipeline(self, sample_slots):
        """Simulate video stream across multiple frames with temporal smoothing."""
        engine = OccupancyEngine(ios_threshold=0.3)
        car_in_slot1 = BoundingBox(
            x_min=10.0, y_min=10.0, x_max=90.0, y_max=90.0, confidence=0.95
        )

        # Frame 1: Car appears in Slot 1 -> Not enough consecutive frames, still EMPTY
        r1 = engine.compute_smoothed_occupancy(
            slots=sample_slots, detections=[car_in_slot1], threshold_frame=3
        )
        assert r1[0].status == SlotStatus.EMPTY

        # Frame 2: Car still there -> Still EMPTY
        r2 = engine.compute_smoothed_occupancy(
            slots=sample_slots, detections=[car_in_slot1], threshold_frame=3
        )
        assert r2[0].status == SlotStatus.EMPTY

        # Frame 3: 3rd consecutive frame -> Transitions to OCCUPIED!
        r3 = engine.compute_smoothed_occupancy(
            slots=sample_slots, detections=[car_in_slot1], threshold_frame=3
        )
        assert r3[0].status == SlotStatus.OCCUPIED

        # Frame 4: 1 noisy glitch frame where car is missed -> Stays OCCUPIED!
        r4 = engine.compute_smoothed_occupancy(
            slots=sample_slots, detections=[], threshold_frame=3
        )
        assert r4[0].status == SlotStatus.OCCUPIED

        # Frame 5: Car detected again -> Remains OCCUPIED!
        r5 = engine.compute_smoothed_occupancy(
            slots=sample_slots, detections=[car_in_slot1], threshold_frame=3
        )
        assert r5[0].status == SlotStatus.OCCUPIED
