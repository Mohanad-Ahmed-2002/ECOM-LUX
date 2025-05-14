from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Prefetch

from .filters import filter_products

from .models import (
    Product, CartItem, CustomerOrder, Government, OrderItem,
    PromoCode, WishlistItem, ProductImage
)
from .forms import OrderForm
from .services import order_service, cart_service 

# ============================== صفحات عامة ==============================

@cache_page(60 * 15)  # 15 دقيقة
def home(request):
    return render(request, 'myapp/home.html')

@cache_page(60 * 15)
def about(request):
    return render(request, 'myapp/about.html')


# ============================== المنتجات ==============================

def products_by_main_category(request, main_category):
    main_category = main_category.upper()

    price_filter = request.GET.get('price_filter')
    sort_by = request.GET.get('sort_by')

    products = filter_products(
        price_filter=price_filter,
        category_filter=None,
        sort_by=sort_by
    ).filter(main_category=main_category)

    products = products.only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category,
        'price_filter': price_filter,
        'sort_by': sort_by,
    })

def products_by_main_and_sub_category(request, main_category, sub_category):
    main_category = main_category.upper()
    sub_category = sub_category.upper()

    price_filter = request.GET.get('price_filter')
    sort_by = request.GET.get('sort_by')

    products = filter_products(
        price_filter=price_filter,
        category_filter=sub_category,
        sort_by=sort_by
    ).filter(main_category=main_category)

    products = products.only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category,
        'sub_category': sub_category,
        'price_filter': price_filter,
        'sort_by': sort_by,
    })

def products_by_main_sub_and_age(request, main_category, sub_category, age_group):
    main_category = main_category.upper()
    sub_category = sub_category.upper()
    age_group = age_group.capitalize()

    price_filter = request.GET.get('price_filter')
    sort_by = request.GET.get('sort_by')

    products = filter_products(
        price_filter=price_filter,
        category_filter=sub_category,
        sort_by=sort_by
    ).filter(main_category=main_category, age_group=age_group)

    products = products.only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category,
        'sub_category': sub_category,
        'age_group': age_group,
        'price_filter': price_filter,
        'sort_by': sort_by,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    extra_images = product.extra_images.only("image", "color_name")  # تحسين
    related_products = Product.objects.filter(
        sub_category=product.sub_category
    ).exclude(id=product.id).only("id", "name", "price", "discount_price", "image")[:4]

    return render(request, 'myapp/product_detail.html', {
        'product': product,
        'extra_images': extra_images,
        'related_products': related_products,
    })

def hot_sale_view(request):
    hot_products = Product.objects.filter(is_hot_sale=True)
    return render(request, 'myapp/hot_sale.html', {'hot_products': hot_products})

# ============================== سلة الشراء ==============================

def cart_detail(request):
    session_key = cart_service.get_or_create_session_key(request)
    cart_items, total_price = cart_service.get_cart_items_and_total(session_key)
    return render(request, 'myapp/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            selected_color = request.POST.get('selected_color')
            product = cart_service.add_product_to_cart(product_id, request)

            if selected_color:
                print(f"Selected Color URL: {selected_color}")

            messages.success(request, f'"{product.name}" has been added to your cart successfully!')
        except Exception as e:
            print(f"Error adding to cart: {e}")
            messages.error(request, "There was a problem adding the product to the cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def remove_from_cart(request, item_id):
    session_key = cart_service.get_or_create_session_key(request)
    item = get_object_or_404(CartItem, id=item_id, session_key=session_key)

    product_name = item.product.name  # نحفظ الاسم قبل الحذف
    item.delete()

    messages.success(request, f'"{product_name}" removed from cart.')
    return redirect('cart_detail')


def increase_quantity(request, item_id):
    cart_service.increase_cart_item_quantity(item_id, request)
    return redirect('cart_detail')

def decrease_quantity(request, item_id):
    cart_service.decrease_cart_item_quantity(item_id, request)
    return redirect('cart_detail')


# ============================== المفضلة ==============================

def add_to_wishlist(request, product_id):
    session_key = cart_service.get_or_create_session_key(request)
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(session_key=session_key, product=product)
    messages.success(request, f'"{product.name}" has been added to your favorites!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def favoritelist(request):
    session_key = cart_service.get_or_create_session_key(request)
    favorites = WishlistItem.objects.filter(session_key=session_key)
    return render(request, 'myapp/favorite.html', {'favorites': favorites})

def remove_from_wishlist(request, product_id):
    session_key = cart_service.get_or_create_session_key(request)
    item = WishlistItem.objects.filter(session_key=session_key, product_id=product_id).first()
    if item:
        item.delete()
        messages.success(request, "Product removed from your favorites.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# ============================== الدفع و الطلب ==============================

def checkout(request):
    form = OrderForm(request.POST or None)
    session_key = request.session.session_key or request.session.create() or request.session.session_key

    price_data = order_service.calculate_total_prices(session_key)
    subtotal = Decimal(price_data['subtotal'])

    shipping_fee = Decimal(0)
    government_id = request.POST.get('government')
    if request.method == 'POST' and government_id and government_id.isdigit():
        shipping_fee = order_service.get_shipping_fee(government_id)

    promo_code_str = request.POST.get('promo_code', '').strip()
    discount_amount = order_service.apply_promo_code(promo_code_str, subtotal, request)
    grand_total = subtotal - discount_amount + shipping_fee

    if request.method == 'POST':
        if form.is_valid():
            payment_method = request.POST.get('payment_method', 'Cash')
            if payment_method == 'visa':
                return redirect('payment_redirect')
            elif payment_method in ['instapay', 'Cash']:
                order = form.save(commit=False)
                order.shipping_fee = shipping_fee
                order.total_price = grand_total
                order.payment_method = payment_method
                order_service.create_order(order, session_key)
                messages.success(request, "Your order has been placed successfully!")
                return redirect('order_success', order_id=order.id)
        else:
            messages.error(request, "Please correct the errors below.")

    governments = cache.get('governments_list')
    if not governments:
        governments = Government.objects.only('id', 'name')
        cache.set('governments_list', governments, 60 * 60)

    return render(request, 'myapp/checkout.html', {
        'form': form,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total,
        'governments': governments,
        'discount_amount': discount_amount if discount_amount > 0 else None,
        'promo_code_str': promo_code_str,
    })

def validate_promo_code(request):
    code = request.POST.get('promo_code', '').strip()
    subtotal = Decimal(request.POST.get('subtotal', '0'))

    discount = order_service.apply_promo_code(code, subtotal, request)

    return JsonResponse({
        'valid': discount > 0,
        'discount': float(discount)
    })

def order_success(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    order_items = order.order_items.all()
    return render(request, 'myapp/order_success.html', {
        'order': order,
        'order_items': order_items
    })


# ============================== لوحة التحكم ==============================

@staff_member_required
def dashboard_home(request):
    return render(request, 'dashboard/home.html', {
        'orders_count': CustomerOrder.objects.count(),
        'products_count': Product.objects.count(),
        'pending_orders': CustomerOrder.objects.filter(status='PENDING').count(),
        'promo_count': PromoCode.objects.count(),
    })

@staff_member_required
def dashboard_orders(request):
    status_filter = request.GET.get('status')
    orders = CustomerOrder.objects.all().order_by('-order_date')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/orders_list.html', {'orders': orders})

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    status_choices = [
        {'value': value, 'label': label, 'selected': value == order.status}
        for value, label in CustomerOrder.STATUS_CHOICES
    ]
    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'status_choices': status_choices
    })

@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(CustomerOrder.STATUS_CHOICES):
        order.status = new_status
        order.save()
    return redirect('order_detail', order_id=order.id)

@require_POST
@staff_member_required
def delete_order(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    order.delete()
    messages.success(request, "تم حذف الطلب بنجاح.")
    return redirect('dashboard_orders')

@staff_member_required
def dashboard_products(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'dashboard/products_list.html', {'products': products})

@require_POST
@staff_member_required
def delete_product(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if product:
        product.delete()
        messages.success(request, "Product deleted successfully.")
    else:
        messages.error(request, "Product not found.")
    return redirect('dashboard_products')
