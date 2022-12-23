from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from produto.models import Variacao
from . models import Pedido, ItemPedido
from utils import functions


class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class Salvar(View):
    template_name = 'pedido/pagamento.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Você precisa fazer login!')
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(self.request, 'Seu carrinho está vazio!')
            return redirect('produto:listar')

        carrinho = self.request.session.get('carrinho')
        variacoes_ids = [v for v in carrinho]
        variacoes_db = list(Variacao.objects.select_related('produto').filter(id__in=variacoes_ids))

        for variacao in variacoes_db:
            vid = str(variacao.id)
            qtd_estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            msg_error = ''

            if qtd_estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = qtd_estoque
                carrinho[vid]['preco_total'] = qtd_estoque * carrinho[vid]['preco_unitario']
                carrinho[vid]['preco_total_promocional'] = qtd_estoque * carrinho[vid]['preco_unitario_promocional']

                msg_error = 'Estoque indisponível para alguns itens do seu carrinho. '\
                            'Reduzimos a quantidade desses itens para o total em estoque. '\
                            'Por favor, verifique seu carrinho antes de prosseguir.'

            if msg_error:
                messages.error(self.request, msg_error)
                self.request.session.save()
                return redirect('produto:vercarrinho')

        pedido = Pedido(
            usuario=self.request.user,
            quantidade=functions.soma_qtde_carrinho(carrinho),
            total=functions.soma_carrinho(carrinho),
            status='C'
        )

        pedido.save()

        ItemPedido.objects.bulk_create([
            ItemPedido(
                pedido=pedido,
                produto=value['produto_nome'],
                produto_id=value['produto_id'],
                variacao=value['variacao_nome'],
                variacao_id=value['variacao_id'],
                preco=value['preco_total'],
                preco_promocional=value['preco_total_promocional'],
                quantidade=value['quantidade'],
                imagem=value['imagem'],
            ) for value in carrinho.values()
        ])

        del self.request.session['carrinho']
        return redirect(reverse('pedido:pagar', kwargs={'pk': pedido.pk}))


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagamento.html'
    model = Pedido
    context_object_name = 'pedido'
    pk_url_kwarg = 'pk'


class Listar(DispatchLoginRequiredMixin, ListView):
    template_name = 'pedido/lista.html'
    model = Pedido
    context_object_name = 'pedidos'
    paginate_by = 8
    ordering = ['-id']


class Detalhar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/detalhe.html'
    model = Pedido
    context_object_name = 'pedido'
    pk_url_kwarg = 'pk'
