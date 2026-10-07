# Smart Parking Vision System (Parking AI)

An end-to-end Computer Vision + Backend system for monitoring parking occupancy from fixed-camera imagery, combined with Self-Supervised Learning (MoCo) research for domain-specific visual representations.

---

## 📌 Project Architecture

```
Camera / Video Stream / Image
            ↓
    Frame Processor
            ↓
Vehicle Detection (YOLO / Custom Detector)
            ↓
    Occupancy Engine (Geometry + Temporal Smoothing)
            ↓
    FastAPI REST API
     ├── PostgreSQL (Slots, Cameras, Vehicles, Events)
     └── Analytics
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.12 or 3.13
- PostgreSQL (for backend & event storage)
- Git

### 2. Environment Setup

```bash
# Clone the repository
git clone <repo-url>
cd parking-ai

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[all]"
```

### 3. Configuration

```bash
cp .env.example .env
# Edit .env to match your local setup
```

---

## 📚 Documentation

Detailed specifications and architectural guides are in the `docs/` folder:

- [`01_PROJECT_SPEC.md`](docs/01_PROJECT_SPEC.md) - Product scope, requirements, and acceptance criteria.
- [`02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md) - System and software architecture.
- [`03_DATASET_SPEC.md`](docs/03_DATASET_SPEC.md) - Dataset conventions, annotations, and splitting rules.
- [`04_ML_SPEC.md`](docs/04_ML_SPEC.md) - SSL (MoCo), Custom Detector, YOLO, and Segmentation specs.
- [`05_EXPERIMENT_SPEC.md`](docs/05_EXPERIMENT_SPEC.md) - Controlled benchmarks and evaluation protocols.
- [`06_API_SPEC.md`](docs/06_API_SPEC.md) - FastAPI endpoints and contracts.
- [`07_DATABASE_SPEC.md`](docs/07_DATABASE_SPEC.md) - PostgreSQL schema and Alembic migrations.
- [`08_ROADMAP.md`](docs/08_ROADMAP.md) - Implementation phases and milestones.
- [`09_TESTING_SPEC.md`](docs/09_TESTING_SPEC.md) - Testing specifications.
- [`10_RESEARCH_PLAN.md`](docs/10_RESEARCH_PLAN.md) - Research questions, hypotheses, and report structure.
- [`11_DEFINITION_OF_DONE.md`](docs/11_DEFINITION_OF_DONE.md) - Definition of Done for each milestone.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
