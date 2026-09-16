from django.urls import path

from . import views

app_name = 'acervo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('livros/', views.lista_livros, name='lista'),
    path('livros/novo/', views.novo_livro, name='novo'),
]
