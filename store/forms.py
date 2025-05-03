from django import forms
from django.forms import modelformset_factory
from .models import Product, ProductImage, Government

class GovernmentForm(forms.ModelForm):
    class Meta:
        model = Government
        fields = ['name', 'shipping_fee']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'main_category', 'sub_category', 'age_group', 'price', 'discount_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'main_category': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'sub_category': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'age_group': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'color_name']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full border border-gray-300 rounded px-3 py-2'}),
            'color_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2',
                'placeholder': 'e.g. Black, Blue'
            }),
        }

ProductImageFormSet = modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=5,
    can_delete=True
)