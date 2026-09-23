from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Emprestimo, Exemplar, Reserva


@transaction.atomic
def registrar_emprestimo(*, membro, exemplar, vencimento):
    exemplar = Exemplar.objects.select_for_update().select_related('livro').get(
        pk=exemplar.pk
    )

    if not membro.ativo:
        raise ValidationError('O membro selecionado esta inativo.')
    if exemplar.status != Exemplar.STATUS_DISPONIVEL:
        raise ValidationError('Este exemplar nao esta disponivel.')

    primeira_reserva = (
        Reserva.objects.select_for_update()
        .filter(livro=exemplar.livro, status=Reserva.STATUS_AGUARDANDO)
        .order_by('solicitada_em', 'id')
        .first()
    )
    if primeira_reserva and primeira_reserva.membro_id != membro.pk:
        raise ValidationError(
            'Este livro esta reservado para o primeiro membro da fila.'
        )

    emprestimo = Emprestimo(
        membro=membro,
        exemplar=exemplar,
        vencimento=vencimento,
    )
    emprestimo.full_clean()
    emprestimo.save()

    exemplar.status = Exemplar.STATUS_EMPRESTADO
    exemplar.save(update_fields=['status'])

    if primeira_reserva:
        primeira_reserva.status = Reserva.STATUS_ATENDIDA
        primeira_reserva.finalizada_em = timezone.now()
        primeira_reserva.save(update_fields=['status', 'finalizada_em'])

    return emprestimo


@transaction.atomic
def registrar_devolucao(*, emprestimo, data_devolucao=None):
    emprestimo = Emprestimo.objects.select_for_update().select_related(
        'exemplar'
    ).get(pk=emprestimo.pk)
    if emprestimo.devolvido_em:
        raise ValidationError('Este emprestimo ja foi devolvido.')

    emprestimo.devolvido_em = data_devolucao or timezone.localdate()
    emprestimo.multa = emprestimo.calcular_multa(emprestimo.devolvido_em)
    emprestimo.save(update_fields=['devolvido_em', 'multa'])

    emprestimo.exemplar.status = Exemplar.STATUS_DISPONIVEL
    emprestimo.exemplar.save(update_fields=['status'])
    return emprestimo


@transaction.atomic
def registrar_reserva(*, membro, livro):
    if not membro.ativo:
        raise ValidationError('O membro selecionado esta inativo.')
    if livro.exemplares.filter(status=Exemplar.STATUS_DISPONIVEL).exists():
        raise ValidationError(
            'Ha exemplar disponivel; realize o emprestimo em vez da reserva.'
        )
    if Reserva.objects.filter(
        livro=livro,
        membro=membro,
        status=Reserva.STATUS_AGUARDANDO,
    ).exists():
        raise ValidationError('Este membro ja esta na fila deste livro.')
    return Reserva.objects.create(livro=livro, membro=membro)


@transaction.atomic
def cancelar_reserva(*, reserva):
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.status != Reserva.STATUS_AGUARDANDO:
        raise ValidationError('Somente reservas em espera podem ser canceladas.')
    reserva.status = Reserva.STATUS_CANCELADA
    reserva.finalizada_em = timezone.now()
    reserva.save(update_fields=['status', 'finalizada_em'])
    return reserva
