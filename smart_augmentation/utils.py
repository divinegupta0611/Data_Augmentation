# smart_augmentation/utils.py
import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from .color import (
    adjust_brightness,
    adjust_contrast,
    adjust_saturation,
    shift_hue,
    gamma_correction,
    color_jitter,
    grayscale,
    solarize,
    posterize,
)
from .geometric import (
    flip,
    rotate,
    translate,
    scale,
    shear,
    crop,
    perspective_transform,
    elastic_deformation,
)
from .noise import (
    gaussian_noise,
    salt_and_pepper,
    speckle_noise,
    gaussian_blur,
    motion_blur,
    defocus_blur,
)
from .occlusion import (
    cutout,
    hide_and_seek,
    gridmask,
    mixup,
    cutmix,
    fmix,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .utils import clip
else:
    clip = None  # define a fallback


ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

def clip(image: np.ndarray) -> np.ndarray:
    """Clip pixel values to [0,255] and convert to uint8"""
    return np.clip(image, 0, 255).astype(np.uint8)

def load_image(path: str) -> Optional[np.ndarray]:
    if not os.path.exists(path):
        return None
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return img

def save_image(path: str, image: np.ndarray) -> None:
    # Use imencode->tofile to support unicode paths on Windows
    ext = os.path.splitext(path)[1]
    if ext == "":
        ext = ".jpg"
        path += ext
    success, enc = cv2.imencode(ext, clip(image))
    if not success:
        raise IOError(f"Failed to encode image for {path}")
    enc.tofile(path)

def is_image_file(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTS

# ---------- Image analysis heuristics ----------
def analyze_image(image: np.ndarray) -> Dict[str, Dict]:
    """
    Inspect an image and return recommended augmentation types with reasons.
    Returns a dict like:
    {
      "brightness": {"score": 34.2, "recommend": True, "reason": "..."},
      "contrast": ...
    }
    """
    if image is None:
        return {}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mean_saturation = float(np.mean(hsv[..., 1]))
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = float(lap.var())

    # detect large uniform/occluded regions (dark or bright blocks)
    h, w = gray.shape
    non_zero_ratio = float(np.count_nonzero(gray) / (h * w))
    # detect heavy black regions (possible occlusion)
    black_ratio = float(np.sum(gray < 10) / (h * w))

    recommendations = {}

    # Brightness
    rec_brightness = mean_brightness < 80 or mean_brightness > 200
    recommendations["brightness"] = {
        "score": mean_brightness,
        "recommend": bool(rec_brightness),
        "reason": (
            "Image is dark (mean brightness {:.1f})".format(mean_brightness)
            if mean_brightness < 80
            else ("Image is very bright (mean {:.1f})".format(mean_brightness) if mean_brightness > 200 else "Brightness within normal range")
        ),
        "suggestions": ["adjust_brightness", "gamma_correction", "color_jitter"]
    }

    # Contrast
    rec_contrast = contrast < 40
    recommendations["contrast"] = {
        "score": contrast,
        "recommend": bool(rec_contrast),
        "reason": "Low contrast (std {:.1f})".format(contrast) if rec_contrast else "Contrast OK",
        "suggestions": ["adjust_contrast", "contrast_jitter", "color_jitter"]
    }

    # Saturation
    rec_saturation = mean_saturation < 30
    recommendations["saturation"] = {
        "score": mean_saturation,
        "recommend": bool(rec_saturation),
        "reason": ("Low saturation ({:.1f})".format(mean_saturation) if rec_saturation else "Saturation OK"),
        "suggestions": ["adjust_saturation", "shift_hue", "color_jitter"]
    }

    # Sharpness / blur
    rec_blur = lap_var < 100.0
    recommendations["blur"] = {
        "score": lap_var,
        "recommend": bool(rec_blur),
        "reason": ("Image looks blurry (laplacian var {:.1f})".format(lap_var) if rec_blur else "Image is sharp"),
        "suggestions": ["gaussian_blur", "motion_blur", "defocus_blur", "speckle_noise"]
    }

    # Occlusion / blocked area
    rec_occlusion = black_ratio > 0.15 or (non_zero_ratio < 0.6)
    recommendations["occlusion"] = {
        "score": black_ratio,
        "recommend": bool(rec_occlusion),
        "reason": ("Large dark area detected (black ratio {:.2f})".format(black_ratio) if rec_occlusion else "No large occlusion detected"),
        "suggestions": ["cutout", "hide_and_seek", "gridmask"]
    }

    # general: recommend color and geometric variety if image is "too similar" (simple heuristic)
    recommendations["general"] = {
        "recommend": True,
        "reason": "Always useful to add geometric and color augmentations to increase dataset variety.",
        "suggestions": ["flip", "rotate", "crop", "scale", "color_jitter", "posterize", "solarize"]
    }

    return recommendations

# ---------- Apply augmentation helpers ----------
def apply_transform_by_name(image: np.ndarray, transform_name: str, **kwargs) -> np.ndarray:
    """
    Map a transform name (string) to the actual function call and return the transformed image.
    Supports common transform names used in analyze_image suggestions.
    """
    tname = transform_name.lower()
    img = image.copy()
    if tname == "adjust_brightness":
        return adjust_brightness(img, factor=kwargs.get("factor", 0.2))
    if tname == "adjust_contrast":
        return adjust_contrast(img, factor=kwargs.get("factor", 0.3))
    if tname == "adjust_saturation":
        return adjust_saturation(img, factor=kwargs.get("factor", 0.3))
    if tname == "shift_hue":
        return shift_hue(img, shift=kwargs.get("shift", 10))
    if tname == "gamma_correction":
        return gamma_correction(img, gamma_range=kwargs.get("gamma_range", (0.8, 1.2)))
    if tname == "color_jitter":
        return color_jitter(img)
    if tname == "grayscale":
        return grayscale(img, alpha=kwargs.get("alpha", 0.5))
    if tname == "solarize":
        return solarize(img, threshold=kwargs.get("threshold", 128))
    if tname == "posterize":
        return posterize(img, bits=kwargs.get("bits", 4))

    # geometric
    if tname == "flip":
        return flip(img, mode=kwargs.get("mode", "horizontal"))
    if tname == "rotate":
        return rotate(img, angle=kwargs.get("angle", 15))
    if tname == "translate":
        return translate(img, shift_x=kwargs.get("shift_x", 0.1), shift_y=kwargs.get("shift_y", 0.1))
    if tname == "scale":
        return scale(img, scale_range=kwargs.get("scale_range", (0.8, 1.2)))
    if tname == "shear":
        return shear(img, shear_range=kwargs.get("shear_range", 0.2))
    if tname == "crop":
        return crop(img, crop_ratio=kwargs.get("crop_ratio", 0.8), center=kwargs.get("center", False))
    if tname == "perspective_transform":
        return perspective_transform(img, margin=kwargs.get("margin", 60))
    if tname == "elastic_deformation":
        return elastic_deformation(img, alpha=kwargs.get("alpha", 40), sigma=kwargs.get("sigma", 8))

    # noise/blur
    if tname == "gaussian_noise":
        return gaussian_noise(img, mean=kwargs.get("mean", 0), std=kwargs.get("std", 10))
    if tname == "salt_and_pepper":
        return salt_and_pepper(img, amount=kwargs.get("amount", 0.01))
    if tname == "speckle_noise":
        return speckle_noise(img)
    if tname == "gaussian_blur":
        return gaussian_blur(img, ksize=kwargs.get("ksize", 5))
    if tname == "motion_blur":
        return motion_blur(img, kernel_size=kwargs.get("kernel_size", 9))
    if tname == "defocus_blur":
        return defocus_blur(img, ksize=kwargs.get("ksize", 9))

    # occlusion-only transforms that may require a second image are not supported here by default
    raise ValueError(f"Unknown transform: {transform_name}")

# ---------- Dataset-level functions ----------
# ---------- Image analysis ----------
def analyze_image_for_transforms(image: np.ndarray) -> List[str]:
    """
    Analyze the image and recommend which augmentations to apply dynamically.
    Returns a list of recommended transformations.
    """
    recommendations = []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Brightness
    mean_brightness = np.mean(gray)
    if mean_brightness < 100:
        recommendations.append("adjust_brightness")
    
    # Contrast
    if np.std(gray) < 50:
        recommendations.append("adjust_contrast")

    # Sharpness / blur
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var < 100:
        recommendations.append("sharpen")  # optional

    # Saturation check
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if np.std(hsv[..., 1]) < 20:
        recommendations.append("adjust_saturation")

    # Orientation / aspect ratio
    h, w = image.shape[:2]
    if h != w:
        recommendations.append("crop")

    # Always include geometric & color variety
    recommendations.extend(["flip", "rotate", "scale", "color_jitter", "posterize", "solarize"])

    # Remove duplicates
    recommendations = list(set(recommendations))

    return recommendations

def generate_report_for_folder(folder_path: str, report_path: str) -> Dict[str, List[str]]:
    """
    Generate a report for all images in a folder.
    Dynamically recommends transformations for each image.
    """
    folder_path = Path(folder_path)
    images = [p for p in folder_path.iterdir() if p.suffix.lower() in ALLOWED_EXTS]

    report = {}
    for img_path in images:
        image = load_image(str(img_path))
        if image is None:
            continue
        recommendations = analyze_image_for_transforms(image)
        report[img_path.name] = recommendations

    # Write to report.txt
    with open(report_path, "w", encoding="utf-8") as f:
        for img_name, recs in report.items():
            f.write(f"{img_name}: recommendations -> {', '.join(recs)}\n")

    return report

def apply_transformations_to_dataset(
    folder_path: str,
    output_dir: str,
    apply_all: bool = False,
    transform_names: Optional[List[str]] = None,
    save_report: bool = True
) -> Tuple[str, List[str]]:
    """
    Iterate images in folder_path and save transformed images into output_dir.
    - If apply_all=True, apply a representative set of transforms to every image and
      save them (one file per transform).
    - If transform_names is provided, apply only those transforms to each image.
    Returns (report_path, list_of_saved_files)
    """
    folder_path = os.path.abspath(folder_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    report_lines = []

    # default transforms to use when apply_all True
    default_transforms = [
        "flip",
        "rotate",
        "crop",
        "adjust_brightness",
        "adjust_contrast",
        "color_jitter",
        "gaussian_noise",
        "gaussian_blur",
        "cutout",
    ]

    for fname in sorted(os.listdir(folder_path)):
        fpath = os.path.join(folder_path, fname)
        if not is_image_file(fpath):
            continue
        img = load_image(fpath)
        if img is None:
            report_lines.append(f"{fname}: FAILED_TO_LOAD\n")
            continue

        base_name = os.path.splitext(fname)[0]
        # analyze
        recs = analyze_image(img)
        rec_list = []
        for key, val in recs.items():
            if isinstance(val, dict) and val.get("recommend"):
                rec_list.extend(val.get("suggestions", []))
        rec_list = sorted(set(rec_list))

        report_lines.append(f"{fname}: recommendations -> {', '.join(rec_list) if rec_list else 'none'}\n")

        transforms_to_apply = []
        if transform_names:
            transforms_to_apply = transform_names
        elif apply_all:
            transforms_to_apply = default_transforms
        else:
            transforms_to_apply = rec_list if rec_list else []

        # save original copy
        orig_out = os.path.join(output_dir, f"{base_name}__orig.jpg")
        save_image(orig_out, img)
        saved_files.append(orig_out)

        # apply transforms
        for t in transforms_to_apply:
            try:
                transformed = apply_transform_by_name(img, t)
            except Exception as e:
                # skip complex transforms that need second image etc.
                report_lines.append(f"{fname}: transform {t} FAILED -> {e}\n")
                continue
            out_name = os.path.join(output_dir, f"{base_name}__{t}.jpg")
            save_image(out_name, transformed)
            saved_files.append(out_name)

    report_path = os.path.join(output_dir, "smart_augmentation_report.txt")
    if save_report:
        with open(report_path, "w", encoding="utf-8") as f:
            f.writelines(report_lines)

    return report_path, saved_files

# ---------- Utility: process single image with choice ----------
def process_single_image(
    image_path: str,
    output_dir: str,
    transform_names: Optional[List[str]] = None,
    save_original: bool = True
) -> Tuple[Dict, List[str]]:
    """
    Analyze image and optionally apply given transforms (list of names). Returns (analysis, saved_files)
    """
    os.makedirs(output_dir, exist_ok=True)
    img = load_image(image_path)
    if img is None:
        raise FileNotFoundError(image_path)
    analysis = analyze_image(img)
    saved = []
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    if save_original:
        orig_out = os.path.join(output_dir, f"{base_name}__orig.jpg")
        save_image(orig_out, img)
        saved.append(orig_out)
    if transform_names:
        for t in transform_names:
            try:
                out = apply_transform_by_name(img, t)
            except Exception as e:
                continue
            out_path = os.path.join(output_dir, f"{base_name}__{t}.jpg")
            save_image(out_path, out)
            saved.append(out_path)
    return analysis, saved

def clip(image):
    """Ensure pixel values are within [0, 255]."""
    return np.clip(image, 0, 255).astype(np.uint8)
