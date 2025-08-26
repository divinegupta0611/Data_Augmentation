from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
import os
import cv2
import numpy as np
import random

# -------------------------
# Augmentation functions
# -------------------------

def horizontal_flip(image):
    return cv2.flip(image, 1)

def vertical_flip(image):
    return cv2.flip(image, 0)

def flip_both(image):
    return cv2.flip(image, -1)

def random_crop(image, crop_size=(100,100)):
    h, w = image.shape[:2]
    ch, cw = crop_size
    if ch > h or cw > w:
        return image
    x = random.randint(0, w - cw)
    y = random.randint(0, h - ch)
    return image[y:y+ch, x:x+cw]

def adjust_brightness(image, factor=None):
    if factor is None:
        factor = random.uniform(0.7,1.5)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def add_gaussian_noise(image, mean=0, sigma=25):
    gauss = np.random.normal(mean, sigma, image.shape).astype('uint8')
    return cv2.add(image, gauss)

def gaussian_blur(image, ksize=(5,5)):
    return cv2.GaussianBlur(image, ksize, 0)

def scale_image(image, scale=None):
    if scale is None:
        scale = random.uniform(0.8,1.5)
    h, w = image.shape[:2]
    return cv2.resize(image, (int(w*scale), int(h*scale)))

def shear_image(image, shear_factor=None):
    if shear_factor is None:
        shear_factor = random.uniform(-0.3,0.3)
    h, w = image.shape[:2]
    M = np.array([[1, shear_factor, 0],
                  [0, 1, 0]], dtype=float)
    return cv2.warpAffine(image, M, (w, h))

def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# -------------------------
# Main augmentation
# -------------------------

def augment_image(image_path):
    augmented_files = []
    base_name = os.path.basename(image_path)
    img = cv2.imread(image_path)

    # List of augmentations
    augmentations = [
        ('hflip', horizontal_flip),
        ('vflip', vertical_flip),
        ('flip_both', flip_both),
        ('crop', lambda x: random_crop(x, crop_size=(min(100,x.shape[0]), min(100,x.shape[1])))),
        ('brightness', adjust_brightness),
        ('gaussian_noise', add_gaussian_noise),
        ('gaussian_blur', gaussian_blur),
        ('scale', scale_image),
        ('shear', shear_image),
        ('grayscale', to_grayscale)
    ]

    for prefix, func in augmentations:
        aug = func(img)
        save_name = f"{prefix}_{base_name}"
        save_path = os.path.join(settings.MEDIA_ROOT, save_name)

        # Convert grayscale to BGR to save properly
        if len(aug.shape) == 2:
            aug = cv2.cvtColor(aug, cv2.COLOR_GRAY2BGR)

        cv2.imwrite(save_path, aug)
        augmented_files.append(save_name)

    return augmented_files

# -------------------------
# API view
# -------------------------

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)

    image_file = request.FILES['image']

    # Save original uploaded file
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    save_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
    with open(save_path, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    # Run augmentations
    augmented_files = augment_image(save_path)

    # Return URLs for frontend
    augmented_urls = [f"{settings.MEDIA_URL}{name}" for name in augmented_files]

    return Response({
        "message": "Image uploaded and augmented successfully!",
        "augmented": augmented_urls
    })

# augmentation/views.py
from django.http import FileResponse, JsonResponse
import os

def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return JsonResponse({'error': 'File not found'}, status=404)
