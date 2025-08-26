import os
import cv2
import random
import numpy as np
from django.conf import settings

# Augmentation functions (no rotation)
def horizontal_flip(img):
    return cv2.flip(img, 1)

def vertical_flip(img):
    return cv2.flip(img, 0)

def random_crop(img):
    h, w = img.shape[:2]
    ch, cw = int(h*0.8), int(w*0.8)
    if ch >= h or cw >= w:
        return img
    x = random.randint(0, w - cw)
    y = random.randint(0, h - ch)
    return img[y:y+ch, x:x+cw]

def adjust_brightness(img):
    factor = random.uniform(0.5, 1.5)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def adjust_color(img):
    img = img.astype(np.float32) / 255.0
    factor = random.uniform(0.5, 1.5)
    img = np.clip(img * factor, 0, 1.0)
    return (img * 255).astype(np.uint8)

# Main augmentation function
def augment_image(image_path, num_augments=5):
    orig_img = cv2.imread(image_path)
    if orig_img is None:
        raise ValueError(f"Image not found at path: {image_path}")

    augmented_files = []
    augmentation_functions = [
        horizontal_flip,
        vertical_flip,
        random_crop,
        adjust_brightness,
        adjust_color
    ]

    for i in range(num_augments):
        aug_func = random.choice(augmentation_functions)
        aug_img = aug_func(orig_img.copy())

        save_name = f"augmented_{i}_{aug_func.__name__}_{os.path.basename(image_path)}"
        save_path = os.path.join(settings.MEDIA_ROOT, save_name)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        cv2.imwrite(save_path, aug_img)
        augmented_files.append(save_name)

    return augmented_files
