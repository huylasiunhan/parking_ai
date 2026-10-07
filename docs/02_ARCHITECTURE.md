# Architecture Specification

## 1. High-level architecture

``` text
                     ┌────────────────────┐
                     │ Camera / Video     │
                     └─────────┬──────────┘
                               ↓
                     ┌────────────────────┐
                     │ Frame Processor    │
                     └─────────┬──────────┘
                               ↓
                     ┌────────────────────┐
                     │ Vehicle Detector   │
                     │ YOLO / Custom      │
                     └─────────┬──────────┘
                               ↓
                     ┌────────────────────┐
                     │ Tracker (later)    │
                     └─────────┬──────────┘
                               ↓
                     ┌────────────────────┐
                     │ Occupancy Engine   │
                     └─────────┬──────────┘
                               ↓
                  ┌────────────┴────────────┐
                  ↓                         ↓
           ┌─────────────┐          ┌──────────────┐
           │ FastAPI     │          │ Event Engine │
           └──────┬──────┘          └──────┬───────┘
                  ↓                         ↓
           ┌─────────────┐          ┌──────────────┐
           │ PostgreSQL  │          │ Analytics    │
           └─────────────┘          └──────────────┘
```

## 2. Backend architecture

Recommended structure:

``` text
app/
├── main.py
├── routers/
├── services/
├── repositories/
├── models/
├── schemas/
├── ml/
└── core/
```

### Router

HTTP concerns only: request validation, authentication later, calling
services and response serialization.

### Service

Business logic and orchestration.

### Repository

SQLAlchemy/database access only.

### ML layer

Model loading, preprocessing, inference and postprocessing.

## 3. ML inference lifecycle

Do not load a model on every HTTP request.

Bad:

``` text
request → load checkpoint → inference → destroy model
```

Preferred:

``` text
startup → load model → warm up → keep in memory
request → inference
```

A `ModelManager` should eventually support model name/version/device and
health status.

## 4. Offline-first strategy

First:

``` text
image/video file → inference → JSON/result visualization
```

Later:

``` text
RTSP → frame reader → inference → tracker → occupancy
```

This keeps CV bugs separate from streaming/network bugs.

## 5. Realtime architecture

``` text
RTSP
 ↓
Frame Reader
 ↓
Bounded Frame Queue
 ↓
Inference Worker
 ↓
Tracker
 ↓
Occupancy Engine
 ↓
Event Service
 ├── PostgreSQL
 └── WebSocket
```

A bounded queue prevents unbounded latency when inference is slower than
the camera.

## 6. Research architecture

``` text
Unlabeled Images
       ↓
   MoCo Training
       ↓
Pretrained Encoder
   ┌────┴────┐
   ↓         ↓
Detection  Segmentation
```

The research model and YOLO production baseline should remain separate
so experiments are easy to reproduce.

## 7. Deployment evolution

``` text
Local development
→ Docker Compose
→ GPU Linux environment
→ optional worker/Redis
```

Do not optimize deployment before the CV pipeline works.
