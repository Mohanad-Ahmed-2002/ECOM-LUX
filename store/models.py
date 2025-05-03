from django.db import models
from django import forms
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils import timezone
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


# Create your models here.


class Product(models.Model):

    MAIN_CATEGORY_CHOICES = [
        ('SUNGLASSES', 'SUNGLASSES'),
        ('OPTICAL', 'OPTICAL'),
        ('JEANSCLUB', 'JEANSCLUB'),
        ('CLIP-ON', 'CLIP-ON'),
    ]

    SUB_CATEGORY_CHOICES = [
        ('SUNGLASSES', 'SUNGLASSES'),
        ('OPTICAL', 'OPTICAL'),
        
    ]

    AGE_GROUP_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Kids', 'Kids'),
    ]

    name = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)  # ✅ السعر بعد الخصم
    main_category = models.CharField(max_length=20, choices=MAIN_CATEGORY_CHOICES)  # ✨ الفئة الأساسية
    sub_category = models.CharField(max_length=20, choices=SUB_CATEGORY_CHOICES ,blank=True, null=True)
    image = CloudinaryField('image', folder='LUXFLEX/')
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, default='Men')
    description = models.TextField(blank=True)  # 👈 شرح المنتج
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', folder='LUXFLEX/')
    color_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"

class CartItem(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)  # بدل user    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_color = models.URLField(blank=True, null=True) 

    def get_total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class Government(models.Model):
    name = models.CharField(max_length=100)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}"
    
class CustomerOrder(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'قيد الانتظار'),
        ('PROCESSING', 'تم التحضير'),
        ('SHIPPED', 'تم الشحن'),
        ('DELIVERED', 'تم التوصيل'),
        ('CANCELLED', 'تم الإلغاء'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('instapay', 'Instapay'),
        ('visa', 'Visa / MasterCard'),
        ('Cash', 'Cash on Delivery'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=6, decimal_places=2, default=70)
    order_date = models.DateTimeField(auto_now_add=True)
    government = models.ForeignKey(Government, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')  # 👈 الحقل الجديد
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')


    def get_order_items(self):
        return self.order_items.all()  # جلب كل العناصر الخاصة بالطلب

    def save(self, *args, **kwargs):
        if self.government:
            self.shipping_fee = self.government.shipping_fee  # تحديد رسوم الشحن تلقائيًا
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.name}-{self.order_date}"
    
class OrderForm(forms.ModelForm):

    government = forms.ModelChoiceField(
        queryset=Government.objects.all(),
        empty_label="Select your governorate",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model=CustomerOrder
        fields=['name','email','address','phone','government']

class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_color = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.is_active and self.expiration_date > timezone.now()


    def __str__(self):
        return self.code
    
class WishlistItem(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist - {self.product.name}"
