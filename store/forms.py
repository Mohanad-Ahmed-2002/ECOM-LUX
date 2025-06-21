from django import forms
from django.core.exceptions import ValidationError
from .models import Government, CustomerOrder, Product,ProductImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys
from .models import Product, BRAND_CHOICES
from store.constants import BRAND_CHOICES

class OrderForm(forms.ModelForm):
    government = forms.ModelChoiceField(
        queryset=Government.objects.all(),
        empty_label="Select your governorate",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomerOrder
        fields = ['name', 'email', 'address', 'phone', 'government']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'brand': forms.Select(choices=BRAND_CHOICES)  # استخدم القيم الأصلية
        }


    def clean_image(self):
        image = self.cleaned_data.get('image')
        max_size = 4 * 1024 * 1024  # 4MB

        if image and isinstance(image, InMemoryUploadedFile):
            if image.size > max_size:
                raise ValidationError("حجم الصورة لا يجب أن يتجاوز 4 ميجا.")

            # ضغط الصورة وتصغيرها
            img = Image.open(image)
            output = BytesIO()
            img = img.convert('RGB')

            if img.height > 1000 or img.width > 1000:
                img.thumbnail((1000, 1000))  # تصغير الأبعاد

            img.save(output, format='JPEG', quality=70)  # ضغط الجودة
            output.seek(0)

            image = InMemoryUploadedFile(
                output, 'ImageField', image.name, 'image/jpeg', sys.getsizeof(output), None
            )

        return image

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'color_name']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        max_size = 4 * 1024 * 1024  # 4MB

        if image and isinstance(image, InMemoryUploadedFile):
            if image.size > max_size:
                raise ValidationError("حجم الصورة لا يجب أن يتجاوز 4 ميجا.")

            img = Image.open(image)
            output = BytesIO()
            img = img.convert('RGB')

            if img.height > 1000 or img.width > 1000:
                img.thumbnail((1000, 1000))

            img.save(output, format='JPEG', quality=70)
            output.seek(0)

            image = InMemoryUploadedFile(
                output, 'ImageField', image.name, 'image/jpeg', sys.getsizeof(output), None
            )

        return image
