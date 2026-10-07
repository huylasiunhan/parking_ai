# Implementation Roadmap

## Phase 0 --- Dataset and experiment design

### Goal

Freeze the data strategy before large-scale coding.

### Deliverables

-   Primary dataset selected.
-   License documented.
-   Train/validation/test split.
-   Annotation format.
-   Dataset version.
-   Evaluation protocol.

------------------------------------------------------------------------

## Phase 1 --- Classical slot baseline

### Goal

Solve the parking-domain logic without deep learning.

### Tasks

1.  Manual slot polygon annotation.
2.  Slot visualization.
3.  Vehicle-box simulation.
4.  Point-in-polygon assignment.
5.  EMPTY/OCCUPIED rendering.

### Deliverable

A deterministic script that displays slot state.

------------------------------------------------------------------------

## Phase 2 --- YOLO detector

### Goal

Create a strong production baseline.

### Tasks

1.  Run pretrained YOLO.
2.  Inspect confidence/IoU/NMS behavior.
3.  Prepare parking dataset.
4.  Fine-tune YOLO.
5.  Evaluate fixed test set.
6.  Measure latency/FPS.

### Deliverable

Reproducible YOLO baseline.

------------------------------------------------------------------------

## Phase 3 --- Occupancy engine

### Goal

Convert detections into stable parking states.

### Tasks

-   vehicle-to-slot assignment;
-   confidence threshold;
-   temporal smoothing;
-   state machine;
-   parking events;
-   visualization;
-   tests.

### Milestone

**MVP complete.**

------------------------------------------------------------------------

## Phase 4 --- Self-supervised learning

### Goal

Train a project-owned visual representation.

### Tasks

-   two-view dataset;
-   augmentations;
-   query encoder;
-   key encoder;
-   projection head;
-   momentum update;
-   queue;
-   InfoNCE;
-   checkpointing;
-   linear/kNN evaluation.

------------------------------------------------------------------------

## Phase 5 --- Downstream detection research

### Goal

Measure whether SSL improves detection.

### Models

``` text
Custom + Random
Custom + ImageNet
Custom + MoCo
YOLO + parking fine-tuning
```

### Deliverable

Controlled benchmark and analysis.

------------------------------------------------------------------------

## Phase 6 --- Segmentation

### Goal

Transfer the encoder to segmentation.

### Tasks

-   masks;
-   U-Net decoder;
-   Random/ImageNet/MoCo experiments;
-   IoU/Dice;
-   failure analysis.

------------------------------------------------------------------------

## Phase 7 --- FastAPI + PostgreSQL

### Goal

Integrate the stable CV pipeline into the backend.

### Tasks

-   SQLAlchemy models;
-   Alembic;
-   repositories;
-   services;
-   routers;
-   inference endpoint;
-   status endpoint;
-   event persistence;
-   model registry;
-   pytest.

------------------------------------------------------------------------

## Phase 8 --- Tracking + realtime

### Goal

Move from offline inference to continuous camera operation.

### Tasks

-   RTSP;
-   frame sampling;
-   ByteTrack/BoT-SORT;
-   tracking IDs;
-   parking duration;
-   WebSocket.

------------------------------------------------------------------------

## Phase 9 --- Productionization

Optional:

-   Docker.
-   Compose.
-   GPU inference service.
-   Structured logging.
-   Health checks.
-   Monitoring.
-   Background workers.
-   Redis where justified.

## Suggested schedule

``` text
Weeks 1–2   Dataset + baseline + YOLO
Weeks 3–4   Occupancy MVP
Weeks 5–7   MoCo
Weeks 8–9   Detection benchmark
Weeks 10–11 Segmentation
Weeks 12–13 FastAPI + PostgreSQL
Week 14+    Tracking/realtime/production
```

The schedule is a guide. Do not sacrifice experiment quality to hit an
arbitrary deadline.
