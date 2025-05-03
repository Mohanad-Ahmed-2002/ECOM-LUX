from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from .models import Product,CartItem,CustomerOrder,Government,OrderItem,PromoCode,WishlistItem,ProductImage
from decimal import Decimal
from django.http import JsonResponse
from .services import order_service,cart_service,product_service
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django import forms
from django.forms import modelformset_factory
from .forms import OrderForm
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Create your views here.
def home(request):
    return render(request,'myapp/home.html')

def about(request):
    return render(request,'myapp/about.html')

from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Product, ProductImage

@cache_page(60 * 5)  # كاش 5 دقايق
def products_by_main_category(request, main_category):
    products = Product.objects.filter(
        main_category=main_category.upper()
    ).only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category,
    })

def products_by_main_and_sub_category(request, main_category, sub_category):
    products = Product.objects.filter(
        main_category=main_category.upper(),
        sub_category=sub_category.upper()
    ).only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category,
        'sub_category': sub_category,
    })

def products_by_main_sub_and_age(request, main_category, sub_category, age_group):
    products = Product.objects.filter(
        main_category=main_category.upper(),
        sub_category=sub_category.upper(),
        age_group=age_group.capitalize()
    ).only("id", "name", "price", "discount_price", "image").prefetch_related(
        Prefetch('extra_images', queryset=ProductImage.objects.only('image', 'color_name'))
    )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {
        'page_obj': page_obj,
        'main_category': main_category.upper(),
        'sub_category': sub_category.upper(),
        'age_group': age_group.capitalize()
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # الصور الإضافية
    extra_images = product.extra_images.all()

    # المنتجات المشابهة (حسب نفس الفئة الفرعية)
    related_products = Product.objects.filter(
        sub_category=product.sub_category,
    ).exclude(id=product.id)[:4]  # عرض 4 منتجات فقط

    return render(request, 'myapp/product_detail.html', {
        'product': product,
        'extra_images': extra_images,
        'related_products': related_products,
    })

def cart_detail(request):
    session_key = cart_service.get_or_create_session_key(request)
    cart_items, total_price = cart_service.get_cart_items_and_total(session_key)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'myapp/cart_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        selected_color = request.POST.get('selected_color')  # قراءة اللون أو الصورة المختارة

        product = cart_service.add_product_to_cart(product_id, request)

        if selected_color:
            print(f"Selected Color URL: {selected_color}")  #

        messages.success(request, f'"{product.name}" has been added to your cart successfully!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def increase_quantity(request, item_id):
    cart_service.increase_cart_item_quantity(item_id, request)
    return redirect('cart_detail')

def decrease_quantity(request, item_id):
    cart_service.decrease_cart_item_quantity(item_id,request)
    return redirect('cart_detail')

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
    code = request.GET.get('code', '').strip()
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    
    discount = order_service.apply_promo_code(code, subtotal)  # request مش محتاجينها هنا

    if discount > 0:
        return JsonResponse({'valid': True, 'discount': float(discount)})
    else:
        return JsonResponse({'valid': False, 'message': 'Promo code is not valid or expired'})

def order_success(request,order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    order_items = order.order_items.all()

    order_id=order.id
    context = {
        'order': order,
        'order_items': order_items
    }

    return render(request,'myapp/order_success.html',context)

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

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, session_key=cart_service.get_or_create_session_key(request))
    product_name = item.product.name
    item.delete()
    messages.success(request, f'"{item.product.name}" removed from cart.')
    return redirect('cart_detail')


@staff_member_required
def dashboard_home(request):
    orders_count = CustomerOrder.objects.count()
    products_count = Product.objects.count()
    pending_orders = CustomerOrder.objects.filter(status='PENDING').count()
    promo_count = PromoCode.objects.count()



    return render(request, 'dashboard/home.html', {
        'orders_count': orders_count,
        'products_count': products_count,
        'pending_orders': pending_orders,
        'promo_count': promo_count,

    })

@staff_member_required
def dashboard_orders(request):
    status_filter = request.GET.get('status')
    if status_filter:
        orders = CustomerOrder.objects.filter(status=status_filter).order_by('-order_date')
    else:
        orders = CustomerOrder.objects.all().order_by('-order_date')

    return render(request, 'dashboard/orders_list.html', {'orders': orders})

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)

    status_choices = []
    for value, label in CustomerOrder.STATUS_CHOICES:
        status_choices.append({
            'value': value,
            'label': label,
            'selected': value == order.status  
        })

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'status_choices': status_choices
    })

@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(CustomerOrder.STATUS_CHOICES).keys():
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

@staff_member_required
@require_POST
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    return redirect('dashboard_products')

