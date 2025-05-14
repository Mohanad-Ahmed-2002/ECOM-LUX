import pytest
from django.urls import reverse
from store.models import CartItem, Government,WishlistItem, CustomerOrder, PromoCode,Product,ProductImage
from django.test import RequestFactory
from store.views import add_to_wishlist,remove_from_wishlist
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages.middleware import MessageMiddleware
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


def attach_session_and_messages(request):
    # تفعيل session
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()

    # تفعيل message framework
    setattr(request, '_messages', FallbackStorage(request))

@pytest.mark.django_db
def test_products_by_main_category(client):
    # نجهز منتجات من نوعين
    Product.objects.create(name="P1", price=100, main_category="SUNGLASSES", image="img1", age_group="Men")
    Product.objects.create(name="P2", price=200, main_category="OPTICAL", image="img2", age_group="Men")

    # نطلب المنتجات حسب نوع SUNGLASSES
    url = reverse('products_by_main_category', args=['sunglasses'])
    response = client.get(url)

    assert response.status_code == 200

    page_obj = response.context['page_obj']
    assert page_obj.paginator.count == 1
    product = page_obj.object_list[0]
    assert product.main_category == "SUNGLASSES"

@pytest.mark.django_db
def test_products_by_main_and_sub_category(client):
    # منتج بنوع وتصنيف معين
    Product.objects.create(
        name="Combo Product",
        price=120,
        main_category="SUNGLASSES",
        sub_category="KIDS",
        image="img",
        age_group="Kids"
    )

    # منتج من نوع تاني
    Product.objects.create(
        name="Other",
        price=100,
        main_category="SUNGLASSES",
        sub_category="MEN",
        image="img",
        age_group="Men"
    )

    url = reverse('products_by_main_and_sub_category', args=['sunglasses', 'kids'])
    response = client.get(url)

    assert response.status_code == 200

    page_obj = response.context['page_obj']
    assert page_obj.paginator.count == 1
    product = page_obj.object_list[0]
    assert product.sub_category == "KIDS"

@pytest.mark.django_db
def test_products_by_main_sub_and_age(client):
    # منتج بالمواصفات الكاملة
    Product.objects.create(
        name="Combo Full",
        price=150,
        main_category="SUNGLASSES",
        sub_category="KIDS",
        age_group="Kids",
        image="img"
    )

    # منتج تاني مشابه لكن Age مختلف
    Product.objects.create(
        name="Wrong Age",
        price=150,
        main_category="SUNGLASSES",
        sub_category="KIDS",
        age_group="Men",
        image="img"
    )

    url = reverse('products_by_main_sub_and_age', args=['sunglasses', 'kids', 'kids'])
    response = client.get(url)

    assert response.status_code == 200

    page_obj = response.context['page_obj']
    assert page_obj.paginator.count == 1
    product = page_obj.object_list[0]
    assert product.age_group == "Kids"

@pytest.mark.django_db
def test_product_detail_view(client, product):
    ProductImage.objects.create(product=product, image="extra.jpg", color_name="Red")

    Product.objects.create(
        name="Related",
        price=120,
        main_category=product.main_category,
        sub_category=product.sub_category,
        image="img",
        age_group=product.age_group
    )

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)

    assert response.status_code == 200

    # نأخذ ثاني dict في context list
    context = response.context[1]  # ✅ بناءً على الخطأ اللي شفته

    assert 'product' in context
    assert context['product'].id == product.id

    assert 'extra_images' in context
    assert len(context['extra_images']) == 1

    assert 'related_products' in context
    assert context['related_products'].count() == 1


@pytest.mark.django_db
def test_checkout_view(client,product):

    session_key = client.session.session_key or client.session.create() or client.session.session_key
    CartItem.objects.create(product=product,session_key=client.session.session_key,quantity=2)

    gov = Government.objects.create(name="Cairo", shipping_fee=50)

    # نجهز بيانات POST لعمل checkout
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'address': '123 Street',
        'phone': '01060961669',
        'government': gov.id,
        'promo_code': '',
        'payment_method': 'Cash'
    }

    url = reverse('checkout')
        # نتأكد إن الصفحة رجعت تمام
    response = client.post(url, data, follow=True)

    # نتأكد من الوصول للصفحة النهائية
    assert response.status_code == 200

    # دلوقتي نقدر نستخدم context
    context = response.context

    # نتحقق من وجود order
    assert 'order' in context
    assert context['order'].total_price > 0

@pytest.mark.django_db
def test_add_to_wishlist(product):

    factory = RequestFactory()
    request = factory.get('/')
    attach_session_and_messages(request)

    response = add_to_wishlist(request,product.id)

    assert WishlistItem.objects.count() == 1
    wishlist = WishlistItem.objects.first()
    assert wishlist.product == product
    assert response.status_code == 302 


@pytest.mark.django_db
def test_remove_from_wishlist(product):
    factory = RequestFactory()
    request = factory.get('/')
    attach_session_and_messages(request)

    # نحط منتج في المفضلة يدويًا
    WishlistItem.objects.create(product=product, session_key=request.session.session_key)

    # نتحقق إنه موجود
    assert WishlistItem.objects.count() == 1

    # ننفذ الفيو لإزالته
    response = remove_from_wishlist(request, product.id)

    assert response.status_code == 302
    assert WishlistItem.objects.count() == 0

@pytest.mark.django_db
def test_favoritelist_view(client, product):
    session_key = client.session.session_key or client.session.create() or client.session.session_key

    # أضف منتج للمفضلة
    WishlistItem.objects.create(product=product, session_key=session_key)

    # استدعاء view من خلال URL
    url = reverse('favorite')  # ده اسم المسار في urls.py
    response = client.get(url)

    assert response.status_code == 200

    # تأكد إن المنتج موجود في السياق
    favorites = response.context['favorites']
    assert favorites.count() == 1
    assert favorites.first().product == product

@pytest.mark.django_db
def test_validate_promo_code_valid(client):
    PromoCode.objects.create(
        code='SAVE10',
        discount_percentage=10,
        is_active=True,
        expiration_date=timezone.now() + timedelta(days=10)
    )

    url = reverse('validate_promo_code')
    response = client.post(url, {
        'promo_code': 'SAVE10',
        'subtotal': '200'
    })

    assert response.status_code == 200
    data = response.json()
    assert data['discount'] == 20  # 10% of 200

@pytest.mark.django_db
def test_validate_promo_code_invalid(client):
    url = reverse('validate_promo_code')
    response = client.post(url, {
        'promo_code': 'FAKECODE',
        'subtotal': '200'
    })

    assert response.status_code == 200
    data = response.json()
    print("Response JSON:", data)  # مؤقتًا لو حبيت تشوفه
    assert 'discount' in data
    assert data['discount'] == 0


@pytest.mark.django_db
def test_dashboard_home_view(client):
    # إنشاء مستخدم admin
    admin_user = User.objects.create_user(username='admin', password='1234', is_staff=True)
    client.login(username='admin', password='1234')

    # إضافة بيانات لاختبار الإحصائيات
    Product.objects.create(name="P1", price=100, main_category="SUNGLASSES", image="img", age_group="Men")
    PromoCode.objects.create(code="SAVE", discount_percentage=10, is_active=True, expiration_date="2099-01-01")
    CustomerOrder.objects.create(name="Ali", email="a@a.com", address="x", phone="010", total_price=100, government=None)

    url = reverse('dashboard_home')
    response = client.get(url)

    assert response.status_code == 200
    context = response.context
    assert context['orders_count'] == 1
    assert context['products_count'] == 1
    assert context['pending_orders'] == 1
    assert context['promo_count'] == 1

@pytest.mark.django_db
def test_dashboard_orders_view_with_filter(client):
    # إنشاء مستخدم مشرف
    user = User.objects.create_user(username='admin2', password='1234', is_staff=True)
    client.login(username='admin2', password='1234')

    # إنشاء طلبات بحالات مختلفة
    CustomerOrder.objects.create(name='Ali', email='a@a.com', address='X', phone='010', total_price=100, shipping_fee=0, status='PENDING', government=None)
    CustomerOrder.objects.create(name='Sara', email='s@s.com', address='Y', phone='011', total_price=200, shipping_fee=0, status='SHIPPED', government=None)

    # تصفية حسب الحالة
    url = reverse('dashboard_orders') + '?status=PENDING'
    response = client.get(url)

    assert response.status_code == 200
    orders = response.context['orders']
    assert orders.count() == 1
    assert orders.first().name == 'Ali'


@pytest.mark.django_db
def test_delete_order_view(client):
    # إنشاء مشرف
    user = User.objects.create_user(username='admin3', password='1234', is_staff=True)
    client.login(username='admin3', password='1234')

    # إنشاء طلب وهمي
    order = CustomerOrder.objects.create(
        name='To Delete',
        email='x@x.com',
        address='X',
        phone='011',
        total_price=150,
        shipping_fee=0,
        status='PENDING',
        government=None
    )

    # تنفيذ حذف بـ POST
    url = reverse('delete_order', args=[order.id])
    response = client.post(url)

    # تحقق من الحذف
    assert response.status_code == 302  # Redirect بعد الحذف
    assert not CustomerOrder.objects.filter(id=order.id).exists()
