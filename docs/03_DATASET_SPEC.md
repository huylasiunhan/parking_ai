# Dataset Specification

## 1. Dataset goals

The project needs data for:

1.  Vehicle detection.
2.  Parking-slot geometry.
3.  Parking-space segmentation.
4.  Unlabeled self-supervised learning.

One dataset may cover all tasks, or multiple compatible datasets may be
used. If multiple datasets are used, document them separately and never
silently mix their label definitions.

## 2. Dataset groups

### Detection labels

``` text
class_id
x_min
 y_min
x_max
 y_max
```

### Parking slot polygons

``` json
{
  "slot_id": 17,
  "polygon": [[100,100],[180,105],[175,190],[95,185]]
}
```

### Segmentation mask

Initial binary mask:

``` text
0 = background
1 = parking-space
```

### SSL images

No labels required.

## 3. Directory convention

``` text
datasets/
└── parking_v1/
    ├── images/train/
    ├── images/val/
    ├── images/test/
    ├── labels/train/
    ├── labels/val/
    ├── labels/test/
    ├── masks/train/
    ├── masks/val/
    ├── masks/test/
    ├── slots/
    └── metadata.json
```

## 4. Splitting rules

Target split can begin around:

``` text
70% train
15% validation
15% test
```

But the critical rule is **no temporal leakage**.

If images come from video, do not randomly split adjacent frames. Split
by video, scene, camera or time segment.

## 5. Dataset versioning

Use versions such as:

``` text
parking_v1
parking_v2
```

Record:

-   source
-   license
-   acquisition date
-   preprocessing
-   removed files
-   annotation changes
-   split identifier

## 6. Quality checks

Before training:

-   Load every image or run a complete validation scan.
-   Verify image/label correspondence.
-   Check class IDs.
-   Check box boundaries.
-   Check polygon coordinates.
-   Check mask dimensions and values.
-   Visualize at least 100 random samples.
-   Detect corrupted images.

## 7. Data-efficiency subsets

Create nested subsets:

``` text
10% ⊂ 25% ⊂ 50% ⊂ 100%
```

Keep validation and test unchanged.

## 8. Dataset acceptance checklist

-   [ ] License documented.
-   [ ] Split fixed.
-   [ ] No temporal leakage.
-   [ ] Labels validated.
-   [ ] Visualizer works.
-   [ ] Dataset version recorded.
-   [ ] Class mapping documented.
