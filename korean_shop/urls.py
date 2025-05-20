"""
URL configuration for korean_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from accounts.views import register
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.urls import path
from cart.views import get_user_cart


class LoginMessageView(auth_views.LoginView):
    def form_valid(self, form):
        # Если пользователь уже вошел, выводим сообщение
        if self.request.user.is_authenticated:
            messages.info(self.request, "Вы уже авторизованы.")
        else:
            user = form.get_user()
            messages.success(self.request, f'✅ Добро пожаловать, {user.username}!')

            # Получаем или создаем корзину для пользователя
            cart = get_user_cart(self.request, user)

        return super().form_valid(form)

class LogoutMessageView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "🚪 Вы вышли из аккаунта.")
        else:
            messages.info(request, "Вы уже вышли из аккаунта.")
        return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path("register/", register, name="register"),
    path("login/", LoginMessageView.as_view(template_name="accounts/login.html"), name="login"),  # Используем кастомное представление
    path("logout/", LogoutMessageView.as_view(), name="logout"),  # Используем кастомное представление
    path('accounts/', include('accounts.urls')),
    path('', include("products.urls", namespace='products')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
