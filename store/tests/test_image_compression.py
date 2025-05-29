import pytest
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from store.forms import ProductForm
import sys

def create_test_image(size=(3000, 3000), format='JPEG', quality=95):
    img = Image.new("RGB", size, color=(255, 0, 0))
    output = BytesIO()
    img.save(output, format=format, quality=quality)
    output.seek(0)
    return InMemoryUploadedFile(
        output, 'ImageField', 'test.jpg', 'image/jpeg', sys.getsizeof(output), None
    )


@pytest.mark.django_db
def test_product_form_image_compression():
    image_file = create_test_image()

    form_data = {
        'name': 'Test Product',
        'price': 100,
        'main_category': 'SUNGLASSES',
        'age_group': 'Men'
    }

    form = ProductForm(data=form_data, files={'image': image_file})

    assert form.is_valid(), form.errors

    compressed_image = form.cleaned_data['image']
    assert compressed_image.size < 1024 * 1024 * 2, "الصورة المضغوطة لازم تكون أقل من 2MB"



