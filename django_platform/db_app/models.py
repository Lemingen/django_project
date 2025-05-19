from django.db import models
from django.contrib.auth.models import User


#загруженные картинки
class Docs(models.Model):
    file_path = models.CharField(max_length=255)
    size = models.PositiveIntegerField(help_text="Размер файла в Кб")
    extracted_text = models.TextField(null=True, blank=True)

#какой пользователь каую картинку загрузил
class UsersToDocs(models.Model):
    username = models.CharField(max_length=150)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)

class Price(models.Model):
    file_type = models.CharField(max_length=10)
    price = models.FloatField(help_text="Цена за 1 Кб") #анализ 1 Кб данных

#корзина покупателя
class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)