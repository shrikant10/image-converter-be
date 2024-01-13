import json
import os
import uuid

from django.http import FileResponse, JsonResponse, HttpResponseNotFound

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .forms import ImageUploadForm, ImageConversionForm, FrontendEventForm
from PIL import Image as PILImage

from .models import StoredImage


def success_page(request):
    return render(request, 'image_processing/success_page.html')


@require_GET
def health_check(request):
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        print('request: ', request)
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():

            # Generate a unique identifier (filename) for the stored image
            unique_identifier = str(uuid.uuid4())
            # Check if the identifier is already in use, generate a new one if needed
            while StoredImage.objects.filter(identifier=unique_identifier).exists():
                unique_identifier = str(uuid.uuid4())

            # Save the uploaded image to the specified path
            image = form.save(commit=False)
            image.image.name = f'{unique_identifier}.jpg'
            image.identifier = unique_identifier
            image.path = f'media/uploads/{unique_identifier}.jpg'
            image.save()

            # Return the unique identifier as the HTTP response
            response_data = {
                'status': 'success',
                'message': 'Image uploaded and stored successfully',
                'identifier': unique_identifier,
            }
            response = JsonResponse(response_data)
            response["Access-Control-Allow-Origin"] = "*"  # Replace with your frontend domain
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            return response

    response_data = {
        'status': 'error',
        'message': 'Invalid form data',
    }
    return JsonResponse(response_data, status=400)


@csrf_exempt
def convert_image(request):
    if request.method == 'POST' or request.method == 'OPTIONS':

        try:
            data = json.loads(request.body)
            data['target_file_size'] = data.get('target_file_size', 0)
            form = ImageConversionForm(data)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            width = form.cleaned_data.get('width')
            height = form.cleaned_data.get('height')
            target_file_size = form.cleaned_data.get('target_file_size') # File size in KB

            # Fetch the stored image details from the database
            stored_image = StoredImage.objects.get(identifier=identifier)

            # Open the stored image using Pillow
            img = PILImage.open(stored_image.path)

            # Perform image processing (resizing) based on configuration parameters
            if width and height:
                resized_img = img.resize((width, height))
            else:
                # If width or height is not provided, use original dimensions
                resized_img = img

            # Save the processed image
            converted_folder_path = os.path.join('media', 'converted')
            if not os.path.exists(converted_folder_path):
                os.makedirs(converted_folder_path)

            converted_identifier_path = f'media/converted/{identifier}.jpg'
            print('------ ', target_file_size)
            if target_file_size > 0:
                quality = 95

                # Compress the image iteratively until the file size is below the target
                print('------ ', quality, os.path.getsize(converted_identifier_path), target_file_size * 1024)
                while os.path.getsize(converted_identifier_path) > target_file_size * 1024 and quality >= 10:
                    resized_img.save(converted_identifier_path, 'JPEG', quality=quality)
                    quality -= 5
            else:
                # If target_file_size is not provided, save without compression
                resized_img.save(converted_identifier_path)

            response_data = {
                'status': 'success',
                'message': 'Image converted and stored successfully',
                'identifier': identifier,
            }
            response = JsonResponse(response_data)
            # Optionally, you can set a custom filename for the downloaded image
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            return response

    # If the form is not valid, return an error response
    response_data = {
        'status': 'error',
        'message': 'Invalid form data',
    }
    response = JsonResponse(response_data, status=400)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@csrf_exempt
def log_frontend_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = FrontendEventForm(data)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Event logged successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
@require_GET
def get_converted_image(request, identifier):
    converted_identifier_path = f'media/converted/{identifier}.jpg'  # Adjust the path as needed

    if os.path.isfile(converted_identifier_path):
        response = FileResponse(open(converted_identifier_path, 'rb'), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(converted_identifier_path)}'
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    else:
        return HttpResponseNotFound("Converted image not found")
