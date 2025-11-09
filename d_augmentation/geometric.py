import cv2
import numpy as np
from .utils import clip

def flip(image, mode="horizontal"):
    if mode == "horizontal":
        return cv2.flip(image, 1)
    elif mode == "vertical":
        return cv2.flip(image, 0)
    return image

def rotate(image, angle=15):
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), np.random.uniform(-angle, angle), 1)
    return cv2.warpAffine(image, M, (w, h))

def translate(image, shift_x=0.1, shift_y=0.1):
    h, w = image.shape[:2]
    tx, ty = w * shift_x, h * shift_y
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(image, M, (w, h))

def scale(image, scale_range=(0.8, 1.2)):
    scale_factor = np.random.uniform(*scale_range)
    h, w = image.shape[:2]
    resized = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    return cv2.resize(resized, (w, h))

def shear(image, shear_range=0.2):
    h, w = image.shape[:2]
    shear_factor = np.random.uniform(-shear_range, shear_range)
    M = np.array([[1, shear_factor, 0], [0, 1, 0]], dtype=np.float32)
    return cv2.warpAffine(image, M, (w, h))

def crop(image, crop_ratio=0.8, center=False):
    h, w = image.shape[:2]
    new_h, new_w = int(h * crop_ratio), int(w * crop_ratio)
    if center:
        startx = w // 2 - new_w // 2
        starty = h // 2 - new_h // 2
    else:
        startx = np.random.randint(0, w - new_w)
        starty = np.random.randint(0, h - new_h)
    cropped = image[starty:starty+new_h, startx:startx+new_w]
    return cv2.resize(cropped, (w, h))

def perspective_transform(image, margin=60):
    h, w = image.shape[:2]
    pts1 = np.float32([[margin, margin], [w-margin, margin], [margin, h-margin], [w-margin, h-margin]])
    pts2 = np.float32([
        [margin + np.random.randint(-margin, margin), margin + np.random.randint(-margin, margin)],
        [w - margin + np.random.randint(-margin, margin), margin + np.random.randint(-margin, margin)],
        [margin + np.random.randint(-margin, margin), h - margin + np.random.randint(-margin, margin)],
        [w - margin + np.random.randint(-margin, margin), h - margin + np.random.randint(-margin, margin)]
    ])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(image, M, (w, h))

def elastic_deformation(image, alpha=40, sigma=8):
    random_state = np.random.RandomState(None)
    shape = image.shape[:2]

    dx = cv2.GaussianBlur((random_state.rand(*shape) * 2 - 1), (17, 17), sigma) * alpha
    dy = cv2.GaussianBlur((random_state.rand(*shape) * 2 - 1), (17, 17), sigma) * alpha

    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    map_x = (x + dx).astype(np.float32)
    map_y = (y + dy).astype(np.float32)
    return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR)

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
    """
    Apply a sequence of geometric transformations to an image.
    If `apply_random=True`, each transformation is applied randomly.
    """
    transformed = image.copy()

    # Flip
    if not apply_random or np.random.rand() > 0.5:
        transformed = flip(transformed, flip_mode)

    # Rotation
    if not apply_random or np.random.rand() > 0.5:
        transformed = rotate(transformed, rotation_angle)

    # Translation
    if not apply_random or np.random.rand() > 0.5:
        transformed = translate(transformed, shift_x, shift_y)

    # Scaling
    if not apply_random or np.random.rand() > 0.5:
        transformed = scale(transformed, scale_range)

    # Shearing
    if not apply_random or np.random.rand() > 0.5:
        transformed = shear(transformed, shear_range)

    # Cropping
    if not apply_random or np.random.rand() > 0.5:
        transformed = crop(transformed, crop_ratio)

    # Perspective
    if not apply_random or np.random.rand() > 0.5:
        transformed = perspective_transform(transformed, perspective_margin)

    # Elastic deformation
    if not apply_random or np.random.rand() > 0.5:
        transformed = elastic_deformation(transformed, alpha, sigma)

    return transformed
