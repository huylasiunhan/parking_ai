# Machine Learning Specification

## 1. ML tasks

### Task A --- Vehicle detection

Input: parking image.

Output: vehicle bounding boxes, classes and confidence.

### Task B --- Parking-space segmentation

Input: parking image.

Output: pixel-level mask.

### Task C --- Self-supervised representation learning

Input: unlabeled parking images.

Output: pretrained visual encoder.

The SSL encoder is a representation learner, not the final parking
system by itself.

# 2. MoCo-style SSL

## 2.1 Recommended architecture

Start with ResNet-18.

``` text
Image
 ↓
ResNet-18
 ↓
Global Average Pooling
 ↓
Projection MLP
 ↓
Embedding
```

Two encoders are maintained:

``` text
encoder_q
encoder_k
```

The key encoder is updated by:

``` text
θ_k ← m θ_k + (1-m) θ_q
```

## 2.2 Contrastive learning

For query `q`, positive key `k+` and queued negative keys `k_i`:

``` text
positive_logit = q · k+ / τ
negative_logit_i = q · k_i / τ
```

Use cross-entropy/InfoNCE with the positive key as the target.

The implementation must explicitly handle:

-   L2 normalization.
-   Positive logit.
-   Negative logits.
-   Temperature.
-   Queue update.
-   Queue pointer.
-   Momentum encoder update.

## 2.3 Augmentations

Initial candidates:

-   RandomResizedCrop.
-   HorizontalFlip.
-   ColorJitter.
-   RandomGrayscale.
-   GaussianBlur.

Augmentations should preserve semantic identity for parking scenes. SSL
augmentation can be stronger than detection augmentation.

## 2.4 Starting configuration

``` yaml
encoder: resnet18
image_size: 224
embedding_dim: 128
temperature: 0.2
momentum: 0.999
queue_size: 4096
batch_size: 64
optimizer: SGD
epochs: 100
```

These are starting values, not guaranteed optimal values.

## 2.5 SSL evaluation

Training loss alone is insufficient.

Use at least one of:

-   linear evaluation
-   k-NN evaluation
-   downstream transfer

The most important project-level validation is downstream
detection/segmentation.

# 3. Custom detector

The custom detector exists to answer whether the learned representation
helps downstream detection.

A manageable first architecture is:

``` text
ResNet-18 backbone
→ lightweight FPN-style features
→ detection head
```

Do not reproduce an entire modern YOLO architecture unless there is a
strong reason.

## 3.1 Initialization variants

``` text
A: Random
B: ImageNet
C: MoCo
```

Keep the downstream detector architecture the same for A/B/C.

# 4. YOLO baseline

YOLO is the production-oriented baseline.

It must be evaluated on the same parking detection task and the same
test set as the custom detector.

Fair comparison:

``` text
Custom detector + parking training
vs
YOLO + parking fine-tuning
```

Unfair primary comparison:

``` text
Custom detector on parking test
vs
raw YOLO on a different dataset
```

# 5. Segmentation

## 5.1 Architecture

``` text
Encoder
 ↓
feature maps
 ↓
U-Net-style decoder
 ↓
1-channel mask
```

Compare:

``` text
Random encoder
ImageNet encoder
MoCo encoder
```

## 5.2 Loss

``` text
L = BCE + λ DiceLoss
```

Start with `λ = 1.0` and tune only through validation.

## 5.3 Metrics

-   IoU
-   Dice
-   Precision
-   Recall
-   Pixel accuracy

For imbalanced segmentation, prioritize IoU and Dice.

# 6. Experiment configuration

Every training run must have a config, for example:

``` yaml
experiment:
  name: detector_moco_v1
  seed: 42

dataset:
  version: parking_v1
  split: fixed_v1

model:
  backbone: resnet18
  pretrained: moco
  detector: custom_fpn

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001

evaluation:
  metrics: [map50, map5095, precision, recall]
```

# 7. Research questions

1.  Does SSL improve detection over random initialization?
2.  Does domain-specific SSL help beyond ImageNet initialization?
3.  How does the best custom detector compare with fine-tuned YOLO?
4.  Does SSL transfer to segmentation?
5.  Does SSL improve performance with limited labels?
6.  What is the accuracy/latency trade-off?
