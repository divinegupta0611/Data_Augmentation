# smart_augmentation/geometric.py
import cv2
import numpy as np

def flip(image, mode="horizontal"):
    if mode == "horizontal":
        return cv2.flip(image, 1)
    elif mode == "vertical":
        return cv2.flip(image, 0)
    return image

def rotate(image, angle=15):
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), float(np.random.uniform(-angle, angle)), 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

def translate(image, shift_x=0.1, shift_y=0.1):
    h, w = image.shape[:2]
    # allow positive or negative shift
    tx = w * shift_x * (1 if np.random.rand() > 0.5 else -1)
    ty = h * shift_y * (1 if np.random.rand() > 0.5 else -1)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT101)

def scale(image, scale_range=(0.8, 1.2)):
    scale_factor = float(np.random.uniform(*scale_range))
    h, w = image.shape[:2]
    resized = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    return cv2.resize(resized, (w, h), interpolation=cv2.INTER_LINEAR)

def shear(image, shear_range=0.2):
    h, w = image.shape[:2]
    shear_factor = float(np.random.uniform(-shear_range, shear_range))
    M = np.array([[1, shear_factor, 0], [0, 1, 0]], dtype=np.float32)
    return cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT101)

def crop(image, crop_ratio=0.8, center=False):
    h, w = image.shape[:2]
    new_h, new_w = int(h * crop_ratio), int(w * crop_ratio)
    if new_h <= 0 or new_w <= 0:
        return image
    if center:
        startx = max(0, w // 2 - new_w // 2)
        starty = max(0, h // 2 - new_h // 2)
    else:
        startx = np.random.randint(0, max(1, w - new_w))
        starty = np.random.randint(0, max(1, h - new_h))
    cropped = image[starty:starty+new_h, startx:startx+new_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

def perspective_transform(image, margin=60):
    h, w = image.shape[:2]
    margin = int(min(margin, w//4, h//4))
    pts1 = np.float32([[margin, margin], [w-margin, margin], [margin, h-margin], [w-margin, h-margin]])
    pts2 = np.float32([
        [margin + np.random.randint(-margin, margin), margin + np.random.randint(-margin, margin)],
        [w - margin + np.random.randint(-margin, margin), margin + np.random.randint(-margin, margin)],
        [margin + np.random.randint(-margin, margin), h - margin + np.random.randint(-margin, margin)],
        [w - margin + np.random.randint(-margin, margin), h - margin + np.random.randint(-margin, margin)]
    ])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(image, M, (w, h), borderMode=cv2.BORDER_REFLECT101)

def elastic_deformation(image, alpha=40, sigma=8):
    random_state = np.random.RandomState(None)
    shape = image.shape[:2]
    dx = (random_state.rand(*shape) * 2 - 1).astype(np.float32)
    dy = (random_state.rand(*shape) * 2 - 1).astype(np.float32)
    dx = cv2.GaussianBlur(dx, (17, 17), sigma) * alpha
    dy = cv2.GaussianBlur(dy, (17, 17), sigma) * alpha
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    map_x = (x + dx).astype(np.float32)
    map_y = (y + dy).astype(np.float32)
    return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

def all_geometric(
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
):
    transformed = image.copy()
    if not apply_random or np.random.rand() > 0.5:
        transformed = flip(transformed, flip_mode)
    if not apply_random or np.random.rand() > 0.5:
        transformed = rotate(transformed, rotation_angle)
    if not apply_random or np.random.rand() > 0.5:
        transformed = translate(transformed, shift_x, shift_y)
    if not apply_random or np.random.rand() > 0.5:
        transformed = scale(transformed, scale_range)
    if not apply_random or np.random.rand() > 0.5:
        transformed = shear(transformed, shear_range)
    if not apply_random or np.random.rand() > 0.5:
        transformed = crop(transformed, crop_ratio)
    if not apply_random or np.random.rand() > 0.5:
        transformed = perspective_transform(transformed, perspective_margin)
    if not apply_random or np.random.rand() > 0.5:
        transformed = elastic_deformation(transformed, alpha, sigma)
    return np.clip(transformed)
