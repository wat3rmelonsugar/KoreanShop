from django.shortcuts import render
from .forms import QuestionnaireForm
from .tasks import calculate_skin_type, select_products, generate_pdf, send_email
from celery import chain

from django.shortcuts import render
from .forms import QuestionnaireForm
from .main import run_task_chain  # Импортируем функцию запуска цепочк
from products.models import Product
from accounts.models import Favorite

def questionnaire_view(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            # Собираем ответы из формы
            user_answers = {
                str(i): form.cleaned_data[f"question_{i}"]
                for i in range(1, 10)
            }
            user_answers["10"] = form.cleaned_data["question_10"]

            user_email = form.cleaned_data.get('email')
            user_id = request.user.id if request.user.is_authenticated else None

            run_task_chain(user_answers, user_email, user_id)

            # Добавляем товары в избранное, если пользователь вошёл в систему
            if request.user.is_authenticated:
                # Пример: список ID товаров, которые надо добавить в избранное
                recommended_product_ids = [10, 12, 13, 14]

                for product_id in recommended_product_ids:
                    try:
                        product = Product.objects.get(id=product_id)
                        Favorite.objects.get_or_create(user=request.user, product=product)
                    except Product.DoesNotExist:
                        continue  # Пропускаем, если товар не найден

            return render(request, "recommendation/thank_you.html")
    else:
        form = QuestionnaireForm()

    return render(request, "recommendation/questionnaire.html", {"form": form})