from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Brand, Review
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .forms import ReviewForm
from accounts.models import Favorite  # или откуда у тебя модель избранного
from django.db.models import Q

def ajax_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(Q(name__icontains=query)) if query else Product.objects.all()

    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': product.price,
            'image_url': product.image.url if product.image else '',
        })

    return JsonResponse({'products': data})

def product_list(request, category_slug=None, brand_slug=None):
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    else:
        category_slug_param = request.GET.get('category')
        if category_slug_param:
            category = get_object_or_404(Category, slug=category_slug_param)

    if category:
        products = products.filter(category=category)

    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
    else:
        brand_slug_param = request.GET.get('brand')
        if brand_slug_param:
            brand = get_object_or_404(Brand, slug=brand_slug_param)

    if brand:
        products = products.filter(brand=brand)

    in_stock = request.GET.get('in_stock')
    if in_stock == 'yes':
        products = products.filter(available=True)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    order = request.GET.get('order')
    price_order = request.GET.get('price')

    if order == 'name_asc':
        products = products.order_by('name')
    elif order == 'name_desc':
        products = products.order_by('-name')
    elif price_order == 'low_to_high':
        products = products.order_by('price')
    elif price_order == 'high_to_low':
        products = products.order_by('-price')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product/list.html', {
        'category': category,
        'categories': categories,
        'brands': brands,
        'products': page_obj,
        'selected_order': order,
        'selected_price': price_order,
        'brand': brand,
        'in_stock': in_stock,
        'min_price': min_price,
        'max_price': max_price,
        'page_obj': page_obj,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    is_favorite = False
    form = ReviewForm()

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'add':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    new_review = form.save(commit=False)
                    new_review.user = request.user
                    new_review.product = product
                    new_review.save()
                    return redirect(request.path_info)

            elif action == 'edit':
                review = get_object_or_404(Review, id=request.POST.get('review_id'))
                if review.user != request.user:
                    return HttpResponseForbidden()
                form = ReviewForm(request.POST, instance=review)
                if form.is_valid():
                    form.save()
                    return redirect(request.path_info)

            elif action == 'delete':
                review = get_object_or_404(Review, id=request.POST.get('review_id'))
                if review.user == request.user:
                    review.delete()
                    return redirect(request.path_info)

    return render(request, 'products/product/detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'is_favorite': is_favorite
    })

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if review.user != request.user:
        return HttpResponseForbidden("You cannot edit someone else's review.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('products:product_detail', id=review.product.id, slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'products/edit_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if review.user != request.user:
        return HttpResponseForbidden("You cannot delete someone else's review.")

    product = review.product
    review.delete()
    return redirect('products:product_detail', id=product.id, slug=product.slug)


def product_list_by_brand(request, brand_slug):
    brand = get_object_or_404(Brand, slug=brand_slug)
    products = Product.objects.filter(brand=brand)
    return render(request, 'products/product/list.html', {'brand': brand, 'products': products})
