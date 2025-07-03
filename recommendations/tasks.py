from fpdf import FPDF
import re
import smtplib
import os
from email.message import EmailMessage
import pandas as pd
import numpy as np
from .models import UserRecommendation
from django.contrib.auth import get_user_model


questions = {1: "Как часто вы испытываете ощущение сухости на вашем лице?\n",
 2: "Как ваша кожа реагирует на обычное мыло?\n",
 3: "Как часто вы замечаете блеск или жирный блеск на вашем лице?\n",
 4: "Как ваша кожа реагирует на изменения погоды, такие как холод или влажность?\n",
 5: "Как вы оцениваете состояние пор на вашем лице?\n",
 6: "Как вы оцениваете уровень упругости вашей кожи?\n",
 7: "Сколько часов вы в среднем спите?\n",
 8: "Какой уровень SPF предпочитаете для солнцезащиты?\n",
 9: "Есть ли у вас какие-либо аллергии или чувствительность к определенным ингредиентам?\n",
 10: "Какие проблемы с кожей вас беспокоят? (можно выбрать несколько вариантов)\n",
}

answers = {1: "1 - Почти никогда\n"
 "2 - Иногда, особенно после мытья\n"
 "3 - Часто, моя кожа постоянно чувствует сухость\n",
 2: "1 - Она обычно остается мягкой и увлажненной\n"
 "2 - Она становится немного сухой и стянутой\n"
 "3 - Она становится сухой и раздраженной\n",
 3: "1 - Почти никогда\n"
 "2 - Иногда, особенно в течение дня\n"
 "3 - Часто, моя кожа постоянно выглядит жирной\n",
 4: "1 - Она обычно не реагирует или реагирует слабо\n"
 "2 - Она становится немного сухой или раздраженной\n"
 "3 - Она реагирует сильно, меняя текстуру или высыпаниями\n",
 5: "1 - Они мало заметны и не вызывают проблем\n"
 "2 - Они видны, но не вызывают беспокойства\n"
 "3 - Они заметны и порой забиты, вызывая проблемы с чистотой кожи\n",
 6: "1 - Она обычно кажется упругой и эластичной\n"
 "2 - Она немного утратила упругость, но еще не слишком заметно\n"
 "3 - Она потеряла значительную упругость, появились морщины или провисание\n",
 7: "1 - Менее 4 часов в день\n"
 "2 - 5-6 часов в день\n"
 "3 - 8 часов и более\n",
 8: "1 - SPF 15-30\n"
 "2 - SPF 30-50\n"
 "3 - SPF 50+\n"
 "4 - Я предпочитаю косметику без SPF\n",
 9: "1 - Да\n"
 "2 - Нет\n",
 10: "1 - Акне/прыщи\n"
 "2 - Пигментные пятна\n"
 "3 - Повышенная чувствительность\n"
 "4 - Морщины/старение кожи\n"
 "5 - Раздражение\n"
 "6 - Нет проблем, хочу поддерживать здоровье кожи\n",
}

# блоки правил: для сухой, для жирной, для комби, для нормальной, для возрастной

from experta import *
from .celery_config import app


class SkinCareExpert(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        # Меры доверия
        self.dry = 0
        self.oily = 0
        self.combined = 0
        self.normal = 0

        # Меры недоверия
        self.mnd_dry = 0
        self.mnd_oily = 0
        self.mnd_combined = 0
        self.mnd_normal = 0

        self.acne = 0
        self.pigmented = 0
        self.sensitive = 0
        self.wrinkles = 0
        self.puffy = 0
        self.none = 1

    weights = {
        1: 0.25,
        2: 0.2,
        3: 0.2,
        4: 0.1,
        5: 0.05,
        6: 0.05,
        7: 0.03,
        8: 0.03,
        9: 0.04,
        10: 0.05
    }

    @Rule(Fact(answ="1-3") | Fact(answ="2-3") | Fact(answ="4-2"))
    def plusDry(self):
        self.dry += (0.7 * self.weights[1]) * (1 - self.dry)
        self.mnd_oily += (0.3 * self.weights[2]) * (1 - self.mnd_oily)
        self.mnd_combined += (0.2 * self.weights[4]) * (1 - self.mnd_combined)
        self.mnd_normal -= (0.3 * self.weights[4]) * self.mnd_normal
        self.mnd_normal = max(0, self.mnd_normal)

    @Rule(Fact(answ="3-3") | Fact(answ="5-3"))
    def plusOily(self):
        self.oily += (1.2 * self.weights[3]) * (1 - self.oily)
        self.mnd_dry += (0.05 * self.weights[5]) * (1 - self.mnd_dry)
        self.mnd_combined += (0.07 * self.weights[3]) * (1 - self.mnd_combined)
        self.mnd_normal -= (0.2 * self.weights[5]) * self.mnd_normal
        self.mnd_normal = max(0, self.mnd_normal)

    @Rule(Fact(answ="1-2") | Fact(answ="2-2") | Fact(answ="3-2") | Fact(answ="4-1"))
    def plusCombined(self):
        self.combined += (0.8 * self.weights[3]) * (1 - self.combined)
        self.mnd_oily += (0.3 * self.weights[2]) * (1 - self.mnd_oily)
        self.mnd_dry += (0.3 * self.weights[1]) * (1 - self.mnd_dry)
        self.mnd_normal -= (0.2 * self.weights[4]) * self.mnd_normal
        self.mnd_normal = max(0, self.mnd_normal)

    @Rule(Fact(answ="1-1") | Fact(answ="2-1") | Fact(answ="3-1") | Fact(answ="4-1") | Fact(answ="5-1") | Fact(answ="6-1"))
    def plusNormal(self):
        self.normal += (0.3 * self.weights[1]) * (1 - self.normal)
        self.mnd_oily += (0.2 * self.weights[3]) * (1 - self.mnd_oily)
        self.mnd_combined += (0.2 * self.weights[5]) * (1 - self.mnd_combined)
        self.mnd_dry += (0.2 * self.weights[2]) * (1 - self.mnd_dry)

    @Rule(Fact(answ="4-3") | Fact(answ="6-3") | Fact(answ="7-1") | Fact(answ="8-4") | Fact(answ="9-1"))
    def problematic(self):
        self.dry += (0.2 * self.weights[4]) * (1 - self.dry)
        self.oily += (0.4 * self.weights[6]) * (1 - self.oily)
        self.combined += (0.3 * self.weights[8]) * (1 - self.combined)
        self.normal -= (0.2 * self.weights[9]) * self.normal
        self.normal = max(0, self.normal)

    @Rule(Fact(answ="6-2") | Fact(answ="7-2") | Fact(answ="8-1"))
    def mediumProblematic(self):
        self.dry += (0.05 * self.weights[7]) * (1 - self.dry)
        self.oily += (0.07 * self.weights[8]) * (1 - self.oily)
        self.combined += (0.05 * self.weights[6]) * (1 - self.combined)
        self.normal -= (0.1 * self.weights[6]) * self.normal
        self.normal = max(0, self.normal)

    @Rule(Fact(answ="7-3") | Fact(answ="8-2") | Fact(answ="8-3") | Fact(answ="9-2"))
    def goodCare(self):
        self.dry += (0.1 * self.weights[7]) * (1 - self.dry)
        self.oily += (0.1 * self.weights[9]) * (1 - self.oily)
        self.combined += (0.2 * self.weights[8]) * (1 - self.combined)
        self.normal -= (0.1 * self.weights[8]) * self.normal
        self.normal = max(0, self.normal)


    @Rule(Fact(answ="10-1"))
    def rule_acne(self):
        self.acne += 1
        self.none = 0

    @Rule(Fact(answ="10-2"))
    def rule_pigmented(self):
        self.pigmented += 1
        self.none = 0

    @Rule(Fact(answ="10-3"))
    def rule_sensitive(self):
        self.sensitive += 1
        self.none = 0

    @Rule(Fact(answ="10-4"))
    def rule_wrinkles(self):
        self.wrinkles += 1
        self.none = 0

    @Rule(Fact(answ="10-5"))
    def rule_puffy(self):
        self.puffy += 1
        self.none = 0

    def get_certainty_factors(self):
        return {
            'Oily': self.oily - self.mnd_oily,
            'Dry': self.dry - self.mnd_dry,
            'Normal': self.normal - self.mnd_normal,
            'Combined': self.combined - self.mnd_combined
        }

    def get_specific_conditions(self):
        return {
            'acne': self.acne,
            'none': self.none,
            'pigm': self.pigmented,
            'sens': self.sensitive,
            'wrinkles': self.wrinkles,
            'irritated': self.puffy
        }

    def checkSkincare(self):
        ku = self.get_certainty_factors()
        spec = self.get_specific_conditions()
        print(ku)
        print(spec)
        max_type = max(ku, key=ku.get)
        max_conditions = [k for k, v in spec.items() if v == 1 and k != 'none']



        return (max_type, max_conditions)

def collect_user_answers(form):
    """
    Принимает валидированную форму QuestionnaireForm,
    возвращает словарь с ответами пользователя.
    """
    answers = {}

    # Пробегаем по всем полям формы, кроме email
    for field_name, field_value in form.cleaned_data.items():
        if field_name == 'email':
            continue  # email не входит в вопросы

        # Для множественного выбора (вопрос 10) сохраняем список ответов
        if isinstance(field_value, list):
            answers[field_name] = field_value
        else:
            answers[field_name] = field_value
    print(answers)
    return answers



@app.task
def calculate_skin_type(answers):
    expert = SkinCareExpert()
    expert.reset()
    print(answers)
    for question_id, answer in answers.items():
        if isinstance(answer, list):
            for a in answer:
                expert.declare(Fact(answ=f"{question_id}-{str(a)}"))
        else:
            expert.declare(Fact(answ=f"{question_id}-{str(answer)}"))

    expert.run()
    # <<< Вот здесь вставка >>>
    print("\n--- RAW PARAMETERS ---")
    print(f"Dry: {expert.dry:.4f} | MND Dry: {expert.mnd_dry:.4f}")
    print(f"Oily: {expert.oily:.4f} | MND Oily: {expert.mnd_oily:.4f}")
    print(f"Combined: {expert.combined:.4f} | MND Combined: {expert.mnd_combined:.4f}")
    print(f"Normal: {expert.normal:.4f} | MND Normal: {expert.mnd_normal:.4f}")
    print("\nFinal Certainty Factors:", expert.get_certainty_factors())
    print("Detected Skin Conditions:", expert.get_specific_conditions())
    # <<< конец вставки >>>
    # Получаем тип кожи и состояния кожи
    skin_types, conditions = expert.get_certainty_factors(), expert.get_specific_conditions()
    print(skin_types)
    # Находим тип кожи с наибольшим значением
    best_skin_type = [max(skin_types, key=skin_types.get)]

    # Выбираем состояния, у которых значение == 1 и ключ != 'none'
    active_conditions = [cond for cond, value in conditions.items() if value == 1 and cond != 'none']

    return best_skin_type, active_conditions

## Соответствие типов кожи и их кодов
SKIN_TYPE_CODES = {
    "Oily": "O",
    "Dry": "D",
    "Normal": "N",
    "Combined": "C"
}

# Соответствие особенностей кожи и их кодов
CONDITION_CODES = {
    "acne": "A",
    "wrinkles": "Age",
    "irritated": "I",
    "pigm": "P",
    "sens": "S"
}
SKIN_TYPE_TRANSLATIONS = {
    "Oily": "Жирная",
    "Dry": "Сухая",
    "Normal": "Нормальная",
    "Combined": "Комбинированная"
}
CONDITION_TRANSLATIONS = {
    "acne": "Акне",
    "wrinkles": "Морщины",
    "irritated": "Раздражённая кожа",
    "pigm": "Пигментация",
    "sens": "Чувствительная кожа",
    'none': 'Не проблемная'
}
@app.task
def generate_recommendation_text(products, skin_label, condition_labels):
    """Формирует текстовую рекомендацию на основе подобранных товаров"""
    text = (
        f"Ваш тип кожи: {skin_label}\n"
        f"Особенности кожи: {condition_labels}\n\n"
        f"На основе этого мы рекомендуем следующие продукты:\n\n"
    )

    for group_label, group_products in products.items():
        text += f"{group_label}:\n"
        for category, items in group_products.items():
            text += f"{category}:\n"
            for item in items:
                # Обработка и форматирование названия
                product_info = item['product'].split(' (')
                product_name = product_info[0]
                details = product_info[1][:-1] if len(product_info) > 1 else ""
                formatted_name = ' '.join(
                    word.capitalize() for word in product_name.replace('-', ' ').split()
                )
                if details:
                    formatted_name += f" ({details})"
                text += f"- {formatted_name} (Цена: {item['price']*80} руб.)\n"
            text += "\n"
        text += "\n"
    return text




@app.task
def select_products(recommendations, user_id):
    """Фильтрует продукты по типу кожи и особенностям"""
    skin_type, conditions = recommendations  # Распаковываем кортеж




    # Получаем переводы
    skin_label = SKIN_TYPE_TRANSLATIONS.get(skin_type[0], "Не указан") if skin_type else "Не указан"
    condition_labels = ", ".join([CONDITION_TRANSLATIONS.get(c, c) for c in conditions]) if conditions else "Не указаны"

    print(condition_labels)

    # Коды
    skin_code = SKIN_TYPE_CODES.get(skin_type[0], "") if skin_type else ""
    condition_codes = {CONDITION_CODES[c] for c in conditions if c in CONDITION_CODES}

    # Загружаем CSV с товарами
    df = pd.read_csv("recommendations/cleaned_file_with_codes.csv")

    # Фильтрация по типу кожи
    skin_filtered = df[df['skin_type_code'].str.contains(skin_code, na=False)]
    skin_filtered = skin_filtered[skin_filtered['ranking'] >= 4.4]

    # Фильтрация по особенностям кожи
    condition_filtered = df.copy()
    if condition_codes:
        condition_filtered = condition_filtered[
            condition_filtered['skin_problem_code'].astype(str).apply(lambda x: any(c in x for c in condition_codes))
        ]
        condition_filtered = condition_filtered[condition_filtered['ranking'] >= 4.4]

    selected_products = {
        'По типу кожи': {},
        'По состояниям кожи': {}
    }

    categories = ['Cleanser', 'Toner', 'Moisturisers', 'Serum']
    category_translation = {
        'Cleanser': 'Очищающее средство',
        'Toner': 'Тоник',
        'Moisturisers': 'Крем',
        'Serum': 'Сыворотка'
    }

    def process_category(df_filtered, category, top_n):
        cat_products = df_filtered[df_filtered['category'] == category]
        if cat_products.empty:
            return []
        cat_products = cat_products.copy()
        median_price = np.median(cat_products['price'])
        cat_products.loc[:, 'Price_Diff'] = abs(cat_products['price'] - median_price)
        best_matches = cat_products.nsmallest(top_n, 'Price_Diff')
        return best_matches[['product', 'price', 'ranking']].to_dict(orient='records')

    for category in categories:
        translated_category = category_translation.get(category, category)

        # По типу кожи — 3 товара
        products_by_skin = process_category(skin_filtered, category, top_n=3)

        # По состояниям кожи — 1 товар
        products_by_condition = process_category(condition_filtered, category, top_n=1)

        if products_by_skin:
            selected_products['По типу кожи'][translated_category] = products_by_skin
        if products_by_condition:
            selected_products['По состояниям кожи'][translated_category] = products_by_condition

    # Генерация текста рекомендации с типом и состояниями кожи
    recommendation_text = generate_recommendation_text(selected_products, skin_label, condition_labels)

    # Сохраняем рекомендацию в БД
    User = get_user_model()
    user = User.objects.get(id=user_id)
    UserRecommendation.objects.create(
        user=user,
        recommendation_text=recommendation_text
    )

    return recommendation_text


PDF_FOLDER = "generated_pdfs"

from django.conf import settings


@app.task
def generate_pdf(recommendation_text, user_email):
    pdf = FPDF()
    pdf.add_page()

    # Подключаем шрифты
    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Montserrat-ExtraLight.ttf")
    font_bold_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Montserrat-SemiBold.ttf")

    pdf.add_font("Montserrat", "", font_path, uni=True)
    pdf.add_font("Montserrat", "B", font_bold_path, uni=True)

    # Настройки стилей
    primary_color = (50, 100, 150)  # Синий
    secondary_color = (100, 100, 100)  # Серый

    # Заголовок документа
    pdf.set_font("Montserrat", "B", 16)
    pdf.set_text_color(*primary_color)
    pdf.cell(0, 15, "Персональные рекомендации по уходу за кожей", 0, 1, 'C')
    pdf.ln(10)

    # Информация о пользователе
    pdf.set_font("Montserrat", "", 12)
    pdf.set_text_color(*secondary_color)
    pdf.cell(40, 8, "Создано для:", 0, 0)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, user_email, 0, 1)
    pdf.ln(15)

    # Обработка текста рекомендаций
    pdf.set_font("Montserrat", "", 12)
    pdf.set_text_color(0, 0, 0)  # Черный

    lines = recommendation_text.split('\n')

    for line in lines:
        if line.startswith('- '):
            # Обработка названия продукта
            product_info = line[2:].split(' (')
            product_name = product_info[0]
            details = product_info[1][:-1] if len(product_info) > 1 else ""

            # Форматирование названия
            formatted_name = ' '.join(
                word.capitalize() for word in product_name.replace('-', ' ').split()
            )

            pdf.set_font("Montserrat", "B", 12)
            pdf.cell(0, 8, f"• {formatted_name}", 0, 1)

            if details:
                pdf.set_font("Montserrat", "", 10)
                pdf.cell(0, 6, f"  {details}", 0, 1)

            pdf.ln(3)
        else:
            pdf.multi_cell(0, 8, line)
            pdf.ln(5)
    # Ссылка на главную страницу
    pdf.ln(10)
    pdf.set_text_color(50, 100, 150)  # Цвет ссылки
    pdf.set_font("Montserrat", "B", 12)
    homepage_url = "http://127.0.0.1:8000"  # <-- Замени на свой URL
    pdf.cell(0, 10, "Вернуться на главную страницу", 0, 1, "C", link=homepage_url)

    # Создаем папку пользователя
    safe_folder_name = user_email.replace('@', '_at_').replace('.', '_')
    user_folder = os.path.join(PDF_FOLDER, safe_folder_name)
    os.makedirs(user_folder, exist_ok=True)

    # Сохраняем PDF
    filename = os.path.join(user_folder, "Cosmetic_Recommendations.pdf")
    pdf.output(filename)

    return filename


# Загружаем конфигурацию из переменных окружения
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Или другой SMTP-сервер
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Обычно 587 для TLS
SMTP_USER = os.getenv("SMTP_USER", "yuliab.890@gmail.com")  # Ваш email
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "picv bcxh xyqn sssf")  # Пароль или App Password
PDF_FOLDER = "generated_pdfs"  # Папка, где хранятся PDF-файлы


def get_email_from_filename(pdf_filename):
    """Извлекает email пользователя из имени файла (например, 'user@example.com.pdf')."""
    return pdf_filename.replace(".pdf", "").replace("_", "@")


@app.task
def send_email(pdf_path):
    """
    Отправляет PDF по email, извлекая адрес из имени папки, в которой лежит файл.
    Пример пути: generated_pdfs/user_at_example_com/Cosmetic recommendation.pdf
    """

    # Извлекаем название папки = закодированный email
    folder_name = os.path.basename(os.path.dirname(pdf_path))

    # Преобразуем в оригинальный email
    recipient = folder_name.replace("_at_", "@").replace("_", ".")

    msg = EmailMessage()
    msg["Subject"] = "Ваши рекомендации по уходу за кожей"
    msg["From"] = SMTP_USER
    msg["To"] = recipient

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return f"Email отправлен: {recipient}"
    except Exception as e:
        return f"Ошибка при отправке: {e}"


@app.task
def send_all_pdfs():
    """Находит все PDF-файлы и отправляет их пользователям."""
    if not os.path.exists(PDF_FOLDER):
        return "Папка с PDF не найдена"

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        return "Нет PDF-файлов для отправки"

    results = []
    for pdf in pdf_files:
        user_email = get_email_from_filename(pdf)  # Получаем email из имени файла
        pdf_path = os.path.join(PDF_FOLDER, pdf)

        result = send_email(pdf_path, user_email)
        results.append(result)

        os.remove(pdf_path)  # Удаляем PDF после отправки

    return results


