from django.urls import path
from . import views
from .views import payment

urlpatterns = [
    path('', views.index, name = 'index'),
    path('upload/', views.upload, name='upload_file'),
    path('analys/', views.analys, name='order_analysis'),
    path('payment/', views.payment, name='payment'),
    path('payment_result/', views.payment_result, name='payment_result'),
]

