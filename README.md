# Smart_Augmentation

A complete Python library for advanced image and video augmentation — including geometric, color, noise, and occlusion-based transformations.

## Features

### Geometric Transformations
- **Flip** (Horizontal, Vertical, Random)
- **Rotate** (Custom angle, random)
- **Scale** (Zoom in/out)
- **Shear** (Affine shear transform)
- **Crop** (Center, Random, or Region-based)
- **Perspective Transform** (Warping simulation)
- **Elastic Deformation** (Realistic non-linear distortion)

### Color Transformations
- **Brightness Adjustment**
- **Contrast Adjustment**
- **Hue Shift**
- **Gamma Correction**
- **Solarize Effect**
- **Posterize Effect**
- **Color Jitter** (Combined random color augmentation)

### Noise Transformations
- **Gaussian Noise**
- **Speckle Noise**
- **Motion Blur**
- **Defocus Blur**
- **Salt & Pepper Noise**

### Occlusion Techniques
- **Cutout** (Random black square)
- **Hide-and-Seek** (Random grid occlusion)
- **GridMask** (Structured occlusion)
- **Mixup** (Linear blending of two images)
- **CutMix** (Region replacement)
- **FMix** (Frequency-based mask blending)

### Video Augmentation
- **Brightness Flicker**
- **Temporal Noise**
- **Random Crop**
- **Rotation**
- **Color Jitter**
- **Motion Blur (Temporal Blending)**

### Analysis & Reporting
- **Image Analysis:** brightness, contrast, sharpness, color balance, entropy
- **Automatic Report Generation:** generates text-based summary for all images in a folder
- **Batch Augmentation:** apply multiple augmentations at once to image or video folders


## Installation

You can install the package directly from [PyPI](https://pypi.org/project/smart-augmentation):

```bash
pip install smart_augmentation
```

## Analysis
```bash
from smart_augmentation import utils

# ✅ Path setup
dataset_path = "Dataset"
output_dir = "Dataset_augmented"
report_path = "augmentation_report.txt"
image_path = "Dataset/sample1.jpg"  # change as needed

# -------------------------------
# Test analyze_image
# -------------------------------
image = utils.load_image(image_path)
analysis = utils.analyze_image(image)
print("🔹 Image Analysis:")

# -------------------------------
# Test analyze_image_for_transforms
# -------------------------------
transform_recs = utils.analyze_image_for_transforms(image)
print("\n🔹 Recommended Transformations:")
print(transform_recs)

# -------------------------------
# Test generate_report_for_folder
# -------------------------------
report = utils.generate_report_for_folder(dataset_path, report_path)
print("\n📄 Generated Report:")
print(report)

# -------------------------------
# Test apply_transform_by_name
# -------------------------------
transformed = utils.apply_transform_by_name(image, "rotate", angle=15)
print("\n✅ Applied single transform (rotate)")
# Show inline in Jupyter
from matplotlib import pyplot as plt
import cv2
plt.imshow(cv2.cvtColor(transformed, cv2.COLOR_BGR2RGB))
plt.title("Rotated Image")
plt.axis('off')
plt.show()

# -------------------------------
# Test process_single_image
# -------------------------------
analysis, saved_files = utils.process_single_image(
    image_path=image_path,
    output_dir=output_dir,
    transform_names=["flip", "color_jitter", "gaussian_noise"]
)
print("\n📊 Single Image Analysis:")
pprint.pprint(analysis)
print("\n🖼️ Saved Files:")
print(saved_files)

# -------------------------------
# Test apply_transformations_to_dataset
# -------------------------------
report_path, saved_files = utils.apply_transformations_to_dataset(
    folder_path=dataset_path,
    output_dir=output_dir,
    apply_all=True  # or False to use auto-recommendations
)
print("\n📦 Dataset Augmentation Completed.")
print("📄 Report saved at:", report_path)
print("🖼️ Total images saved:", len(saved_files))
```

## Geometric Augmentation
```bash
from smart_augmentation import geometric
rotated = geometric.rotate(image, angle=30)
flipped_vertical = geometric.flip(image, mode="vertical")
flipped_horizontal = geometric.flip(image, mode="horizontal")
scaled = geometric.scale(image, scale_range=(0.8, 1.2))
translated = geometric.translate(image, shift_x=0.1, shift_y=0.1)
sheared = geometric.shear(image, shear_range=0.2)
cropped = geometric.crop(image, crop_ratio=0.8, center=False)
transformed = geometric.perspective_transform(image, margin=60)
deformation = geometric.elastic_deformation(image, alpha=40, sigma=8)
all_aug = geometric.all_geometric(
    image,
    apply_random=True,
    flip_mode="horizontal",
    rotation_angle=15,
    shift_x=0.1,
    shift_y=0.1,
    scale_range=(0.8, 1.2),
    shear_range=0.2,
    crop_ratio=0.8,
    perspective_margin=60,
    alpha=40,
    sigma=8
)
```
## Color Augmentation
```bash
from smart_augmentation import color

# Individual color transformations
bright = color.adjust_brightness(image, factor=1.2)
contrasted = color.adjust_contrast(image, factor=1.5)
saturated = color.adjust_saturation(image, factor=1.3)
gamma_corrected = color.gamma_correction(image, gamma_range=(0.8, 1.2))
posterized = color.posterize(image, bits=4)
solarized = color.solarize(image, threshold=128)
hue_shifted = color.shift_hue(image, shift=10)
grayscale = color.grayscale(image, alpha=0.5)

# Apply random color jitter (brightness, contrast, saturation, hue)
jittered = color.color_jitter(image)

# Apply all color augmentations (randomized or fixed)
all_color = color.all_color(
    image,
    apply_random=True,
    brightness_factor=1.2,
    contrast_factor=1.5,
    saturation_factor=1.3,
    hue_delta=0.05,
    gamma_value=1.2,
    solarize_threshold=128,
    posterize_bits=4
)
```
## Noise Augmentation
```bash
from smart_augmentation import noise

gaussian_noisy = noise.gaussian_noise(image, mean=0, std=25)
speckle_noisy = noise.speckle_noise(image)
salt_pepper_noisy = noise.salt_and_pepper(image, amount=0.02)
gaussian_noisy = noise.gaussian_blur(image, ksize=5)
motion_noisy = noise.motion_blur(image, kernel_size=9)
defocus_noisy = noise.defocus_blur(image, ksize=9)
all_noisy = noise.all_noise(
    image,
    apply_random=True,
    mean=0,
    std=10,
    amount=0.01,
    ksize=5,
    motion_kernel=9,
    defocus_kernel=9
)
```

## Video Augmentation
``` bash
from smart_augmentation import video

# Apply transformation to every frame
video.apply_transform_to_video(
    video_path="input.mp4",
    output_path="output_rotated.mp4",
    transform_func=lambda frame: geometric.rotate(frame, angle=15)
)

# Temporal transformation using sliding window (e.g., motion blur)
video.apply_temporal_transform(
    video_path="input.mp4",
    output_path="output_temporal_blur.mp4",
    transform_func=lambda frames: np.mean(frames, axis=0).astype(np.uint8),
    frame_window=3
)

# Built-in augmentations
video.video_brightness_flicker("input.mp4", "output_flicker.mp4", intensity=0.3)
video.video_temporal_noise("input.mp4", "output_temporal_noise.mp4", std=10)
video.video_random_crop("input.mp4", "output_crop.mp4", crop_ratio=0.9)
video.video_rotation("input.mp4", "output_rotated.mp4", angle=15)
video.video_color_jitter("input.mp4", "output_color_jitter.mp4")
video.video_motion_blur_temporal("input.mp4", "output_motion_blur.mp4")

# Apply multiple augmentations in batch
video.augment_video_batch(
    video_path="input.mp4",
    output_dir="augmented_videos",
    augmentations=["brightness_flicker", "rotation", "motion_blur_temporal"],
    prefix="aug"
)

# Extract frames for frame-level augmentation
frames = video.extract_frames("input.mp4", "frames_output", frame_rate=5)

# Combine frames back into a video
video.frames_to_video("frames_output", "reconstructed.mp4", fps=30)
```

