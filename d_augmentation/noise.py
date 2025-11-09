import cv2
import numpy as np
from .utils import clip

def gaussian_noise(image, mean=0, std=10):
    noise = np.random.normal(mean, std, image.shape)
    return clip(image + noise)

def salt_and_pepper(image, amount=0.01):
    output = image.copy()
    num_salt = np.ceil(amount * image.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
    output[coords[0], coords[1]] = 255
    num_pepper = np.ceil(amount * image.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape[:2]]
    output[coords[0], coords[1]] = 0
    return output

def speckle_noise(image):
    noise = np.random.randn(*image.shape)
    return clip(image + image * noise * 0.1)

def gaussian_blur(image, ksize=5):
    return cv2.GaussianBlur(image, (ksize, ksize), 0)

def motion_blur(image, kernel_size=9):
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1)/2), :] = np.ones(kernel_size)
    kernel /= kernel_size
    return cv2.filter2D(image, -1, kernel)

def defocus_blur(image, ksize=9):
    kernel = np.ones((ksize, ksize), np.float32) / (ksize * ksize)
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
    """
    Apply all noise transformations (Gaussian, Salt & Pepper, Speckle, Blur, Motion Blur, Defocus Blur)
    Sequentially or randomly depending on `apply_random`.
    """
    transformed = image.copy()

    # Gaussian Noise
    if not apply_random or np.random.rand() > 0.5:
        transformed = gaussian_noise(transformed, mean, std)

    # Salt & Pepper Noise
    if not apply_random or np.random.rand() > 0.5:
        transformed = salt_and_pepper(transformed, amount)

    # Speckle Noise
    if not apply_random or np.random.rand() > 0.5:
        transformed = speckle_noise(transformed)

    # Gaussian Blur
    if not apply_random or np.random.rand() > 0.5:
        transformed = gaussian_blur(transformed, ksize)

    # Motion Blur
    if not apply_random or np.random.rand() > 0.5:
        transformed = motion_blur(transformed, motion_kernel)

    # Defocus Blur
    if not apply_random or np.random.rand() > 0.5:
        transformed = defocus_blur(transformed, defocus_kernel)

    return clip(transformed)
