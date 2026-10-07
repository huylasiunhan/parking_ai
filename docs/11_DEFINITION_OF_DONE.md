# Definition of Done

## General rule

Code that merely runs is not automatically complete.

A feature is done when it is implemented, tested, documented and
reproducible at the appropriate level.

## ML task DoD

-   [ ] Dataset version recorded.
-   [ ] Config file exists.
-   [ ] Training command documented.
-   [ ] Checkpoint saved.
-   [ ] Metrics saved.
-   [ ] Evaluation script works.
-   [ ] Visualization exists.
-   [ ] Failure cases inspected.

## SSL DoD

-   [ ] Query encoder implemented.
-   [ ] Key encoder implemented.
-   [ ] Momentum update implemented.
-   [ ] Projection head implemented.
-   [ ] Queue implemented.
-   [ ] InfoNCE implemented.
-   [ ] Checkpoint can reload.
-   [ ] Loss behaves sensibly.
-   [ ] At least one representation evaluation completed.

## Detection DoD

-   [ ] Dataset loads.
-   [ ] Labels validated.
-   [ ] Detector trains.
-   [ ] Validation metrics recorded.
-   [ ] Fixed test evaluation recorded.
-   [ ] mAP50 and mAP50-95 available.
-   [ ] Precision and recall available.
-   [ ] Efficiency measured.

## Segmentation DoD

-   [ ] Masks validated.
-   [ ] Encoder/decoder implemented.
-   [ ] Training works.
-   [ ] IoU recorded.
-   [ ] Dice recorded.
-   [ ] Predictions visualized.

## Backend DoD

-   [ ] Pydantic schemas exist.
-   [ ] Router exists.
-   [ ] Service exists.
-   [ ] Repository exists when DB access is required.
-   [ ] Migration exists.
-   [ ] Endpoint works.
-   [ ] Error cases defined.
-   [ ] Tests exist.

## Database DoD

-   [ ] SQLAlchemy model.
-   [ ] Alembic migration.
-   [ ] Constraints.
-   [ ] Required indexes.
-   [ ] Repository tests.

## Research result DoD

-   [ ] Baseline defined.
-   [ ] Comparison is fair.
-   [ ] Test set fixed.
-   [ ] Metrics reported.
-   [ ] Hardware/software recorded.
-   [ ] Limitations documented.
-   [ ] Conclusion does not overclaim.

## MVP DoD

The project can be called an MVP when:

``` text
Image/video
→ YOLO
→ slot assignment
→ occupancy state
→ FastAPI
→ PostgreSQL
```

works end-to-end with tests.

The SSL/research component is an extension of the MVP, not a
prerequisite for proving the basic parking system works.
