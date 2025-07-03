from celery import chain
from .tasks import calculate_skin_type, select_products, generate_pdf, collect_user_answers, send_email

def run_task_chain(answers,user_email,user_id):
    task_chain = chain(
        calculate_skin_type.s(answers) |
        select_products.s(user_id=user_id) |
        generate_pdf.s(user_email=user_email) |
        send_email.s()
    )
    result = task_chain.apply_async()
    return result

def main():
    # Тут collect_user_answers - CLI, в Django не нужен
    answers = collect_user_answers()  # Только если запускаешь из командной строки
    result = run_task_chain(answers)
    print("Обработка завершена. Результат:")
    pdf_filename = result.get()
    print(f"PDF-файл сохранен: {pdf_filename}")

if __name__ == "__main__":
    main()
