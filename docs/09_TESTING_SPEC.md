# Testing Specification

## 1. Testing philosophy

The project contains geometry, business logic, database logic and ML
inference. Each should be tested at the appropriate level.

## 2. Unit tests

### Geometry

Test:

-   point inside polygon;
-   point outside polygon;
-   boundary behavior;
-   malformed polygon;
-   box/polygon overlap.

### Occupancy state machine

Examples:

``` text
EMPTY + one positive frame → EMPTY
EMPTY + N positive frames → OCCUPIED
OCCUPIED + one negative frame → OCCUPIED
OCCUPIED + N negative frames → EMPTY
```

### Schemas

Test valid and invalid polygon/detection payloads.

## 3. Repository tests

Use a test database.

Test:

-   create;
-   read;
-   update;
-   delete;
-   relationships;
-   constraints;
-   pagination/filtering where implemented.

## 4. Service tests

Services should be tested without depending on HTTP routing.

Examples:

-   create parking lot;
-   assign vehicle to slot;
-   create parking event;
-   calculate occupancy rate.

## 5. API tests

Use FastAPI's test client or async equivalent.

Verify:

-   status code;
-   response schema;
-   validation errors;
-   not-found behavior;
-   service errors.

## 6. ML tests

ML tests should focus on deterministic correctness rather than training
the whole model every test run.

Examples:

-   tensor shapes;
-   output ranges;
-   NMS behavior;
-   IoU implementation;
-   loss returns finite values;
-   queue size remains correct;
-   momentum update changes key encoder correctly;
-   checkpoint can be loaded.

## 7. Data tests

Run a dataset validation script before training.

Check:

-   image readability;
-   label readability;
-   class range;
-   bounding-box validity;
-   mask values;
-   missing labels;
-   duplicate/corrupt files.

## 8. Regression tests

Whenever a bug is found:

``` text
bug → write test → fix code
```

Do not rely on manually remembering the bug.

## 9. Suggested test structure

``` text
tests/
├── unit/
│   ├── test_geometry.py
│   ├── test_occupancy.py
│   └── test_schemas.py
├── integration/
│   ├── test_repositories.py
│   └── test_database.py
├── api/
│   ├── test_parking.py
│   └── test_inference.py
└── ml/
    ├── test_iou.py
    ├── test_losses.py
    └── test_moco.py
```
