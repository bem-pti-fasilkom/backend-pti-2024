from django.forms import ModelForm
from cloudinary.forms import CloudinaryFileField
from .models import Image

class PhotoForm(ModelForm):
    image = CloudinaryFileField()

    class Meta:
        model = Image
        fields = ['image', 'owner']