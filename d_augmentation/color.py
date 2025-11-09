import cv2
import numpy as np
from .utils import clip

def adjust_brightness(image, factor=0.2):
    factor = 1 + np.random.uniform(-factor, factor)
    return clip(image * factor)

def adjust_contrast(image, factor=0.3):
    factor = 1 + np.random.uniform(-factor, factor)
    mean = np.mean(image)
    return clip((image - mean) * factor + mean)

def adjust_saturation(image, factor=0.3):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 1 + np.random.uniform(-factor, factor)
    return clip(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))

def shift_hue(image, shift=10):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[..., 0] = (hsv[..., 0].astype(int) + np.random.randint(-shift, shift)) % 180
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def gamma_correction(image, gamma_range=(0.8, 1.2)):
    gamma = np.random.uniform(*gamma_range)
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

def color_jitter(image):
    image = adjust_brightness(image)
    image = adjust_contrast(image)
    image = adjust_saturation(image)
    image = shift_hue(image)
    return image

def grayscale(image, alpha=0.5):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return clip(alpha * gray + (1 - alpha) * image)

def solarize(image, threshold=128):
    return np.where(image < threshold, image, 255 - image).astype(np.uint8)

def posterize(image, bits=4):
    shift = 8 - bits
    return ((image >> shift) << shift).astype(np.uint8)

def all_color(
    image,
    apply_random=True,
    brightness_factor=0.2,
    contrast_factor=0.3,
    saturation_factor=0.3,
    hue_shift=10,
    gamma_range=(0.8, 1.2),
    grayscale_alpha=0.5,
    solarize_threshold=128,
    posterize_bits=4
):
    """
    Apply all color transformations (brightness, contrast, saturation, hue, gamma correction,
    grayscale, solarize, posterize) either sequentially or randomly.
    """
    transformed = image.copy()

    # Brightness
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_brightness(transformed, brightness_factor)

    # Contrast
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_contrast(transformed, contrast_factor)

    # Saturation
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_saturation(transformed, saturation_factor)

    # Hue Shift
    if not apply_random or np.random.rand() > 0.5:
        transformed = shift_hue(transformed, hue_shift)

    # Gamma Correction
    if not apply_random or np.random.rand() > 0.5:
        transformed = gamma_correction(transformed, gamma_range)

    # Color Jitter (combination of above)
    if not apply_random or np.random.rand() > 0.5:
        transformed = color_jitter(transformed)

    # Grayscale Blend
    if not apply_random or np.random.rand() > 0.5:
        transformed = grayscale(transformed, grayscale_alpha)

    # Solarize
    if not apply_random or np.random.rand() > 0.5:
        transformed = solarize(transformed, solarize_threshold)

    # Posterize
    if not apply_random or np.random.rand() > 0.5:
        transformed = posterize(transformed, posterize_bits)

    return clip(transformed)
