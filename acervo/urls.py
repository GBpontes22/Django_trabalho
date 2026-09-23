from django.urls import path

from . import views

app_name = 'acervo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('painel/', views.dashboard, name='dashboard'),
    path('livros/', views.lista_livros, name='lista'),
    path('livros/novo/', views.novo_livro, name='novo'),
    path('livros/<int:pk>/editar/', views.editar_livro, name='editar_livro'),
    path('livros/<int:pk>/excluir/', views.excluir_livro, name='excluir_livro'),
    path('autores/', views.lista_autores, name='autores'),
    path('autores/novo/', views.novo_autor, name='novo_autor'),
    path('autores/<int:pk>/editar/', views.editar_autor, name='editar_autor'),
    path('autores/<int:pk>/excluir/', views.excluir_autor, name='excluir_autor'),
    path('exemplares/', views.lista_exemplares, name='exemplares'),
    path('exemplares/novo/', views.novo_exemplar, name='novo_exemplar'),
    path('exemplares/<int:pk>/editar/', views.editar_exemplar, name='editar_exemplar'),
    path('exemplares/<int:pk>/excluir/', views.excluir_exemplar, name='excluir_exemplar'),
    path('membros/', views.lista_membros, name='membros'),
    path('membros/novo/', views.novo_membro, name='novo_membro'),
    path('membros/<int:pk>/editar/', views.editar_membro, name='editar_membro'),
    path('membros/<int:pk>/excluir/', views.excluir_membro, name='excluir_membro'),
    path('emprestimos/', views.lista_emprestimos, name='emprestimos'),
    path('emprestimos/novo/', views.novo_emprestimo, name='novo_emprestimo'),
    path('emprestimos/<int:pk>/devolver/', views.devolver_emprestimo, name='devolver_emprestimo'),
    path('reservas/', views.lista_reservas, name='reservas'),
    path('reservas/nova/', views.nova_reserva, name='nova_reserva'),
    path('reservas/<int:pk>/cancelar/', views.cancelar_reserva_view, name='cancelar_reserva'),
]
