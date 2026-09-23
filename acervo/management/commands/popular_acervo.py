from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone

from acervo.models import Autor, Emprestimo, Exemplar, Livro, Membro
from acervo.services import registrar_emprestimo, registrar_reserva


class Command(BaseCommand):
    help = 'Cria dados demonstrativos do P1 de Biblioteca.'

    def handle(self, *args, **options):
        machado, _ = Autor.objects.get_or_create(
            nome='Machado de Assis', defaults={'nacionalidade': 'Brasileira'}
        )
        martin, _ = Autor.objects.get_or_create(
            nome='Robert C. Martin', defaults={'nacionalidade': 'Americana'}
        )

        dom, _ = Livro.objects.get_or_create(
            titulo='Dom Casmurro',
            defaults={
                'autor': machado,
                'ano': 1899,
                'tipo_acervo': Livro.TIPO_FISICO,
                'categoria': '800',
            },
        )
        clean, _ = Livro.objects.get_or_create(
            titulo='Clean Code',
            defaults={
                'autor': martin,
                'ano': 2008,
                'tipo_acervo': Livro.TIPO_DIGITAL,
                'categoria': '600',
            },
        )

        exemplar_dom, _ = Exemplar.objects.get_or_create(
            codigo='DOM-001', defaults={'livro': dom, 'localizacao': 'Estante A1'}
        )
        Exemplar.objects.get_or_create(
            codigo='CLN-DIG-001', defaults={'livro': clean, 'localizacao': 'Online'}
        )

        ana, _ = Membro.objects.get_or_create(
            email='ana@example.com', defaults={'nome': 'Ana Silva'}
        )
        bruno, _ = Membro.objects.get_or_create(
            email='bruno@example.com', defaults={'nome': 'Bruno Lima'}
        )
        carla, _ = Membro.objects.get_or_create(
            email='carla@example.com', defaults={'nome': 'Carla Souza'}
        )

        if not Emprestimo.objects.filter(
            exemplar=exemplar_dom, devolvido_em__isnull=True
        ).exists():
            registrar_emprestimo(
                membro=ana,
                exemplar=exemplar_dom,
                vencimento=timezone.localdate() + timedelta(days=14),
            )

        for membro in (bruno, carla):
            try:
                registrar_reserva(membro=membro, livro=dom)
            except ValidationError:
                pass

        self.stdout.write(self.style.SUCCESS('Dados demonstrativos criados.'))
