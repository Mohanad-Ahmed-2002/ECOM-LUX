from django import forms
from django.core.exceptions import ValidationError
from .models import Government, CustomerOrder, Product
from django.core.files.uploadedfile import InMemoryUploadedFile


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
    image = forms.ImageField()  # استخدم ImageField بدلاً من CloudinaryField

    class Meta:
        model = Product
        fields = ['name', 'price', 'discount_price', 'main_category',
                'sub_category', 'image', 'age_group', 'description', 'is_hot_sale']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        max_size = 4 * 1024 * 1024  # 4MB

        # فقط تحقق من الحجم إذا كانت الصورة مرفوعة الآن (ملف جديد)
        if image and isinstance(image, InMemoryUploadedFile):
            if image.size > max_size:
                raise ValidationError("حجم الصورة لا يجب أن يتجاوز 4 ميجا.")
        return image
