# smart_augmentation/noise.py
import cv2
import numpy as np

def gaussian_noise(image, mean=0, std=10):
    noise = np.random.normal(mean, std, image.shape).astype(np.float32)
    return np.clip(image.astype(np.float32) + noise)

def salt_and_pepper(image, amount=0.01):
    output = image.copy().astype(np.uint8)
    h, w = image.shape[:2]
    num_salt = int(np.ceil(amount * h * w * 0.5))
    # coordinates
    ys = np.random.randint(0, h, num_salt)
    xs = np.random.randint(0, w, num_salt)
    output[ys, xs] = 255
    num_pepper = int(np.ceil(amount * h * w * 0.5))
    ys = np.random.randint(0, h, num_pepper)
    xs = np.random.randint(0, w, num_pepper)
    output[ys, xs] = 0
    return output

def speckle_noise(image):
    noise = np.random.randn(*image.shape).astype(np.float32)
    return np.clip(image.astype(np.float32) + image.astype(np.float32) * noise * 0.1)

def gaussian_blur(image, ksize=5):
    k = max(1, int(ksize))
    if k % 2 == 0:
        k += 1
    return cv2.GaussianBlur(image, (k, k), 0)

def motion_blur(image, kernel_size=9):
    kernel_size = max(3, int(kernel_size))
    kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    kernel[int((kernel_size - 1)/2), :] = np.ones(kernel_size, dtype=np.float32)
    kernel /= kernel_size
    return cv2.filter2D(image, -1, kernel)

def defocus_blur(image, ksize=9):
    k = max(1, int(ksize))
    kernel = np.ones((k, k), np.float32) / (k * k)
    return cv2.filter2D(image, -1, kernel)

def all_noise(
    image,
    apply_random=True,
    mean=0,
    std=10,
    amount=0.01,
    ksize=5,
    motion_kernel=9,
    defocus_kernel=9
):
    transformed = image.copy()
    if not apply_random or np.random.rand() > 0.5:
        transformed = gaussian_noise(transformed, mean, std)
    if not apply_random or np.random.rand() > 0.5:
        transformed = salt_and_pepper(transformed, amount)
    if not apply_random or np.random.rand() > 0.5:
        transformed = speckle_noise(transformed)
    if not apply_random or np.random.rand() > 0.5:
        transformed = gaussian_blur(transformed, ksize)
    if not apply_random or np.random.rand() > 0.5:
        transformed = motion_blur(transformed, motion_kernel)
    if not apply_random or np.random.rand() > 0.5:
        transformed = defocus_blur(transformed, defocus_kernel)
    return np.clip(transformed)
