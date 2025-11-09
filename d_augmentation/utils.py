import cv2
import numpy as np

def show(image, title="Image"):
    """Display image using OpenCV (for quick testing)"""
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def clip(image):
    """Clip pixel values to [0, 255] and convert to uint8"""
    return np.clip(image, 0, 255).astype(np.uint8)
