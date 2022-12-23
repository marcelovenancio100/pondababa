from django.template import Library
from utils import functions

register = Library()


@register.filter
def formata_preco(value):
    return functions.formata_preco(value)


@register.filter
def soma_qtde_carrinho(carrinho):
    return functions.soma_qtde_carrinho(carrinho)


@register.filter
def soma_carrinho(carrinho):
    return functions.soma_carrinho(carrinho)
