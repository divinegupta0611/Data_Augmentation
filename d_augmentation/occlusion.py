import cv2
import numpy as np
from .utils import clip

def cutout(image, mask_size=50):
    h, w = image.shape[:2]
    x = np.random.randint(0, w - mask_size)
    y = np.random.randint(0, h - mask_size)
    image[y:y+mask_size, x:x+mask_size] = 0
    return image

def hide_and_seek(image, grid_size=4, hide_prob=0.25):
    h, w = image.shape[:2]
    cell_h, cell_w = h // grid_size, w // grid_size
    for i in range(grid_size):
        for j in range(grid_size):
            if np.random.rand() < hide_prob:
                y1, y2 = i*cell_h, (i+1)*cell_h
                x1, x2 = j*cell_w, (j+1)*cell_w
                image[y1:y2, x1:x2] = 0
    return image

def gridmask(image, grid_size=50, ratio=0.5):
    h, w = image.shape[:2]
    mask = np.ones((h, w), np.uint8)
    for i in range(0, h, grid_size):
        for j in range(0, w, grid_size):
            if np.random.rand() < ratio:
                mask[i:i+grid_size//2, j:j+grid_size//2] = 0
    return clip(image * mask[..., None])

def mixup(image1, image2, alpha=0.4):
    lam = np.random.beta(alpha, alpha)
    return clip(lam * image1 + (1 - lam) * image2)

def cutmix(image1, image2):
    h, w = image1.shape[:2]
    cut_w, cut_h = w // 4, h // 4
    x = np.random.randint(0, w - cut_w)
    y = np.random.randint(0, h - cut_h)
    image1[y:y+cut_h, x:x+cut_w] = image2[y:y+cut_h, x:x+cut_w]
    return image1

def fmix(image1, image2, alpha=1.0):
    mask = np.fft.ifft2(np.fft.fft2(np.random.rand(*image1.shape[:2]))).real
    mask = (mask - mask.min()) / (mask.max() - mask.min())
    mask = (mask > 0.5).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (15, 15), 5)
    mask = np.expand_dims(mask, axis=-1)
    return clip(mask * image1 + (1 - mask) * image2)

def all_occlusion(
    image1,
    image2=None,
    apply_random=True,
    mask_size=50,
    grid_size=4,
    hide_prob=0.25,
    gridmask_size=50,
    gridmask_ratio=0.5,
    alpha=0.4
):
    """
    Apply all occlusion transformations (Cutout, Hide-and-Seek, GridMask, Mixup, CutMix, FMix)
    Sequentially or randomly depending on `apply_random`.
    If using mixup/cutmix/fmix, provide a second image (image2).
    """
    transformed = image1.copy()

    # Cutout
    if not apply_random or np.random.rand() > 0.5:
        transformed = cutout(transformed, mask_size)

    # Hide and Seek
    if not apply_random or np.random.rand() > 0.5:
        transformed = hide_and_seek(transformed, grid_size, hide_prob)

    # GridMask
    if not apply_random or np.random.rand() > 0.5:
        transformed = gridmask(transformed, gridmask_size, gridmask_ratio)

    # For these, we need another image
    if image2 is not None:
        # Mixup
        if not apply_random or np.random.rand() > 0.5:
            transformed = mixup(transformed, image2, alpha)

        # CutMix
        if not apply_random or np.random.rand() > 0.5:
            transformed = cutmix(transformed, image2)

        # FMix
        if not apply_random or np.random.rand() > 0.5:
            transformed = fmix(transformed, image2)

    return clip(transformed)
