from django.contrib import admin
from .models import Product, Government, PromoCode, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'color_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('is_hot_sale','name', 'price', 'main_category', 'sub_category', 'age_group', 'image_count')
    list_filter = ('main_category', 'sub_category', 'age_group')
    search_fields = ('name',)
    inlines = [ProductImageInline]

    def image_count(self, obj):
        return obj.extra_images.count()
    image_count.short_description = 'image_count'

@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'expiration_date')
    search_fields = ('code',)
    list_filter = ('is_active',)
