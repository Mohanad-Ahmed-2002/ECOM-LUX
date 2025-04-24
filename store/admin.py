from django.contrib import admin
from .models import Product, Government, PromoCode

# ---------- Product Admin ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'gender']
    list_filter = ['category']

# ---------- Government Admin ----------
@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')

# ---------- Promo Code Admin ----------
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'is_active', 'expiration_date']
    search_fields = ['code']
