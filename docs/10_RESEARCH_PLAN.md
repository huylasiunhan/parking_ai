# Research Plan

## 1. Central research story

The project should not be presented merely as "YOLO detects cars in a
parking lot".

The stronger question is:

> Can self-supervised visual representation learning from unlabeled
> parking imagery improve downstream vehicle detection and parking-space
> segmentation, and how does the resulting model compare with a
> production-grade YOLO detector?

## 2. Hypotheses

### H1

MoCo pretraining improves downstream detection compared with random
initialization.

### H2

Domain-specific SSL can provide useful representations compared with
generic ImageNet initialization.

### H3

Fine-tuned YOLO will likely have stronger absolute detection performance
because it is a mature detector.

### H4

A custom detector may provide a useful accuracy/latency/size trade-off.

These are hypotheses, not target results.

## 3. Experiments

### Experiment 1 --- SSL sanity check

-   contrastive loss curve;
-   embedding inspection;
-   kNN/linear evaluation.

### Experiment 2 --- initialization

Compare:

``` text
Random
ImageNet
MoCo
```

### Experiment 3 --- YOLO comparison

Compare the best custom detector with fine-tuned YOLO on the same test
set.

### Experiment 4 --- label efficiency

Compare 10/25/50/100% labeled training data.

### Experiment 5 --- segmentation transfer

Compare Random/ImageNet/MoCo encoders with the same decoder.

## 4. Strong-result definition

The project does not need to beat YOLO.

A strong result can be:

``` text
MoCo > Random
MoCo improves low-label performance
YOLO > custom model in mAP
custom model is smaller/faster
MoCo transfers to segmentation
```

This is scientifically more meaningful than forcing a YOLO-beating
result.

## 5. Failure analysis

Inspect errors involving:

-   small vehicles;
-   occlusion;
-   shadows;
-   reflections;
-   low light;
-   crowded scenes;
-   unusual viewpoints.

For segmentation:

-   faded markings;
-   shadows;
-   partially blocked spaces;
-   boundary errors.

## 6. Final report structure

``` text
1. Introduction
2. Problem Definition
3. Dataset
4. Parking Baseline
5. YOLO Baseline
6. Self-Supervised Learning
7. Downstream Detection
8. Segmentation
9. Backend System
10. Experiments
11. Results
12. Failure Analysis
13. Limitations
14. Conclusion
```

## 7. Portfolio description

Suggested title:

**Smart Parking Vision System: Self-Supervised Representation Learning
for Vehicle Detection and Parking Occupancy**

Suggested description:

> An end-to-end Computer Vision and backend system for parking occupancy
> monitoring. The project implements MoCo-style self-supervised
> pretraining from scratch, transfers the learned encoder to vehicle
> detection and parking-space segmentation, benchmarks against ImageNet
> initialization and fine-tuned YOLO, and exposes inference and parking
> analytics through FastAPI and PostgreSQL.
