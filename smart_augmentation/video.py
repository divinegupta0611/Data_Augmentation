# smart_augmentation/video.py
import cv2
import numpy as np
import os
from typing import Optional, List, Callable
from pathlib import Path

def apply_transform_to_video(
    video_path: str,
    output_path: str,
    transform_func: Callable,
    transform_kwargs: Optional[dict] = None,
    fps: Optional[float] = None,
    codec: str = 'mp4v'
) -> bool:
    """
    Apply a transformation function to every frame of a video.
    
    Args:
        video_path: Path to input video
        output_path: Path to save augmented video
        transform_func: Function that takes an image and returns transformed image
        transform_kwargs: Dictionary of kwargs to pass to transform_func
        fps: Output FPS (if None, uses source FPS)
        codec: FourCC codec string
    
    Returns:
        True if successful, False otherwise
    """
    if transform_kwargs is None:
        transform_kwargs = {}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    
    # Get video properties
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_fps = fps if fps is not None else source_fps
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        return False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply transformation
            transformed_frame = transform_func(frame, **transform_kwargs)
            out.write(transformed_frame.astype(np.uint8))
        
        return True
    except Exception as e:
        print(f"Error during video processing: {e}")
        return False
    finally:
        cap.release()
        out.release()


def apply_temporal_transform(
    video_path: str,
    output_path: str,
    transform_func: Callable,
    frame_window: int = 3,
    transform_kwargs: Optional[dict] = None,
    fps: Optional[float] = None,
    codec: str = 'mp4v'
) -> bool:
    """
    Apply temporal transformation using a sliding window of frames.
    Useful for temporal consistency or motion-based augmentations.
    
    Args:
        video_path: Path to input video
        output_path: Path to save augmented video
        transform_func: Function that takes list of frames and returns transformed frame
        frame_window: Number of frames to pass to transform function
        transform_kwargs: Dictionary of kwargs to pass to transform_func
        fps: Output FPS (if None, uses source FPS)
        codec: FourCC codec string
    
    Returns:
        True if successful, False otherwise
    """
    if transform_kwargs is None:
        transform_kwargs = {}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_fps = fps if fps is not None else source_fps
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        return False
    
    frame_buffer = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_buffer.append(frame)
            if len(frame_buffer) > frame_window:
                frame_buffer.pop(0)
            
            if len(frame_buffer) == frame_window:
                transformed_frame = transform_func(frame_buffer, **transform_kwargs)
                out.write(transformed_frame.astype(np.uint8))
        
        return True
    except Exception as e:
        print(f"Error during temporal video processing: {e}")
        return False
    finally:
        cap.release()
        out.release()


def video_brightness_flicker(video_path: str, output_path: str, intensity: float = 0.3):
    """Add random brightness flickering effect to video."""
    def flicker_transform(frame, intensity):
        from .color import adjust_brightness
        return adjust_brightness(frame, factor=intensity)
    
    return apply_transform_to_video(
        video_path, output_path, 
        flicker_transform, 
        {'intensity': intensity}
    )


def video_temporal_noise(video_path: str, output_path: str, std: float = 10):
    """Add temporal noise that changes per frame."""
    def noise_transform(frame, std):
        from .noise import gaussian_noise
        return gaussian_noise(frame, std=std)
    
    return apply_transform_to_video(
        video_path, output_path,
        noise_transform,
        {'std': std}
    )


def video_random_crop(video_path: str, output_path: str, crop_ratio: float = 0.9):
    """Apply consistent random crop across video."""
    # Determine crop coordinates once
    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    cap.release()
    
    if not ret:
        return False
    
    h, w = first_frame.shape[:2]
    new_h, new_w = int(h * crop_ratio), int(w * crop_ratio)
    startx = np.random.randint(0, max(1, w - new_w))
    starty = np.random.randint(0, max(1, h - new_h))
    
    def crop_transform(frame, startx, starty, new_w, new_h, w, h):
        cropped = frame[starty:starty+new_h, startx:startx+new_w]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
    
    return apply_transform_to_video(
        video_path, output_path,
        crop_transform,
        {'startx': startx, 'starty': starty, 'new_w': new_w, 'new_h': new_h, 'w': w, 'h': h}
    )


def video_rotation(video_path: str, output_path: str, angle: float = 15):
    """Apply consistent rotation across video."""
    rotation_angle = np.random.uniform(-angle, angle)
    
    def rotate_transform(frame, angle):
        from .geometric import rotate
        return rotate(frame, angle=0)  # Use fixed angle
    
    # Get first frame dimensions for rotation matrix
    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    cap.release()
    
    if not ret:
        return False
    
    h, w = first_frame.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rotation_angle, 1.0)
    
    def fixed_rotate(frame, M, w, h):
        return cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    
    return apply_transform_to_video(
        video_path, output_path,
        fixed_rotate,
        {'M': M, 'w': w, 'h': h}
    )


def video_color_jitter(video_path: str, output_path: str):
    """Apply color jitter that varies per frame."""
    def jitter_transform(frame):
        from .color import color_jitter
        return color_jitter(frame)
    
    return apply_transform_to_video(video_path, output_path, jitter_transform)


def video_motion_blur_temporal(video_path: str, output_path: str):
    """Apply motion blur using temporal frame blending."""
    def temporal_blur(frames):
        if len(frames) < 2:
            return frames[-1]
        # Blend multiple frames
        blended = frames[0].astype(np.float32)
        for i in range(1, len(frames)):
            blended += frames[i].astype(np.float32)
        blended /= len(frames)
        return np.clip(blended, 0, 255).astype(np.uint8)
    
    return apply_temporal_transform(
        video_path, output_path,
        temporal_blur,
        frame_window=3
    )


def augment_video_batch(
    video_path: str,
    output_dir: str,
    augmentations: Optional[List[str]] = None,
    prefix: str = "aug"
) -> List[str]:
    """
    Apply multiple augmentations to a video and save each variant.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save augmented videos
        augmentations: List of augmentation names to apply
        prefix: Prefix for output filenames
    
    Returns:
        List of paths to saved videos
    """
    os.makedirs(output_dir, exist_ok=True)
    
    default_augmentations = [
        'brightness_flicker',
        'temporal_noise',
        'random_crop',
        'rotation',
        'color_jitter',
        'motion_blur_temporal'
    ]
    
    if augmentations is None:
        augmentations = default_augmentations
    
    video_name = Path(video_path).stem
    saved_videos = []
    
    aug_functions = {
        'brightness_flicker': video_brightness_flicker,
        'temporal_noise': video_temporal_noise,
        'random_crop': video_random_crop,
        'rotation': video_rotation,
        'color_jitter': video_color_jitter,
        'motion_blur_temporal': video_motion_blur_temporal
    }
    
    for aug_name in augmentations:
        if aug_name not in aug_functions:
            continue
        
        output_path = os.path.join(output_dir, f"{prefix}_{video_name}_{aug_name}.mp4")
        success = aug_functions[aug_name](video_path, output_path)
        
        if success:
            saved_videos.append(output_path)
    
    return saved_videos


def extract_frames(video_path: str, output_dir: str, frame_rate: Optional[int] = None) -> List[str]:
    """
    Extract frames from video for frame-by-frame augmentation.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save frames
        frame_rate: Extract every Nth frame (None = all frames)
    
    Returns:
        List of paths to extracted frames
    """
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    
    frame_paths = []
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_rate is None or frame_count % frame_rate == 0:
            frame_path = os.path.join(output_dir, f"frame_{saved_count:06d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    return frame_paths


def frames_to_video(frame_dir: str, output_path: str, fps: float = 30.0, codec: str = 'mp4v') -> bool:
    """
    Combine frames back into a video.
    
    Args:
        frame_dir: Directory containing frames
        output_path: Path to save output video
        fps: Frames per second
        codec: FourCC codec string
    
    Returns:
        True if successful, False otherwise
    """
    frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith(('.jpg', '.png'))])
    
    if not frame_files:
        return False
    
    first_frame = cv2.imread(os.path.join(frame_dir, frame_files[0]))
    height, width = first_frame.shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        return False
    
    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(frame_dir, frame_file))
        out.write(frame)
    
    out.release()
    return True