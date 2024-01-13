from django import forms
from .models import StoredImage, FrontendEvent


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = StoredImage
        fields = ['image']


class ImageConversionForm(forms.Form):
    identifier = forms.CharField(max_length=50)
    width = forms.IntegerField(required=False)
    height = forms.IntegerField(required=False)
    target_file_size = forms.IntegerField(required=False)


class FrontendEventForm(forms.ModelForm):
    class Meta:
        model = FrontendEvent
        fields = ['event_type']
