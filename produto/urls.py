from django.urls import path
from . import views


app_name = 'produto'

urlpatterns = [
    path('', views.ListarProdutos.as_view(), name='listar'),
    path('pesquisar/', views.PesquisarProdutos.as_view(), name='pesquisar'),
    path('<slug>', views.DetalharProduto.as_view(), name='detalhar'),
    path('adicionaraocarrinho/', views.AdicionarAoCarrinho.as_view(), name='adicionaraocarrinho'),
    path('removerdocarrinho/', views.RemoverDoCarrinho.as_view(), name='removerdocarrinho'),
    path('vercarrinho/', views.VerCarrinho.as_view(), name='vercarrinho'),
    path('resumircompra/', views.ResumirCompra.as_view(), name='resumircompra'),
]
