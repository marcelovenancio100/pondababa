from django.db import models
from PIL import Image
from django.conf import settings
from django.utils.text import slugify
import os
from utils import functions


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(upload_to='produto_imagens/%Y/%m', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField()
    preco_marketing_promocional = models.FloatField(default=0)
    tipo = models.CharField(default='V', max_length=1, choices=(
        ('V', 'Variável'),
        ('S', 'Simples')
    ))

    def get_preco_marketing_formatado(self):
        return functions.formata_preco(self.preco_marketing)
    get_preco_marketing_formatado.short_description = 'Preço'

    def get_preco_marketing_promocional_formatado(self):
        return functions.formata_preco(self.preco_marketing_promocional)
    get_preco_marketing_promocional_formatado.short_description = 'Preço promocional'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{slugify(self.nome)}'

        super().save(*args, **kwargs)

        if self.imagem:
            self.resize_image(self.imagem, 800)

    @staticmethod
    def resize_image(image, new_width=800):
        image_full_path = os.path.join(settings.MEDIA_ROOT, image.name)
        image_pil = Image.open(image_full_path)
        width, height = image_pil.size

        if width <= new_width:
            image_pil.close()
            return

        new_height = round((new_width * height) / width)
        new_image = image_pil.resize((new_width, new_height), Image.LANCZOS)
        new_image.save(
            image_full_path,
            optimize=True,
            quality=60
        )


class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
