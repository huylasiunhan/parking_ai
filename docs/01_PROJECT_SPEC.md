# Project Specification

## 1. Product definition

The system estimates the occupancy state of predefined parking spaces
from camera imagery and exposes the result through an API.

For each slot the system should eventually provide:

``` json
{
  "slot_id": 12,
  "status": "OCCUPIED",
  "vehicle_id": 83,
  "confidence": 0.94,
  "updated_at": "2026-10-06T10:00:00"
}
```

## 2. Scope

### In scope

-   Fixed-camera parking scenes.
-   Vehicle detection.
-   Parking-slot geometry.
-   Occupancy classification.
-   Offline image/video inference.
-   Self-supervised pretraining.
-   Downstream object detection.
-   Parking-space segmentation.
-   FastAPI backend.
-   PostgreSQL persistence.
-   Experiment tracking.
-   Optional tracking and realtime inference.

### Out of scope initially

-   License plate recognition.
-   Payment processing.
-   Multi-camera vehicle identity matching.
-   Moving cameras.
-   Full mobile application.
-   Cloud-scale deployment.
-   3D reconstruction.

## 3. Functional requirements

### FR-01 Parking lots

Create, retrieve, update and delete parking lots.

### FR-02 Cameras

Register cameras against a parking lot. Initial implementation may use
image/video files instead of RTSP.

### FR-03 Parking slots

Each slot has a stable ID and polygon coordinates.

### FR-04 Vehicle detection

Return class, bounding box, confidence and optional tracking ID.

### FR-05 Occupancy

Map detected vehicles to parking slots.

Initial method: vehicle center point inside slot polygon.

Improved method: polygon/box overlap or vehicle-footprint intersection.

### FR-06 Temporal stability

Avoid changing slot state from one noisy frame. Use configurable
consecutive-frame thresholds.

Example:

``` text
EMPTY → candidate occupied → OCCUPIED
```

### FR-07 Inference

Support image inference first, then video, then realtime streams.

### FR-08 Analytics

Eventually provide occupancy rate, parking duration, peak occupancy and
turnover.

## 4. Non-functional requirements

### Reproducibility

Every experiment records dataset version, split, seed, architecture,
hyperparameters, checkpoint and metrics.

### Maintainability

Use:

``` text
router → service → repository
```

ML inference should be isolated from HTTP routing logic.

### Testability

Core geometry, state transitions, services, repositories and API
contracts must be testable independently.

### Performance

Measure latency, FPS, model size, parameter count and memory instead of
making unsupported claims.

## 5. Domain states

Parking slot:

``` text
UNKNOWN
EMPTY
CANDIDATE_OCCUPIED
OCCUPIED
CANDIDATE_EMPTY
```

Vehicle:

``` text
DETECTED
TRACKED
PARKING_STARTED
PARKED
PARKING_ENDED
LOST
```

## 6. MVP acceptance criteria

The MVP is complete when:

-   A parking image/video can be processed.
-   Slot polygons can be configured.
-   Vehicles can be detected.
-   Vehicle-to-slot assignment works.
-   Occupancy state is visualized.
-   FastAPI exposes inference.
-   PostgreSQL persists parking events.
-   Core occupancy logic has tests.
