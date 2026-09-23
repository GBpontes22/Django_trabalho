from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Autor(models.Model):
    nome = models.CharField('nome', max_length=150)
    nacionalidade = models.CharField('nacionalidade', max_length=80, blank=True)
    data_nascimento = models.DateField('data de nascimento', blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.nome


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
        ('500', '500 - Ciencias Puras (Exatas e Naturais)'),
        ('600', '600 - Ciencias Aplicadas (Tecnologia)'),
        ('700', '700 - Artes e Recreacao'),
        ('800', '800 - Literatura'),
        ('900', '900 - Historia e Geografia'),
    ]

    titulo = models.CharField('titulo', max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT,
        related_name='livros',
        verbose_name='autor',
    )
    ano = models.PositiveIntegerField('ano')
    isbn = models.CharField('ISBN', max_length=20, blank=True, null=True, unique=True)
    disponivel = models.BooleanField('ativo no acervo', default=True)
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

    @property
    def disponivel_para_emprestimo(self):
        return self.disponivel and self.exemplares.filter(
            status=Exemplar.STATUS_DISPONIVEL
        ).exists()


class Exemplar(models.Model):
    STATUS_DISPONIVEL = 'disponivel'
    STATUS_EMPRESTADO = 'emprestado'
    STATUS_MANUTENCAO = 'manutencao'
    STATUS_CHOICES = [
        (STATUS_DISPONIVEL, 'Disponivel'),
        (STATUS_EMPRESTADO, 'Emprestado'),
        (STATUS_MANUTENCAO, 'Em manutencao'),
    ]

    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name='exemplares',
        verbose_name='livro',
    )
    codigo = models.CharField('codigo patrimonial', max_length=40, unique=True)
    localizacao = models.CharField('localizacao', max_length=100, blank=True)
    status = models.CharField(
        'status', max_length=12, choices=STATUS_CHOICES, default=STATUS_DISPONIVEL
    )

    class Meta:
        ordering = ['codigo']
        verbose_name = 'exemplar'
        verbose_name_plural = 'exemplares'

    def __str__(self):
        return f'{self.codigo} - {self.livro}'


class Membro(models.Model):
    nome = models.CharField('nome', max_length=150)
    email = models.EmailField('e-mail', unique=True)
    telefone = models.CharField('telefone', max_length=30, blank=True)
    ativo = models.BooleanField('ativo', default=True)
    cadastrado_em = models.DateTimeField('cadastrado em', auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'membro'
        verbose_name_plural = 'membros'

    def __str__(self):
        return self.nome


class Emprestimo(models.Model):
    VALOR_MULTA_DIA = Decimal('1.00')

    exemplar = models.ForeignKey(
        Exemplar,
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name='exemplar',
    )
    membro = models.ForeignKey(
        Membro,
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name='membro',
    )
    emprestado_em = models.DateField('emprestado em', default=timezone.localdate)
    vencimento = models.DateField('vencimento')
    devolvido_em = models.DateField('devolvido em', blank=True, null=True)
    multa = models.DecimalField('multa', max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-emprestado_em', '-id']
        verbose_name = 'emprestimo'
        verbose_name_plural = 'emprestimos'
        constraints = [
            models.UniqueConstraint(
                fields=['exemplar'],
                condition=Q(devolvido_em__isnull=True),
                name='exemplar_com_um_emprestimo_ativo',
            )
        ]

    def __str__(self):
        return f'{self.exemplar} para {self.membro}'

    def clean(self):
        if self.vencimento and self.emprestado_em:
            if self.vencimento < self.emprestado_em:
                raise ValidationError(
                    {'vencimento': 'O vencimento nao pode ser anterior ao emprestimo.'}
                )

    def calcular_multa(self, data_referencia=None):
        referencia = data_referencia or self.devolvido_em or date.today()
        dias_atraso = max((referencia - self.vencimento).days, 0)
        return self.VALOR_MULTA_DIA * dias_atraso

    @property
    def esta_atrasado(self):
        return self.devolvido_em is None and date.today() > self.vencimento


class Reserva(models.Model):
    STATUS_AGUARDANDO = 'aguardando'
    STATUS_ATENDIDA = 'atendida'
    STATUS_CANCELADA = 'cancelada'
    STATUS_CHOICES = [
        (STATUS_AGUARDANDO, 'Aguardando'),
        (STATUS_ATENDIDA, 'Atendida'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='livro',
    )
    membro = models.ForeignKey(
        Membro,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='membro',
    )
    solicitada_em = models.DateTimeField('solicitada em', auto_now_add=True)
    status = models.CharField(
        'status', max_length=10, choices=STATUS_CHOICES, default=STATUS_AGUARDANDO
    )
    finalizada_em = models.DateTimeField('finalizada em', blank=True, null=True)

    class Meta:
        ordering = ['solicitada_em', 'id']
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'
        constraints = [
            models.UniqueConstraint(
                fields=['livro', 'membro'],
                condition=Q(status='aguardando'),
                name='uma_reserva_ativa_por_membro_e_livro',
            )
        ]

    def __str__(self):
        return f'{self.livro} - {self.membro}'

    @property
    def posicao(self):
        if self.status != self.STATUS_AGUARDANDO:
            return None
        return Reserva.objects.filter(
            livro=self.livro,
            status=self.STATUS_AGUARDANDO,
        ).filter(
            Q(solicitada_em__lt=self.solicitada_em)
            | Q(solicitada_em=self.solicitada_em, id__lte=self.id)
        ).count()
