from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Livro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=200)),
                ("autor", models.CharField(max_length=100)),
                ("ano", models.IntegerField()),
                ("disponivel", models.BooleanField(default=True)),
                ("tipo_acervo", models.CharField(choices=[("DIGITAL", "Digital"), ("FISICO", "Físico")], max_length=10)),
                ("categoria", models.CharField(choices=[
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
                ], max_length=3)),
            ],
            options={
                "verbose_name": "Livro",
                "verbose_name_plural": "Livros",
                "ordering": ["titulo"],
            },
        ),
    ]
