# FastAPI API Specification

## 1. API conventions

Base prefix:

``` text
/api/v1
```

Use Pydantic schemas for request/response validation.

Business logic belongs in services, not routers.

## 2. Parking lot

``` http
POST   /api/v1/parking-lots
GET    /api/v1/parking-lots
GET    /api/v1/parking-lots/{id}
PATCH  /api/v1/parking-lots/{id}
DELETE /api/v1/parking-lots/{id}
```

Create request:

``` json
{
  "name": "Parking Lot A",
  "location": "Campus A"
}
```

## 3. Parking slots

``` http
POST  /api/v1/parking-lots/{parking_lot_id}/slots
GET   /api/v1/parking-lots/{parking_lot_id}/slots
PATCH /api/v1/parking-slots/{slot_id}
```

Request:

``` json
{
  "slot_number": 1,
  "polygon": [[100,100],[200,100],[200,200],[100,200]]
}
```

## 4. Cameras

``` http
POST   /api/v1/cameras
GET    /api/v1/cameras
GET    /api/v1/cameras/{id}
PATCH  /api/v1/cameras/{id}
DELETE /api/v1/cameras/{id}
```

## 5. Image inference

``` http
POST /api/v1/inference/image
```

Input: multipart file plus optional camera ID.

Example response:

``` json
{
  "model_version": "yolo-parking-v1",
  "detections": [
    {
      "class_name": "car",
      "confidence": 0.93,
      "bbox": [100,120,250,300]
    }
  ],
  "slots": [
    {
      "slot_id": 1,
      "status": "OCCUPIED",
      "confidence": 0.93
    }
  ]
}
```

## 6. Video inference

``` http
POST /api/v1/inference/video
```

Initial implementation may process uploaded files synchronously for
development. Long-running jobs should later become asynchronous jobs.

## 7. Parking status

``` http
GET /api/v1/parking-lots/{parking_lot_id}/status
```

Example:

``` json
{
  "parking_lot_id": 1,
  "total_slots": 100,
  "occupied": 63,
  "empty": 37,
  "occupancy_rate": 0.63,
  "updated_at": "2026-10-06T10:00:00"
}
```

## 8. Analytics

``` http
GET /api/v1/parking-lots/{parking_lot_id}/analytics
```

Optional query parameters:

``` text
from
 to
interval
```

## 9. Models

Recommended:

``` http
GET  /api/v1/models
GET  /api/v1/models/{id}
POST /api/v1/models
```

## 10. Error contract

Use a consistent structure:

``` json
{
  "detail": {
    "code": "INVALID_SLOT_POLYGON",
    "message": "Parking slot polygon is invalid."
  }
}
```

Examples:

``` text
400 invalid input
404 resource not found
422 validation error
503 model/database/camera unavailable
```

Do not expose stack traces.

## 11. Testing

### Unit

-   schemas
-   geometry
-   services
-   state transitions

### Integration

-   repositories
-   database

### API

-   status codes
-   response schemas
-   error behavior

ML model correctness should be covered by separate evaluation/benchmark
scripts.
