from django.db import models


class Livro(models.Model):
    TIPOS_ACERVO = [
        ("DIGITAL", "Digital"),
        ("FISICO", "Físico"),
    ]

    CATEGORIAS = [
        ("000", "000 – Generalidades e Informação"),
        ("100", "100 – Filosofia e Psicologia"),
        ("200", "200 – Religião e Teologia"),
        ("300", "300 – Ciências Sociais e Direito"),
        ("400", "400 – Linguística e Idiomas"),
        ("500", "500 – Ciências Puras (Exatas e Naturais)"),
        ("600", "600 – Ciências Aplicadas (Tecnologia)"),
        ("700", "700 – Artes e Recreação"),
        ("800", "800 – Literatura"),
        ("900", "900 – História e Geografia"),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    ano = models.IntegerField()
    disponivel = models.BooleanField(default=True)
    tipo_acervo = models.CharField(max_length=10, choices=TIPOS_ACERVO)
    categoria = models.CharField(max_length=3, choices=CATEGORIAS)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["titulo"]
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
