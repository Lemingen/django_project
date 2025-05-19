import tempfile
from unittest import mock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from db_app.models import Docs, UsersToDocs

class UploadViewTests(TestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    @mock.patch('db_app.views.open', new_callable=mock.mock_open)
    @mock.patch('db_app.views.os.makedirs')
    @mock.patch('db_app.views.Docs.objects.create')
    @mock.patch('db_app.views.UsersToDocs.objects.create')
    def test_upload_post(self, mock_userdoc_create, mock_doc_create, mock_makedirs, mock_open):
        # Создаём тестового пользователя и логинимся
        self.client.login(username='testuser', password='testpass')

        # Подготавливаем файл для загрузки
        file = SimpleUploadedFile('test.jpg', b'test image content', content_type='image/jpeg')

        # Выполняем POST-запрос
        response = self.client.post(reverse('upload_file'), {'image': file})

        # Проверяем редирект после успешной загрузки
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        # Проверяем, что была попытка создать объект Docs
        self.assertTrue(mock_doc_create.called)
        # Проверяем, что была попытка создать UsersToDocs
        self.assertTrue(mock_userdoc_create.called)

        # Проверяем, что папка создавалась
        mock_makedirs.assert_called()

        # Проверяем, что файл "сохранялся" (вызывался open и write)
        mock_open.assert_called()

    def setUp(self):
        # Создаём пользователя для логина
        from django.contrib.auth.models import User
        User.objects.create_user(username='testuser', password='testpass')
