"""Dataset splitting script with anti-temporal-leakage policy and data-efficiency subsets.

References:
- docs/03_DATASET_SPEC.md (Splitting rules & Data-efficiency subsets)
- docs/05_EXPERIMENT_SPEC.md (Benchmark protocol)
"""

import argparse
import random
from pathlib import Path


def split_by_groups(
    image_paths: list[Path],
    group_fn,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[list[Path], list[Path], list[Path]]:
    """Split images by groups (e.g., scene/camera/day) to prevent temporal leakage."""
    rng = random.Random(seed)
    groups: dict[str, list[Path]] = {}
    for p in image_paths:
        gid = group_fn(p)
        groups.setdefault(gid, []).append(p)

    group_keys = list(groups.keys())
    rng.shuffle(group_keys)

    n_total = len(image_paths)
    target_train = int(n_total * train_ratio)
    target_val = int(n_total * val_ratio)

    train_files: list[Path] = []
    val_files: list[Path] = []
    test_files: list[Path] = []

    for gid in group_keys:
        items = groups[gid]
        if len(train_files) + len(items) <= target_train or not train_files:
            train_files.extend(items)
        elif len(val_files) + len(items) <= target_val or not val_files:
            val_files.extend(items)
        else:
            test_files.extend(items)

    return sorted(train_files), sorted(val_files), sorted(test_files)


def create_nested_subsets(
    train_files: list[Path],
    ratios: list[float] = [0.10, 0.25, 0.50, 1.00],
    seed: int = 42,
) -> dict[str, list[Path]]:
    """Create nested data-efficiency subsets: 10% ⊂ 25% ⊂ 50% ⊂ 100%."""
    rng = random.Random(seed)
    shuffled = list(train_files)
    rng.shuffle(shuffled)

    subsets = {}
    for r in ratios:
        name = f"train_{int(r * 100)}pct"
        n = max(1, int(len(shuffled) * r))
        subsets[name] = sorted(shuffled[:n])
    return subsets


def main() -> None:
    parser = argparse.ArgumentParser(description="Split dataset preventing temporal leakage.")
    parser.add_argument("--data-dir", type=str, default="datasets/parking_v1")
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    root = Path(args.data_dir)
    images_dir = root / "images"
    all_images = list(images_dir.glob("**/*.[jJ][pP][gG]")) + list(images_dir.glob("**/*.[pP][nN][gG]"))

    if not all_images:
        print(f"No images found in {images_dir}. Create subsets once images are downloaded.")
        return

    # Default group function: splits by parent directory name (scene/session)
    group_fn = lambda p: p.parent.name

    train_files, val_files, test_files = split_by_groups(
        all_images,
        group_fn=group_fn,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
    )

    print(f"Total: {len(all_images)} images")
    print(f"Train: {len(train_files)} ({len(train_files)/len(all_images):.1%})")
    print(f"Val:   {len(val_files)} ({len(val_files)/len(all_images):.1%})")
    print(f"Test:  {len(test_files)} ({len(test_files)/len(all_images):.1%})")

    # Generate nested subsets
    subsets = create_nested_subsets(train_files, seed=args.seed)
    splits_dir = root / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)

    for subset_name, files in subsets.items():
        subset_file = splits_dir / f"{subset_name}.txt"
        with open(subset_file, "w") as f:
            for p in files:
                f.write(f"{p.resolve()}\n")
        print(f"Saved {subset_name} ({len(files)} files) -> {subset_file}")

    for split_name, files in [("val", val_files), ("test", test_files)]:
        split_file = splits_dir / f"{split_name}.txt"
        with open(split_file, "w") as f:
            for p in files:
                f.write(f"{p.resolve()}\n")
        print(f"Saved {split_name} ({len(files)} files) -> {split_file}")


if __name__ == "__main__":
    main()
