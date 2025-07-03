from django.urls import path
from .views import toggle_favorite, favorites_list, account_profile_view

app_name = 'accounts'
urlpatterns = [
    path('toggle-favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('profile/', account_profile_view, name='account_profile'),
]
