from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Autor, Emprestimo, Exemplar, Livro, Membro, Reserva
from .services import (
    cancelar_reserva,
    registrar_devolucao,
    registrar_emprestimo,
    registrar_reserva,
)


class AcervoBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.machado = Autor.objects.create(nome='Machado de Assis')
        cls.martin = Autor.objects.create(nome='Robert C. Martin')
        cls.dom_casmurro = Livro.objects.create(
            titulo='Dom Casmurro',
            autor=cls.machado,
            ano=1899,
            tipo_acervo=Livro.TIPO_FISICO,
            categoria='800',
        )
        cls.clean_code = Livro.objects.create(
            titulo='Clean Code',
            autor=cls.martin,
            ano=2008,
            tipo_acervo=Livro.TIPO_DIGITAL,
            categoria='600',
        )
        cls.exemplar = Exemplar.objects.create(
            livro=cls.dom_casmurro,
            codigo='DOM-001',
            localizacao='A1',
        )
        cls.exemplar_digital = Exemplar.objects.create(
            livro=cls.clean_code,
            codigo='DIG-001',
        )
        cls.ana = Membro.objects.create(nome='Ana Silva', email='ana@example.com')
        cls.bruno = Membro.objects.create(nome='Bruno Lima', email='bruno@example.com')


class LivroViewsTests(AcervoBaseTestCase):
    def test_lista_exibe_tipo_categoria_autor_e_exemplares(self):
        response = self.client.get(reverse('acervo:lista'))
        self.assertContains(response, 'Dom Casmurro')
        self.assertContains(response, 'Machado de Assis')
        self.assertContains(response, '800 - Literatura')
        self.assertContains(response, 'Fisico')

    def test_pesquisa_por_nome_ou_autor(self):
        response = self.client.get(reverse('acervo:lista'), {'q': 'Machado'})
        self.assertContains(response, 'Dom Casmurro')
        self.assertNotContains(response, 'Clean Code')

    def test_pesquisa_por_tipo(self):
        response = self.client.get(
            reverse('acervo:lista'), {'tipo': Livro.TIPO_DIGITAL}
        )
        self.assertContains(response, 'Clean Code')
        self.assertNotContains(response, 'Dom Casmurro')

    def test_pesquisa_por_categoria(self):
        response = self.client.get(reverse('acervo:lista'), {'categoria': '800'})
        self.assertContains(response, 'Dom Casmurro')
        self.assertNotContains(response, 'Clean Code')

    def test_filtro_por_disponivel(self):
        self.exemplar.status = Exemplar.STATUS_EMPRESTADO
        self.exemplar.save(update_fields=['status'])
        response = self.client.get(
            reverse('acervo:lista'), {'status': Exemplar.STATUS_DISPONIVEL}
        )
        self.assertContains(response, 'Clean Code')
        self.assertNotContains(response, 'Dom Casmurro')

    def test_filtro_por_emprestado(self):
        self.exemplar.status = Exemplar.STATUS_EMPRESTADO
        self.exemplar.save(update_fields=['status'])
        response = self.client.get(
            reverse('acervo:lista'), {'status': Exemplar.STATUS_EMPRESTADO}
        )
        self.assertContains(response, 'Dom Casmurro')
        self.assertNotContains(response, 'Clean Code')

    def test_busca_e_status_funcionam_juntos(self):
        self.exemplar.status = Exemplar.STATUS_EMPRESTADO
        self.exemplar.save(update_fields=['status'])
        response = self.client.get(
            reverse('acervo:lista'),
            {'q': 'Machado', 'status': Exemplar.STATUS_EMPRESTADO},
        )
        self.assertContains(response, 'Dom Casmurro')
        self.assertNotContains(response, 'Clean Code')

    def test_busca_preserva_termo_e_exibe_mensagem_sem_resultado(self):
        response = self.client.get(reverse('acervo:lista'), {'q': 'Inexistente'})
        self.assertContains(response, 'value="Inexistente"', html=False)
        self.assertContains(response, 'Nenhum livro encontrado.')

    def test_cadastro_cria_livro_relacionado_ao_autor(self):
        response = self.client.post(
            reverse('acervo:novo'),
            {
                'titulo': 'O Principe',
                'autor': self.machado.pk,
                'ano': 1532,
                'tipo_acervo': Livro.TIPO_DIGITAL,
                'categoria': '300',
                'disponivel': 'on',
            },
        )
        self.assertRedirects(response, reverse('acervo:lista'))
        livro = Livro.objects.get(titulo='O Principe')
        self.assertEqual(livro.autor, self.machado)

    def test_edicao_e_exclusao_de_livro(self):
        response = self.client.post(
            reverse('acervo:editar_livro', args=[self.clean_code.pk]),
            {
                'titulo': 'Codigo Limpo',
                'autor': self.martin.pk,
                'ano': 2008,
                'tipo_acervo': Livro.TIPO_DIGITAL,
                'categoria': '600',
                'disponivel': 'on',
            },
        )
        self.assertRedirects(response, reverse('acervo:lista'))
        self.clean_code.refresh_from_db()
        self.assertEqual(self.clean_code.titulo, 'Codigo Limpo')

        self.exemplar_digital.delete()
        response = self.client.post(
            reverse('acervo:excluir_livro', args=[self.clean_code.pk])
        )
        self.assertRedirects(response, reverse('acervo:lista'))
        self.assertFalse(Livro.objects.filter(pk=self.clean_code.pk).exists())


class EmprestimoServiceTests(AcervoBaseTestCase):
    def test_emprestimo_altera_status_do_exemplar(self):
        emprestimo = registrar_emprestimo(
            membro=self.ana,
            exemplar=self.exemplar,
            vencimento=timezone.localdate() + timedelta(days=14),
        )
        self.exemplar.refresh_from_db()
        self.assertEqual(self.exemplar.status, Exemplar.STATUS_EMPRESTADO)
        self.assertIsNone(emprestimo.devolvido_em)

    def test_exemplar_nao_pode_ser_emprestado_duas_vezes(self):
        registrar_emprestimo(
            membro=self.ana,
            exemplar=self.exemplar,
            vencimento=timezone.localdate() + timedelta(days=14),
        )
        with self.assertRaises(ValidationError):
            registrar_emprestimo(
                membro=self.bruno,
                exemplar=self.exemplar,
                vencimento=timezone.localdate() + timedelta(days=14),
            )

    def test_devolucao_calcula_multa_e_libera_exemplar(self):
        hoje = timezone.localdate()
        emprestimo = registrar_emprestimo(
            membro=self.ana,
            exemplar=self.exemplar,
            vencimento=hoje + timedelta(days=7),
        )
        Emprestimo.objects.filter(pk=emprestimo.pk).update(
            emprestado_em=hoje - timedelta(days=10),
            vencimento=hoje - timedelta(days=3),
        )
        emprestimo.refresh_from_db()
        emprestimo = registrar_devolucao(
            emprestimo=emprestimo, data_devolucao=hoje
        )
        self.exemplar.refresh_from_db()
        self.assertEqual(emprestimo.multa, Decimal('3.00'))
        self.assertEqual(self.exemplar.status, Exemplar.STATUS_DISPONIVEL)

    def test_membro_inativo_nao_pode_emprestar(self):
        self.ana.ativo = False
        self.ana.save(update_fields=['ativo'])
        with self.assertRaises(ValidationError):
            registrar_emprestimo(
                membro=self.ana,
                exemplar=self.exemplar,
                vencimento=timezone.localdate() + timedelta(days=14),
            )

    def test_view_registra_emprestimo_e_devolucao(self):
        response = self.client.post(
            reverse('acervo:novo_emprestimo'),
            {
                'membro': self.ana.pk,
                'exemplar': self.exemplar.pk,
                'vencimento': timezone.localdate() + timedelta(days=7),
            },
        )
        self.assertRedirects(response, reverse('acervo:emprestimos'))
        emprestimo = Emprestimo.objects.get(exemplar=self.exemplar)
        response = self.client.post(
            reverse('acervo:devolver_emprestimo', args=[emprestimo.pk])
        )
        self.assertRedirects(response, reverse('acervo:emprestimos'))
        emprestimo.refresh_from_db()
        self.assertIsNotNone(emprestimo.devolvido_em)


class ReservaServiceTests(AcervoBaseTestCase):
    def setUp(self):
        registrar_emprestimo(
            membro=self.ana,
            exemplar=self.exemplar,
            vencimento=timezone.localdate() + timedelta(days=14),
        )

    def test_reservas_formam_fila_fifo(self):
        primeira = registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)
        carlos = Membro.objects.create(nome='Carlos', email='carlos@example.com')
        segunda = registrar_reserva(membro=carlos, livro=self.dom_casmurro)
        self.assertEqual(primeira.posicao, 1)
        self.assertEqual(segunda.posicao, 2)

    def test_membro_fora_do_inicio_da_fila_nao_recebe_exemplar(self):
        primeira = registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)
        registrar_devolucao(emprestimo=Emprestimo.objects.get(exemplar=self.exemplar))
        with self.assertRaises(ValidationError):
            registrar_emprestimo(
                membro=self.ana,
                exemplar=self.exemplar,
                vencimento=timezone.localdate() + timedelta(days=7),
            )
        primeira.refresh_from_db()
        self.assertEqual(primeira.status, Reserva.STATUS_AGUARDANDO)

    def test_primeiro_da_fila_recebe_exemplar_e_reserva_e_atendida(self):
        reserva = registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)
        registrar_devolucao(emprestimo=Emprestimo.objects.get(exemplar=self.exemplar))
        registrar_emprestimo(
            membro=self.bruno,
            exemplar=self.exemplar,
            vencimento=timezone.localdate() + timedelta(days=7),
        )
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Reserva.STATUS_ATENDIDA)

    def test_reserva_duplicada_e_impedida(self):
        registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)
        with self.assertRaises(ValidationError):
            registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)

    def test_cancelamento_remove_reserva_da_fila(self):
        reserva = registrar_reserva(membro=self.bruno, livro=self.dom_casmurro)
        cancelar_reserva(reserva=reserva)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Reserva.STATUS_CANCELADA)
        self.assertIsNone(reserva.posicao)


class DashboardTests(AcervoBaseTestCase):
    def test_dashboard_exibe_indicadores(self):
        response = self.client.get(reverse('acervo:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Painel da biblioteca')
        self.assertContains(response, 'Emprestimos ativos')
