#!/usr/bin/env python3
"""Offline, exact-pixel PNG comparison for controlled STT visual experiments.

No game assets are included. No alignment, rendering, texture conversion, or
claims of original-game fidelity are performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageStat, UnidentifiedImageError

MAX_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 4_000_000
Image.MAX_IMAGE_PIXELS = None  # Explicit strict pixel budget is enforced before decoding.


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_png(path: Path) -> Image.Image:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Not a regular file: {path}")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("PNG exceeds 32 MiB input limit")
    try:
        with Image.open(path) as probe:
            if probe.format != "PNG":
                raise ValueError("Only PNG inputs are supported")
            if probe.width * probe.height > MAX_PIXELS:
                raise ValueError("PNG exceeds 4 million pixels")
            probe.verify()
        with Image.open(path) as src:
            rgba = src.convert("RGBA")
            rgba.load()
            return rgba
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
        raise ValueError(f"Invalid or unsafe PNG: {e}") from e


def in_git_worktree(path: Path) -> bool:
    return any((parent / ".git").exists() for parent in (path, *path.parents))


def silhouette_counts(ia: Image.Image, ib: Image.Image, threshold: int) -> dict:
    """Binary alpha silhouette overlap; no registration, scaling or resampling."""
    if not isinstance(threshold, int) or not 0 <= threshold <= 254:
        raise ValueError("Alpha threshold must be an integer from 0 through 254")
    reference_only = candidate_only = intersection = 0
    ref_count = cand_count = 0
    for alpha_a, alpha_b in zip(ia.getchannel("A").get_flattened_data(), ib.getchannel("A").get_flattened_data()):
        fg_a, fg_b = alpha_a > threshold, alpha_b > threshold
        ref_count += fg_a
        cand_count += fg_b
        intersection += fg_a and fg_b
        reference_only += fg_a and not fg_b
        candidate_only += fg_b and not fg_a
    union = intersection + reference_only + candidate_only
    return {
        "alpha_threshold_0_255": threshold,
        "reference_foreground_pixels": ref_count,
        "candidate_foreground_pixels": cand_count,
        "intersection_pixels": intersection,
        "union_pixels": union,
        "reference_only_pixels": reference_only,
        "candidate_only_pixels": candidate_only,
        "silhouette_iou_0_1": None if union == 0 else round(intersection / union, 8),
        "silhouette_caveat": "Alpha>threshold mask only. Fully opaque captures produce full-frame silhouettes; no camera alignment or fidelity claim.",
    }


def compare(a: Path, b: Path, out: Path, diff_png: bool = False, alpha_threshold: int = 127) -> dict:
    if not isinstance(alpha_threshold, int) or not 0 <= alpha_threshold <= 254:
        raise ValueError("Alpha threshold must be an integer from 0 through 254")
    a = a.resolve(strict=True)
    b = b.resolve(strict=True)
    out = out.resolve(strict=False)
    if a == b:
        raise ValueError("Inputs must be distinct files")
    if out.exists():
        raise ValueError("Output directory must be new")
    if in_git_worktree(out):
        raise ValueError("Output must be outside any Git working tree")
    ia, ib = load_png(a), load_png(b)
    if ia.size != ib.size:
        raise ValueError(f"Dimension mismatch: {ia.size} vs {ib.size}; no resampling")
    delta = ImageChops.difference(ia, ib)
    stat = ImageStat.Stat(delta)
    width, height = ia.size
    changed = 0
    maximum = 0
    for px in delta.get_flattened_data():
        if any(px):
            changed += 1
        maximum = max(maximum, *px)
    mae = sum(stat.mean) / 4
    mse = sum(r * r for r in stat.rms) / 4
    report = {
        "schema": "stt-png-comparison/1",
        "inputs": [{"sha256": sha256(p), "bytes": p.stat().st_size} for p in (a, b)],
        "width": width, "height": height,
        "compared_channels": "RGBA, straight channel values, no color management",
        "mean_absolute_error_0_255": round(mae, 8),
        "root_mean_square_error_0_255": round(math.sqrt(mse), 8),
        "max_channel_difference_0_255": maximum,
        "pixels_changed": changed,
        "percent_pixels_changed": round(changed * 100 / (width * height), 8),
        "psnr_db": None if mse == 0 else round(10 * math.log10((255 * 255) / mse), 8),
        "identical_pixels": changed == 0,
        "silhouette": silhouette_counts(ia, ib, alpha_threshold),
        "caveat": "Pixel metrics only: no camera/pose/light/material alignment, no proof of MH4U fidelity.",
    }
    out.mkdir(parents=True, exist_ok=False)
    (out / "comparison.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if diff_png:
        heat = Image.new("RGB", ia.size)
        heat.putdata([(max(px), 0, 0) for px in delta.get_flattened_data()])
        heat.save(out / "difference.png")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Fresh PRIVATE output directory outside Git")
    parser.add_argument("--diff-png", action="store_true", help="Write diagnostic heatmap (PRIVATE)")
    parser.add_argument("--alpha-threshold", type=int, default=127,
                        help="Foreground is alpha > threshold (0..254); default 127")
    args = parser.parse_args()
    try:
        result = compare(args.reference, args.candidate, args.out, args.diff_png, args.alpha_threshold)
    except (ValueError, FileNotFoundError, PermissionError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps({k: result[k] for k in ("identical_pixels", "pixels_changed", "mean_absolute_error_0_255", "psnr_db")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
