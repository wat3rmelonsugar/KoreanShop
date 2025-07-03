from django.urls import path
from .views import questionnaire_view

app_name = 'rec'

urlpatterns = [
    path("questionnaire/", questionnaire_view, name="questionnaire"),
]
