from django.urls import path
from . import views


app_name = 'pedido'

urlpatterns = [
    path('salvar/', views.Salvar.as_view(), name='salvar'),
    path('pagar/<int:pk>', views.Pagar.as_view(), name='pagar'),
    path('listar/', views.Listar.as_view(), name='listar'),
    path('detalhar/<int:pk>', views.Detalhar.as_view(), name='detalhar'),
]
