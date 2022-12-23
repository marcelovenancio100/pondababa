from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . import models
from . import forms
import copy


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.carrinho = None
        self.perfil = None
        self.contexto = None
        self.renderizar = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'
            self.perfil = models.Perfil.objects.filter(usuario=self.request.user).first()

        self.contexto = {
            'userform':
                forms.UserForm(data=self.request.POST or None, usuario=self.request.user, instance=self.request.user)
                if self.request.user.is_authenticated
                else forms.UserForm(data=self.request.POST or None),
            'perfilform': forms.PerfilForm(data=self.request.POST or None, instance=self.perfil)
                if self.request.user.is_authenticated
                else forms.PerfilForm(data=self.request.POST or None),
        }

        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        userform = self.contexto['userform']
        perfilform = self.contexto['perfilform']

        if not userform.is_valid() or not perfilform.is_valid():
            messages.error(
                self.request,
                'Alguns problemas foram encontrados em seu cadastro. Verifique os campos e tente novamente!'
            )
            return self.renderizar

        username = userform.cleaned_data.get('username')
        password = userform.cleaned_data.get('password')
        email = userform.cleaned_data.get('email')
        first_name = userform.cleaned_data.get('first_name')
        last_name = userform.cleaned_data.get('last_name')

        if self.request.user.is_authenticated:
            usuario = get_object_or_404(User, username=self.request.user.username)
            usuario.username = username

            if password:
                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:
                perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**perfilform.cleaned_data)
            else:
                perfil = perfilform.save(commit=False)
                perfil.usuario = usuario

            perfil.save()
        else:
            usuario = userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        if password:
            autentica = authenticate(self.request, username=username, password=password)

            if autentica:
                login(self.request, user=usuario)

        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        messages.success(self.request, 'Cadastro atualizado com sucesso!')
        return redirect('produto:vercarrinho')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        print(username, password)

        if not username or not password:
            messages.error(self.request, 'Usuário ou senha inválidos!')
            return redirect('perfil:criar')

        usuario = authenticate(self.request, username=username, password=password)

        if not usuario:
            messages.error(self.request, 'Usuário ou senha inválidos!')
            return redirect('perfil:criar')

        login(self.request, user=usuario)
        return redirect('produto:vercarrinho')


class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))

        logout(self.request)

        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect('produto:listar')
