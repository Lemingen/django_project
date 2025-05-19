from django.test import SimpleTestCase
from django.urls import reverse, resolve
from db_app.views import index, upload, analys, payment, payment_result

class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, index)

    def test_upload_url_resolves(self):
        url = reverse('upload_file')
        self.assertEqual(resolve(url).func, upload)

    def test_analys_url_resolves(self):
        url = reverse('order_analysis')
        self.assertEqual(resolve(url).func, analys)

    def test_payment_url_resolves(self):
        url = reverse('payment')
        self.assertEqual(resolve(url).func, payment)

    def test_payment_result_url_resolves(self):
        url = reverse('payment_result')
        self.assertEqual(resolve(url).func, payment_result)
