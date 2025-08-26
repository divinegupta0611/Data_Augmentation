# from django.urls import path
# from .views import hello  # import your view

# urlpatterns = [
#     path('hello/', hello),  # this will be accessible at /api/hello/
# ]
from django.urls import path
from .views import upload

urlpatterns = [
    path('upload/', upload),
]
