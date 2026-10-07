# Smart Parking Vision System --- Documentation

## Project purpose

An end-to-end Computer Vision + Backend system for monitoring parking
occupancy from fixed-camera images/video. The project also serves as a
research project for self-supervised representation learning.

## Core system

``` text
Camera / Video
    ↓
Frame Processor
    ↓
Vehicle Detection (YOLO / Custom Detector)
    ↓
Tracking (later)
    ↓
Occupancy Engine
    ↓
Parking Slot State
    ↓
FastAPI
    ├── PostgreSQL
    ├── WebSocket (later)
    └── Analytics
```

## Research system

``` text
Unlabeled Parking Images
    ↓
MoCo-style Self-Supervised Learning
    ↓
Project Encoder
    ├── Vehicle Detection
    └── Parking-space Segmentation
```

## Documentation map

-   `01_PROJECT_SPEC.md` --- product scope, requirements and acceptance
    criteria.
-   `02_ARCHITECTURE.md` --- system and software architecture.
-   `03_DATASET_SPEC.md` --- dataset, annotations, split and leakage
    rules.
-   `04_ML_SPEC.md` --- SSL, detection, segmentation and model
    requirements.
-   `05_EXPERIMENT_SPEC.md` --- fair benchmark and research protocol.
-   `06_API_SPEC.md` --- FastAPI endpoints and contracts.
-   `07_DATABASE_SPEC.md` --- PostgreSQL schema and persistence design.
-   `08_ROADMAP.md` --- implementation phases and milestones.
-   `09_TESTING_SPEC.md` --- unit, integration, ML and API testing.
-   `10_RESEARCH_PLAN.md` --- research questions, hypotheses and final
    report.
-   `11_DEFINITION_OF_DONE.md` --- completion criteria for each phase.

## Guiding principles

1.  Build the simplest working baseline first.
2.  Separate the production baseline from the research model.
3.  Compare models on the same task, dataset and test set.
4.  Never tune against the final test set.
5.  Record configurations and checkpoints.
6.  Prefer measurable engineering over feature count.
7.  Do not add realtime infrastructure before offline inference is
    stable.
