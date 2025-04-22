from django.contrib import admin
from .models import Product, CustomerOrder, Government,PromoCode
from django.core.exceptions import ObjectDoesNotExist

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category','gender']
    list_filter = ['category']

@admin.register(CustomerOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'address', 'phone', 'total_price', 'order_date','government']
    search_fields = ['name', 'phone']
    list_filter = ['order_date']


@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'is_active', 'expiration_date']
    search_fields = ['code']