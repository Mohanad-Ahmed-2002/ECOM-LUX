from django import forms
from django.core.exceptions import ValidationError
from .models import Government, CustomerOrder, Product,ProductImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys,os,io
from .models import Product, BRAND_CHOICES
from store.constants import BRAND_CHOICES
import paramiko

def upload_image_to_vps(image_file, filename):
    private_key_str = os.environ['PRIVATE_KEY']  # من Render Environment
    pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key_str))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("134.209.243.59", username="root", pkey=pkey)

    sftp = ssh.open_sftp()
    remote_path = f"/var/www/media/products/{filename}"
    sftp.putfo(image_file.file, remote_path)

    sftp.close()
    ssh.close()

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
    
    image = forms.ImageField(required=False)

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

            upload_image_to_vps(image.file, image.name)

            return image.name

        return None

class ProductImageForm(forms.ModelForm):

    image = forms.ImageField(required=False)


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

            upload_image_to_vps(image.file, image.name)

            return image.name


        return None
