from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        # Save uploaded file
        file_path = default_storage.save(f'media/{image.name}', ContentFile(image.read()))
        full_path = os.path.join(default_storage.location, file_path)

        # For now, just return the filename
        return JsonResponse({
            'message': 'Image uploaded successfully!',
            'augmented': [image.name]  # React can show this
        })

    return JsonResponse({'error': 'No image uploaded'}, status=400)

def hello(request):
    return JsonResponse({"message": "Hello from Django!"})