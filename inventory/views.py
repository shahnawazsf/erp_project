from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Warehouse, Stock, StockMovement


@login_required
def product_list(request):
    products = Product.objects.select_related('category').filter(is_active=True)
    categories = Category.objects.all()
    cat_filter = request.GET.get('category')
    search = request.GET.get('search', '')
    if cat_filter:
        products = products.filter(category_id=cat_filter)
    if search:
        products = products.filter(name__icontains=search) | products.filter(code__icontains=search)
    return render(request, 'inventory/product_list.html', {
        'products': products, 'categories': categories,
        'cat_filter': cat_filter, 'search': search,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.movements.order_by('-created_at')[:20]
    return render(request, 'inventory/product_detail.html', {'product': product, 'movements': movements})


@login_required
def product_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        messages.success(request, 'Product added successfully.')
        return redirect('inventory_products')
    return render(request, 'inventory/product_form.html', {'categories': categories})


@login_required
def stock_list(request):
    stocks = Stock.objects.select_related('product', 'warehouse').all()
    return render(request, 'inventory/stock_list.html', {'stocks': stocks})


@login_required
def movement_list(request):
    movements = StockMovement.objects.select_related('product', 'warehouse').order_by('-created_at')[:50]
    return render(request, 'inventory/movement_list.html', {'movements': movements})


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'inventory/warehouse_list.html', {'warehouses': warehouses})
