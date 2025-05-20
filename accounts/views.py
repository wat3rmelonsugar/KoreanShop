from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Favorite
from products.models import Product
from django.http import JsonResponse


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "✅ Вы успешно зарегистрировались! Пожалуйста, войдите.")
            return redirect('login')  # Замените 'home' на вашу главную страницу
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'accounts/favorites.html', {'favorites': favorites})


@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            favorite.delete()
            return JsonResponse({'status': 'removed'})
        else:
            return JsonResponse({'status': 'added'})

    return JsonResponse({'status': 'error'}, status=400)



