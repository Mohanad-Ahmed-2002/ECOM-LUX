from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from .models import Product,CartItem,CustomerOrder,OrderForm,Government,OrderItem,PromoCode,WishlistItem,ProductImage
from decimal import Decimal
from django.http import JsonResponse
from .services import order_service,cart_service,product_service
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django import forms
from django.forms import modelformset_factory
from .forms import ProductForm, ProductImageFormSet,GovernmentForm


# Create your views here.
def home(request):
    return render(request,'myapp/home.html')

def about(request):
    return render(request,'myapp/about.html')

def products_by_main_category(request, main_category):
    products = Product.objects.filter(main_category=main_category.upper())
    paginator = Paginator(products, 10)  # 10 منتج في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/shop_list.html', {'page_obj': page_obj, 'main_category': main_category})

def products_by_main_and_sub_category(request, main_category, sub_category):
    products = Product.objects.filter(main_category=main_category.upper(), sub_category=sub_category.upper())
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'myapp/shop_list.html', {'page_obj': page_obj, 'main_category': main_category, 'sub_category': sub_category})

def products_by_main_sub_and_age(request, main_category, sub_category, age_group):
    products = Product.objects.filter(
        main_category=main_category.upper(),
        sub_category=sub_category.upper(),
        age_group=age_group.capitalize()
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
    session_key = request.session.session_key   
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    price_data = order_service.calculate_total_prices(session_key)
    subtotal = Decimal(price_data['subtotal'])

    shipping_fee = Decimal(0)
    government_id = request.POST.get('government')

    if request.method == 'POST' and government_id:
        shipping_fee = order_service.get_shipping_fee(government_id)

    promo_code_str = request.POST.get('promo_code', '').strip()
    discount_amount = order_service.apply_promo_code(promo_code_str, subtotal, request)

    grand_total = subtotal - discount_amount + shipping_fee

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'Cash')  # افتراضي Cash لو مفيش اختيار

        if payment_method == 'visa':
            # العميل اختار Visa ➔ نحوله لصفحة الدفع
            return redirect('payment_redirect')  # لازم يكون عندك URL اسمه payment_redirect

        elif payment_method in ['instapay', 'Cash']:
            if form.is_valid():
                order = form.save(commit=False)
                order.shipping_fee = shipping_fee
                order.total_price = grand_total
                order.payment_method = payment_method  # نحفظ طريقة الدفع
                order_service.create_order(order, session_key)
                messages.success(request, "Your order has been placed successfully!")
                return redirect('order_success', order_id=order.id)

    governments = Government.objects.all()

    return render(request, 'myapp/checkout.html', {
        'form': form,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total,
        'governments': governments,
        'discount_amount': discount_amount if discount_amount > 0 else None,
        'promo_code_str': promo_code_str,
    })

def payment_redirect(request):
    return render(request, 'myapp/payment_redirect.html')


def order_success(request,order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    order_items = order.order_items.all()

    order_id=order.id
    context = {
        'order': order,
        'order_items': order_items
    }

    return render(request,'myapp/order_success.html',context)

def validate_promo_code(request):
    code = request.GET.get('code', '').strip()
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    
    discount = order_service.apply_promo_code(code, subtotal)  # request مش محتاجينها هنا

    if discount > 0:
        return JsonResponse({'valid': True, 'discount': float(discount)})
    else:
        return JsonResponse({'valid': False, 'message': 'Promo code is not valid or expired'})
    
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
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect('dashboard_products')

    return render(request, 'dashboard/edit_product.html', {'form': form, 'product': product})

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


@staff_member_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()

            for form in formset.cleaned_data:
                if form and 'image' in form:
                    ProductImage.objects.create(
                        product=product,
                        image=form['image'],
                        color_name=form.get('color_name', '')
                    )

            messages.success(request, "Product added successfully.")
            return redirect('dashboard_products')
    else:
        product_form = ProductForm()
        formset = ProductImageFormSet(queryset=ProductImage.objects.none())

    return render(request, 'dashboard/add_product.html', {
        'product_form': product_form,
        'formset': formset,
    })

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_percentage', 'is_active', 'expiration_date']

@staff_member_required
def dashboard_promo_codes(request):
    edit_id = request.GET.get('edit')
    promo_to_edit = None

    if edit_id:
        promo_to_edit = get_object_or_404(PromoCode, id=edit_id)
        form = PromoCodeForm(request.POST or None, instance=promo_to_edit)
    else:
        form = PromoCodeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Promo code saved successfully.")
        return redirect('dashboard_promo_codes')

    codes = PromoCode.objects.all().order_by('-id')
    return render(request, 'dashboard/promo_codes_list.html', {
        'codes': codes,
        'form': form,
        'editing': promo_to_edit
    })

@staff_member_required
def delete_promo_code(request, promo_id):
    promo = get_object_or_404(PromoCode, id=promo_id)
    promo.delete()
    messages.success(request, "Promo code deleted.")
    return redirect('dashboard_promo_codes')

@staff_member_required
def dashboard_shipping(request):
    edit_id = request.GET.get('edit')
    gov_to_edit = None

    if edit_id:
        gov_to_edit = get_object_or_404(Government, id=edit_id)
        form = GovernmentForm(request.POST or None, instance=gov_to_edit)
    else:
        form = GovernmentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Saved successfully.")
        return redirect('dashboard_shipping')

    governments = Government.objects.all().order_by('name')
    return render(request, 'dashboard/shipping_list.html', {
        'form': form,
        'governments': governments,
        'editing': gov_to_edit
    })

@staff_member_required
def delete_government(request, gov_id):

    gov = get_object_or_404(Government, id=gov_id)
    gov.delete()
    messages.success(request, "Deleted successfully.")
    return redirect('dashboard_shipping')

