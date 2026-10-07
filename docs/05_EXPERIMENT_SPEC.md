# Experiment and Benchmark Specification

## 1. Core rule

The project must produce controlled evidence, not just screenshots.

The final test set is locked before final comparison.

``` text
train → fit parameters
validation → tune/select
test → final report
```

## 2. Required detection models

  Model   Encoder initialization   Detector
  ------- ------------------------ --------------------------
  A       Random                   Custom
  B       ImageNet                 Custom
  C       MoCo                     Custom
  D       COCO/public pretrained   YOLO + parking fine-tune

## 3. Controlled variables

For A/B/C keep constant:

-   architecture
-   data split
-   optimizer
-   epochs
-   batch size
-   learning-rate schedule
-   augmentation
-   evaluation code
-   seed policy

The major experimental variable is initialization/pretraining.

## 4. Detection metrics

Required:

-   Precision.
-   Recall.
-   mAP@50.
-   mAP@50:95.

Efficiency:

-   FPS.
-   Latency.
-   Parameter count.
-   FLOPs.
-   Checkpoint size.
-   GPU memory.

FPS must document hardware, input size, batch size and whether
preprocessing/postprocessing are included.

## 5. Data-efficiency experiment

Use nested labeled subsets:

``` text
10%
25%
50%
100%
```

Keep validation and test fixed.

Example result table:

  Labeled data     Random   ImageNet   MoCo   YOLO
  -------------- -------- ---------- ------ ------
  10%                 ---        ---    ---    ---
  25%                 ---        ---    ---    ---
  50%                 ---        ---    ---    ---
  100%                ---        ---    ---    ---

## 6. Robustness subsets

When enough data exists, evaluate:

-   small vehicles
-   occlusion
-   crowded scenes
-   poor lighting
-   distant vehicles

## 7. Segmentation benchmark

Compare Random/ImageNet/MoCo encoder initialization with the same
decoder.

Metrics:

-   IoU
-   Dice
-   Precision
-   Recall
-   Pixel accuracy

## 8. Statistical reliability

For important final results:

-   fix seeds where possible;
-   record hardware/software;
-   use repeated runs when compute allows;
-   report mean ± standard deviation for repeated runs.

Do not overinterpret tiny differences without uncertainty.

## 9. Ablation priorities

Recommended order:

1.  Random vs ImageNet vs MoCo.
2.  10/25/50/100% labels.
3.  Frozen vs fine-tuned encoder.
4.  SSL temperature/queue/momentum if needed.

Avoid running every imaginable ablation.

## 10. Experiment directory

``` text
experiments/
└── exp_001_moco_detector/
    ├── config.yaml
    ├── metrics.json
    ├── train.log
    ├── checkpoint.pt
    ├── curves.png
    └── notes.md
```

The directory should be sufficient to reconstruct what happened.

## 11. Final comparison table

``` text
Model | Pretraining | mAP50 | mAP50-95 | Precision | Recall | FPS | Params
```

Then explain:

1.  whether SSL helped;
2.  whether ImageNet was already strong;
3.  how YOLO compares;
4.  the accuracy/efficiency trade-off;
5.  which model should be used in production.
