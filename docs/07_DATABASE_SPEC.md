# PostgreSQL Database Specification

## 1. Purpose

PostgreSQL stores configuration, current state and historical parking
events. Large images/videos should not be stored directly in PostgreSQL.

## 2. ER model

``` text
ParkingLot 1 ─── N Camera
ParkingLot 1 ─── N ParkingSlot
Camera 1 ─── N Detection
Camera 1 ─── N Vehicle
ParkingSlot 1 ─── N ParkingEvent
Vehicle 1 ─── N Detection
Vehicle 1 ─── N ParkingEvent
```

## 3. parking_lots

``` text
id          BIGINT PK
name        VARCHAR NOT NULL
location    VARCHAR NULL
created_at  TIMESTAMP NOT NULL
updated_at  TIMESTAMP NOT NULL
```

## 4. cameras

``` text
id              BIGINT PK
parking_lot_id  BIGINT FK
name            VARCHAR
stream_url      TEXT
status          VARCHAR
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

## 5. parking_slots

``` text
id              BIGINT PK
parking_lot_id  BIGINT FK
slot_number     INTEGER
polygon         JSONB
status          VARCHAR
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

`slot_number` should be unique within a parking lot.

## 6. vehicles

``` text
id              BIGINT PK
camera_id       BIGINT FK
tracking_id     INTEGER NULL
vehicle_type    VARCHAR
first_seen      TIMESTAMP
last_seen       TIMESTAMP
```

A vehicle is a tracked entity, not one database row per video frame.

## 7. detections

``` text
id          BIGINT PK
camera_id   BIGINT FK
vehicle_id  BIGINT FK NULL
class_name  VARCHAR
bbox        JSONB
confidence  FLOAT
timestamp   TIMESTAMP
```

High-frequency raw detections can grow very quickly. Introduce
retention/aggregation later if needed.

## 8. parking_events

``` text
id          BIGINT PK
slot_id     BIGINT FK
vehicle_id  BIGINT FK NULL
event_type  VARCHAR
timestamp   TIMESTAMP
confidence  FLOAT NULL
```

Recommended event types:

``` text
PARKING_STARTED
PARKING_ENDED
```

## 9. model_versions

``` text
id              BIGINT PK
name            VARCHAR
version         VARCHAR
model_type      VARCHAR
checkpoint_path TEXT
metrics         JSONB
created_at      TIMESTAMP
```

Example metrics:

``` json
{"map50":0.81,"map5095":0.54,"precision":0.86,"recall":0.79}
```

## 10. Indexes

Start with:

``` text
cameras.parking_lot_id
parking_slots.parking_lot_id
detections.camera_id
detections.timestamp
parking_events.slot_id
parking_events.timestamp
parking_events.vehicle_id
```

Add indexes based on actual query patterns.

## 11. Alembic

All schema changes must use migrations.

Do not use `Base.metadata.create_all()` in application startup once
Alembic is established.

Workflow:

``` text
change model
→ generate migration
→ inspect migration
→ upgrade
→ test
```

## 12. Future PostGIS

JSONB polygons are sufficient initially. PostGIS is an optional later
upgrade if spatial queries become important.
