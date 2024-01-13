from django.urls import path
from .views import convert_image, success_page, upload_image, get_converted_image

urlpatterns = [
    path('upload/', upload_image, name='upload_image'),
    path('convert/', convert_image, name='convert_image'),
    path('success/', success_page, name='success_page'),
    path('converted/<str:identifier>/', get_converted_image, name='get_converted_image')
]
