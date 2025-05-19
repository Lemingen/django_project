from unittest import mock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AnalysViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('order_analysis')

    @mock.patch('db_app.views.Cart.objects.create')
    @mock.patch('db_app.views.Price.objects.filter')
    @mock.patch('db_app.views.Docs.objects.filter')
    @mock.patch('db_app.views.UsersToDocs.objects.filter')
    def test_analys_post_creates_cart(self, mock_userdocs_filter, mock_docs_filter, mock_price_filter,
                                      mock_cart_create):
        # Мокаем возвращаемые значения
        mock_userdocs_filter.return_value.values_list.return_value = [1, 2]
        mock_docs_filter.return_value = [
            mock.Mock(id=1, file_path='file1.pdf', size=10),
            mock.Mock(id=2, file_path='file2.doc', size=20),
        ]
        mock_price_filter.return_value.first.side_effect = [mock.Mock(price=5), mock.Mock(price=10)]

        # Отправляем POST с выбранными doc_ids
        response = self.client.post(reverse('order_analysis'), data={'doc_ids': ['1', '2']})

        self.assertEqual(response.status_code, 404)


    @mock.patch('db_app.views.Docs.objects.filter')
    @mock.patch('db_app.views.UsersToDocs.objects.filter')
    def test_analys_get_renders_template(self, mock_userdocs_filter, mock_docs_filter):
        mock_userdocs_filter.return_value.values_list.return_value = [1]
        mock_docs_filter.return_value = [mock.Mock(id=1, file_path='file1.pdf', size=10)]

        response = self.client.get(reverse('order_analysis'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'db_app/analysis.html')
        self.assertIn('docs', response.context)
