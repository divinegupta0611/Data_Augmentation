# smart_augmentation/occlusion.py
import cv2
import numpy as np

def cutout(image, mask_size=50):
    out = image.copy()
    h, w = out.shape[:2]
    mask_size = min(mask_size, h - 1, w - 1)
    if mask_size <= 0:
        return out
    x = np.random.randint(0, w - mask_size + 1)
    y = np.random.randint(0, h - mask_size + 1)
    out[y:y+mask_size, x:x+mask_size] = 0
    return out

def hide_and_seek(image, grid_size=4, hide_prob=0.25):
    out = image.copy()
    h, w = out.shape[:2]
    cell_h, cell_w = max(1, h // grid_size), max(1, w // grid_size)
    for i in range(grid_size):
        for j in range(grid_size):
            if np.random.rand() < hide_prob:
                y1, y2 = i*cell_h, min((i+1)*cell_h, h)
                x1, x2 = j*cell_w, min((j+1)*cell_w, w)
                out[y1:y2, x1:x2] = 0
    return out

def gridmask(image, grid_size=50, ratio=0.5):
    out = image.copy()
    h, w = out.shape[:2]
    mask = np.ones((h, w), dtype=np.uint8)
    for i in range(0, h, grid_size):
        for j in range(0, w, grid_size):
            if np.random.rand() < ratio:
                i2 = min(h, i + grid_size//2)
                j2 = min(w, j + grid_size//2)
                mask[i:i2, j:j2] = 0
    if out.ndim == 3:
        return np.clip(out * mask[..., None])
    return np.clip(out * mask)

def mixup(image1, image2, alpha=0.4):
    if image2 is None:
        return image1
    lam = np.random.beta(alpha, alpha)
    return np.clip(lam * image1 + (1 - lam) * image2)

def cutmix(image1, image2):
    if image2 is None:
        return image1
    h, w = image1.shape[:2]
    cut_w, cut_h = max(1, w // 4), max(1, h // 4)
    x = np.random.randint(0, w - cut_w + 1)
    y = np.random.randint(0, h - cut_h + 1)
    out = image1.copy()
    out[y:y+cut_h, x:x+cut_w] = image2[y:y+cut_h, x:x+cut_w]
    return out

def fmix(image1, image2, alpha=1.0):
    if image2 is None:
        return image1
    # simplified fmix: random low-frequency mask
    mask = np.random.rand(*image1.shape[:2]).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (15, 15), 5)
    mask = (mask - mask.min()) / max(1e-8, (mask.max() - mask.min()))
    mask = (mask > 0.5).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (15, 15), 5)
    mask = np.expand_dims(mask, axis=-1)
    return np.clip(mask * image1 + (1 - mask) * image2)

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
    transformed = image1.copy()
    if not apply_random or np.random.rand() > 0.5:
        transformed = cutout(transformed, mask_size)
    if not apply_random or np.random.rand() > 0.5:
        transformed = hide_and_seek(transformed, grid_size, hide_prob)
    if not apply_random or np.random.rand() > 0.5:
        transformed = gridmask(transformed, gridmask_size, gridmask_ratio)
    if image2 is not None:
        if not apply_random or np.random.rand() > 0.5:
            transformed = mixup(transformed, image2, alpha)
        if not apply_random or np.random.rand() > 0.5:
            transformed = cutmix(transformed, image2)
        if not apply_random or np.random.rand() > 0.5:
            transformed = fmix(transformed, image2)
    return np.clip(transformed)
