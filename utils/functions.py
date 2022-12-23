def formata_preco(value):
    return f'R$ {value:.2f}'.replace('.', ',')


def soma_qtde_carrinho(carrinho):
    return sum([item['quantidade'] for item in carrinho.values()])


def soma_carrinho(carrinho):
    return sum([
        item.get('preco_total_promocional') if item.get('preco_total_promocional') else item.get('preco_total')
        for item in carrinho.values()
    ])
