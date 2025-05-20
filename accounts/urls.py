from django.urls import path
from .views import toggle_favorite, favorites_list

app_name = 'accounts'
urlpatterns = [
    path('toggle-favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites_list, name='favorites_list'),
]
