from django.contrib import admin
from .models import Product, Government, PromoCode, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # عدد الصور المفتوحة جاهزة
    fields = ('image', 'color_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'main_category', 'sub_category', 'age_group')
    list_filter = ('main_category', 'sub_category', 'age_group')
    search_fields = ('name',)
    inlines = [ProductImageInline]

@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'expiration_date')
    search_fields = ('code',)
