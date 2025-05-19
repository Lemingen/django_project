import tempfile
import time
from unittest import mock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from db_app.views import FASTAPI_URL


class PaymentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    @mock.patch('db_app.views.Cart.objects.filter')
    @mock.patch('db_app.views.get_object_or_404')
    @mock.patch('db_app.views.requests.post')
    @mock.patch('db_app.views.requests.get')
    @mock.patch('db_app.views.open', new_callable=mock.mock_open, read_data=b'dummy')
    @mock.patch('db_app.views.mimetypes.guess_type')
    @mock.patch('db_app.views.time.sleep', return_value=None)  # чтобы не задерживалось
    def test_payment_post_marks_cart_and_sends_to_fastapi(
        self, mock_sleep, mock_guess_type, mock_open,
        mock_requests_get, mock_requests_post,
        mock_get_object, mock_cart_filter
    ):
        # Настраиваем моки
        mock_cart = mock.Mock()
        mock_doc = mock.Mock(id=1, file_path='doc.pdf')
        mock_cart.docs_id = mock_doc
        mock_cart.id = 123
        mock_cart_filter.return_value = [mock_cart]
        mock_get_object.return_value = mock_cart

        mock_guess_type.return_value = ('application/pdf', None)

        mock_requests_post.return_value.status_code = 200
        mock_requests_post.return_value.json.return_value = {'success': True}

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {'text': 'Extracted text'}

        # Отправляем POST-запрос
        response = self.client.post(reverse('payment'), data={'cart_ids': ['123']})

        # Проверяем редирект
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payment_result'))

        # Проверки вызовов
        mock_cart_filter.assert_called_with(user_id=self.user, payment=False)
        mock_get_object.assert_called_with(mock.ANY, id='123', user_id=self.user)
        mock_open.assert_called()  # файл был открыт
        mock_requests_post.assert_any_call(mock.ANY, files=mock.ANY)
        mock_requests_post.assert_any_call(f'{FASTAPI_URL}/doc_analyse/1')
        mock_requests_get.assert_called_with(f'{FASTAPI_URL}/get_text/1')

        mock_doc.save.assert_called_once()
