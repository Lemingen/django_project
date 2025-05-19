import mimetypes
import os
import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Docs, UsersToDocs, Price, Cart
import requests
from django.conf import settings

# Create your views here.

def index(request):
    user_docs_ids = UsersToDocs.objects.filter(username=request.user.username).values_list('docs_id', flat=True)
    docs = Docs.objects.filter(id__in=user_docs_ids)
    return render(request, 'db_app/index.html', {'docs': docs})


@login_required
def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        file = request.FILES['image']  # получаем файл

        # путь к файлу внутри media/uploads/
        file_path = os.path.join('uploads', file.name)
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # создаём папку, если нужно
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # сохраняем файл на диск
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # считаем размер в Кб
        size_kb = round(file.size / 1024, 2)

        # записываем в БД
        doc = Docs.objects.create(file_path=file_path, size=size_kb)
        UsersToDocs.objects.create(username=request.user.username, docs_id=doc)

        return redirect('index')  # после загрузки перенаправим на главную

    return render(request, 'db_app/upload.html')  # GET-запрос — отрисовать форму


def analys(request):
    user_docs_ids = UsersToDocs.objects.filter(username=request.user.username).values_list('docs_id', flat=True)
    docs = Docs.objects.filter(id__in=user_docs_ids)

    if request.method == 'POST':
        doc_ids = request.POST.getlist('doc_ids')  # Получаем список выбранных ID

        for doc_id in doc_ids:
            doc = get_object_or_404(Docs, id=doc_id)
            extension = doc.file_path.split('.')[-1]

            # определяем цену
            price_obj = Price.objects.filter(file_type=extension).first()
            if price_obj:
                total_price = doc.size * price_obj.price
            else:
                total_price = 0.0  # если нет цены — 0

            # создаём заказ
            Cart.objects.create(user_id=request.user, docs_id=doc, order_price=total_price)

        return redirect('payment')  # можно перенаправить на оплату

    return render(request, 'db_app/analysis.html', {'docs': docs})



FASTAPI_URL = 'http://localhost:8000'

def payment(request):
    cart_items = Cart.objects.filter(user_id=request.user, payment=False)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('cart_ids')

        for cart_id in selected_ids:
            cart = get_object_or_404(Cart, id=cart_id, user_id=request.user)
            cart.payment = True
            cart.save()

            doc = cart.docs_id
            file_path = os.path.join(settings.MEDIA_ROOT, doc.file_path)  # Полный путь к файлу на диске

            try:
                # Шаг 1: загрузка файла
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'  # fallback

                with open(file_path, 'rb') as f:
                    files = [('files', (os.path.basename(file_path), f, mime_type))]
                    response = requests.post(f'{FASTAPI_URL}/upload_files/', files=files)
                    response.raise_for_status()
                    response_data = response.json()
                    print("Ответ FastAPI:", response_data)  # для отладки

                    # Вместо id_text из ответа FastAPI просто используем ID из Django
                    id_text = str(doc.id)  # или str(doc.pk), если это числовой ID

                    # Теперь вызываем остальные ручки с этим id_text
                    analyse_response = requests.post(f'{FASTAPI_URL}/doc_analyse/{id_text}')
                    analyse_response.raise_for_status()

                    print(f"📨 Документ {doc.id} отправлен на анализ (id_text={id_text})")

                    MAX_RETRIES = 10
                    DELAY_SECONDS = 1

                    for _ in range(MAX_RETRIES):
                        text_response = requests.get(f'{FASTAPI_URL}/get_text/{id_text}')
                        if text_response.status_code == 200:
                            extracted_text = text_response.json().get('text')
                            doc.extracted_text = extracted_text
                            doc.save()
                            break
                        time.sleep(DELAY_SECONDS)
                    else:
                        print("❌ Не удалось получить текст после нескольких попыток")


            except Exception as e:
                print(f"❌ Ошибка при отправке документа {doc.id} на FastAPI: {e}")

        return redirect('payment_result')

    return render(request, 'db_app/payment.html', {'cart_items': cart_items})



def payment_result(request):
    # можно показать только что оплаченные, либо последние
    recent_paid = Cart.objects.filter(user_id=request.user, payment=True).order_by('-id')[:5]
    return render(request, 'db_app/payment_result.html', {'recent_paid': recent_paid})