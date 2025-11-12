# smart_augmentation/__init__.py
from . import geometric
from . import color
from . import noise
from . import occlusion
from . import utils
from . import video

# Import key functions for easy access
from .video import (
    apply_transform_to_video,
    augment_video_batch,
    extract_frames,
    frames_to_video,
    video_brightness_flicker,
    video_temporal_noise,
    video_random_crop,
    video_rotation,
    video_color_jitter,
    video_motion_blur_temporal
)

__all__ = [
    "geometric",
    "color", 
    "noise",
    "occlusion",
    "utils",
    "video",
    # Video augmentation functions
    "apply_transform_to_video",
    "augment_video_batch",
    "extract_frames",
    "frames_to_video",
    "video_brightness_flicker",
    "video_temporal_noise",
    "video_random_crop",
    "video_rotation",
    "video_color_jitter",
    "video_motion_blur_temporal"
]

__version__ = "0.2.0"