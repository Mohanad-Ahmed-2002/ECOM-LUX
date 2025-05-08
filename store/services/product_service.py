from store.models import Product

def filter_products(price_filter=None, category_filter=None, sort_by=None):
    products = Product.objects.all()

    # ترتيب المنتجات
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')  

    else:
        products = products.order_by('-id')  # Default sort

    return products
