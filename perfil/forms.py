from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(), label='Senha')
    repassword = forms.CharField(required=False, widget=forms.PasswordInput(), label='Confirmação de senha')

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'repassword', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_msgs = {}
        user_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        repassword_data = cleaned.get('repassword')
        user_db = User.objects.filter(username=user_data).first()
        email_db = User.objects.filter(email=email_data).first()

        if self.usuario:
            if user_db and user_db.username != user_data:
                validation_msgs['username'] = 'Usuário já existe!'

            if email_db and email_db.email != email_data:
                validation_msgs['email'] = 'Email já existe!'

            if password_data:
                if password_data != repassword_data:
                    validation_msgs['password'] = 'As senhas digitadas não conferem!'
                    validation_msgs['repassword'] = 'As senhas digitadas não conferem!'

                if len(password_data) < 6:
                    validation_msgs['password'] = 'Senha precisa ter no mínimo 6 dígitos!'
        else:
            if user_db:
                validation_msgs['username'] = 'Usuário já existe!'

            if email_db:
                validation_msgs['email'] = 'Email já existe!'

            if not password_data:
                validation_msgs['password'] = 'Esse campo é obrigatório!'

            if not repassword_data:
                validation_msgs['repassword'] = 'Esse campo é obrigatório!'

            if password_data != repassword_data:
                validation_msgs['password'] = 'As senhas digitadas não conferem!'
                validation_msgs['repassword'] = 'As senhas digitadas não conferem!'

            if len(password_data) < 6:
                validation_msgs['password'] = 'Senha precisa ter no mínimo 6 dígitos!'

        if validation_msgs:
            raise(forms.ValidationError(validation_msgs))
