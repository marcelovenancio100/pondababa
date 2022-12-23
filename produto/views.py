from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib import messages
from django.db.models import Q
from . import models
from perfil.models import Perfil


class ListarProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 6
    ordering = ['-id']


class PesquisarProdutos(ListarProdutos):
    def get_queryset(self, *args, **kwargs):
        filter = self.request.GET.get('filter') or self.request.session.get('filter')
        qs = super().get_queryset(*args, **kwargs)

        if not filter:
            return qs

        self.request.session['filter'] = filter

        qs = qs.filter(
            Q(nome__icontains=filter) |
            Q(descricao_curta__icontains=filter) |
            Q(descricao_longa__icontains=filter)
        )

        self.request.session.save()
        return qs


class DetalharProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get('HTTP_REFERER', reverse('produto:listar'))
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(self.request, 'Produto não existe!')
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)

        if variacao.estoque < 1:
            messages.error(self.request, 'Produto indisponível no estoque!')
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao.estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque indisponível para {quantidade_carrinho}x no produto {variacao.produto.nome}.'
                    f'Adicionamos {variacao.estoque}x ao seu carrinho.'
                )
                quantidade_carrinho = variacao.estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_total'] = variacao.preco * quantidade_carrinho
            carrinho[variacao_id]['preco_total_promocional'] = variacao.preco_promocional * quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                'produto_id': variacao.produto.id,
                'produto_nome': variacao.produto.nome,
                'variacao_id': variacao.id,
                'variacao_nome': variacao.nome or '',
                'preco_unitario': variacao.preco,
                'preco_unitario_promocional': variacao.preco_promocional,
                'preco_total': variacao.preco,
                'preco_total_promocional': variacao.preco_promocional,
                'quantidade': 1,
                'slug': variacao.produto.slug,
                'imagem': variacao.produto.imagem.name if variacao.produto.imagem else '',
            }

        self.request.session.save()
        messages.success(self.request, f'Produto {variacao.produto.nome} {variacao.nome} adicionado ao seu carrinho!')
        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get('HTTP_REFERER', reverse('produto:listar'))
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]

        messages.success(
            self.request,
            f'O produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} '
            f'foi removido com sucesso do seu carrinho!'
        )

        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)


class VerCarrinho(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'produto/carrinho.html')


class ResumirCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        if not Perfil.objects.filter(usuario=self.request.user).exists():
            messages.error(self.request, 'Usuário não possui perfil cadastrado para compra!')
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.warning(self.request, 'Seu carrinho está vazio!')
            return redirect('produto:listar')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho']
        }

        return render(self.request, 'produto/resumo.html', contexto)
