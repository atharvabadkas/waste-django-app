from django import forms
from .models import ImageClassificationResult, ImageData

class ImageDataForm(forms.ModelForm):
    class Meta:
        model = ImageData
        fields = ['thumbnailLink', 'item_weight', 'time_date', 'camera_flag', 'mcu_flag' ]
