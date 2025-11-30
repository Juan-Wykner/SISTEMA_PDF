from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Pessoas, Classificacao
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for i in range(1,101):
                Pessoas.objects.get_or_create(
                    tipo='CLIENTE',
                    razao_social=f'Cliente {i}',
                    cnpj_cpf=f'{i:011d}',
                    defaults={'ativo':True}
                )
            for i in range(1,101):
                Pessoas.objects.get_or_create(
                    tipo='FORNECEDOR',
                    razao_social=f'Fornecedor {i}',
                    cnpj_cpf=f'{10000000000+i}',
                    defaults={'ativo':True}
                )
            for i in range(1,21):
                Classificacao.objects.get_or_create(
                    tipo='DESPESA',
                    descricao=f'Despesa {i}',
                    defaults={'ativo':True}
                )
            for i in range(1,21):
                Classificacao.objects.get_or_create(
                    tipo='RECEITA',
                    descricao=f'Receita {i}',
                    defaults={'ativo':True}
                )
