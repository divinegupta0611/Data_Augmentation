# smart_augmentation/color.py
import cv2
import numpy as np

def adjust_brightness(image, factor=0.2):
    factor = 1 + np.random.uniform(-factor, factor)
    img = image.astype(np.float32) * factor
    return np.clip(img)

def adjust_contrast(image, factor=0.3):
    factor = 1 + np.random.uniform(-factor, factor)
    img = image.astype(np.float32)
    mean = np.mean(img)
    return np.clip((img - mean) * factor + mean)

def adjust_saturation(image, factor=0.3):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 1 + np.random.uniform(-factor, factor)
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    return np.clip(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))

def shift_hue(image, shift=10):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int32)
    hsv[..., 0] = (hsv[..., 0] + np.random.randint(-shift, shift)) % 180
    hsv[..., 0] = np.clip(hsv[..., 0], 0, 179)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def gamma_correction(image, gamma_range=(0.8, 1.2)):
    gamma = float(np.random.uniform(*gamma_range))
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
    return np.clip(alpha * gray + (1 - alpha) * image)

def solarize(image, threshold=128):
    arr = image.astype(np.uint8)
    out = np.where(arr < threshold, arr, 255 - arr)
    return out.astype(np.uint8)

def posterize(image, bits=4):
    shift = 8 - bits
    arr = image.astype(np.uint8)
    return ((arr >> shift) << shift).astype(np.uint8)

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
    transformed = image.copy()
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_brightness(transformed, brightness_factor)
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_contrast(transformed, contrast_factor)
    if not apply_random or np.random.rand() > 0.5:
        transformed = adjust_saturation(transformed, saturation_factor)
    if not apply_random or np.random.rand() > 0.5:
        transformed = shift_hue(transformed, hue_shift)
    if not apply_random or np.random.rand() > 0.5:
        transformed = gamma_correction(transformed, gamma_range)
    if not apply_random or np.random.rand() > 0.5:
        transformed = color_jitter(transformed)
    if not apply_random or np.random.rand() > 0.5:
        transformed = grayscale(transformed, grayscale_alpha)
    if not apply_random or np.random.rand() > 0.5:
        transformed = solarize(transformed, solarize_threshold)
    if not apply_random or np.random.rand() > 0.5:
        transformed = posterize(transformed, posterize_bits)
    return np.clip(transformed)
