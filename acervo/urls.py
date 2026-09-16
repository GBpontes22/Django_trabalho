from django.urls import path

from . import views

app_name = 'acervo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
]

