from .models import Product

def filter_products(price_filter=None, category_filter=None, sort_by=None):
    products = Product.objects.all()

    # فلتر حسب التصنيف
    if category_filter:
        products = products.filter(sub_category__iexact=category_filter)

    # فلتر حسب السعر
    if price_filter:
        if '-' in price_filter:
            parts = price_filter.split('-')
            min_price = float(parts[0]) if parts[0] else 0
            max_price = float(parts[1]) if len(parts) > 1 and parts[1] else None

            if max_price:
                products = products.filter(price__gte=min_price, price__lte=max_price)
            else:
                products = products.filter(price__gte=min_price)

    # ترتيب النتائج
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    return products
