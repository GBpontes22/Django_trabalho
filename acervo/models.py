from django.db import models


class Livro(models.Model):
    TIPO_DIGITAL = 'digital'
    TIPO_FISICO = 'fisico'

    TIPO_ACERVO_CHOICES = [
        (TIPO_DIGITAL, 'Digital'),
        (TIPO_FISICO, 'Fisico'),
    ]

    CATEGORIA_CHOICES = [
        ('000', '000 - Generalidades e Informacao'),
        ('100', '100 - Filosofia e Psicologia'),
        ('200', '200 - Religiao e Teologia'),
        ('300', '300 - Ciencias Sociais e Direito'),
        ('400', '400 - Linguistica e Idiomas'),
        ('500', '500 - Ciencias Puras'),
        ('600', '600 - Ciencias Aplicadas'),
        ('700', '700 - Artes e Recreacao'),
        ('800', '800 - Literatura'),
        ('900', '900 - Historia e Geografia'),
    ]

    titulo = models.CharField('titulo', max_length=200)
    autor = models.CharField('autor', max_length=100)
    ano = models.PositiveIntegerField('ano')
    disponivel = models.BooleanField('disponivel', default=True)
    tipo_acervo = models.CharField(
        'tipo de acervo',
        max_length=10,
        choices=TIPO_ACERVO_CHOICES,
        default=TIPO_FISICO,
    )
    categoria = models.CharField(
        'categoria',
        max_length=3,
        choices=CATEGORIA_CHOICES,
        default='000',
    )

    class Meta:
        ordering = ['titulo']
        verbose_name = 'livro'
        verbose_name_plural = 'livros'

    def __str__(self):
        return self.titulo

# Create your models here.
