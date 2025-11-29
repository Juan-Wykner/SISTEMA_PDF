from django.db import models
from django.core.validators import MinValueValidator

class Pessoas(models.Model):
    """
    Model para armazenar pessoas (fornecedores, clientes, faturados)
    Implementa a regra de negócio: cadastros não podem ser excluídos, apenas inativados
    """
    TIPO_CHOICES = [
        ('CLIENTE', 'Cliente'),
        ('FORNECEDOR', 'Fornecedor'),
        ('FATURADO', 'Faturado'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo da pessoa: Cliente, Fornecedor ou Faturado")
    razao_social = models.CharField(max_length=200, help_text="Razão social ou nome completo")
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True, help_text="Nome fantasia (opcional)")
    cnpj_cpf = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="CNPJ ou CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True, help_text="Endereço completo")
    ativo = models.BooleanField(default=True, help_text="Indica se o cadastro está ativo ou inativo")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data da última atualização")
    
    class Meta:
        db_table = 'pessoas'
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        
    def __str__(self):
        return f"{self.razao_social}"
    
    def inativar(self):
        """Método para inativar um cadastro (regra de negócio)"""
        self.ativo = False
        self.save()
    
    def reativar(self):
        """Método para reativar um cadastro inativo (regra de negócio)"""
        self.ativo = True
        self.save()


class Classificacao(models.Model):
    """
    Model para tipos de receitas e despesas
    Usado para classificar os movimentos financeiros
    """
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo: Receita ou Despesa")
    descricao = models.CharField(max_length=100, help_text="Descrição da classificação")
    ativo = models.BooleanField(default=True, help_text="Indica se a classificação está ativa")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'classificacao'
        verbose_name = 'Classificação'
        verbose_name_plural = 'Classificações'
        
    def __str__(self):
        return self.descricao


class MovimentoContas(models.Model):
    """
    Model para movimentos de contas a pagar/receber
    Implementa parcelamento e classificação múltipla
    """
    TIPO_CHOICES = [
        ('PAGAR', 'Conta a Pagar'),
        ('RECEBER', 'Conta a Receber'),
    ]
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, help_text="Tipo do movimento")
    pessoa = models.ForeignKey(Pessoas, on_delete=models.PROTECT, help_text="Pessoa relacionada ao movimento")
    descricao = models.TextField(help_text="Descrição do movimento")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Valor total do movimento")
    quantidade_parcelas = models.IntegerField(default=1, help_text="Número de parcelas")
    data_emissao = models.DateField(help_text="Data de emissão")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', help_text="Status do movimento")
    ativo = models.BooleanField(default=True, help_text="Indica se o movimento está ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'movimentocontas'
        verbose_name = 'Movimento de Conta'
        verbose_name_plural = 'Movimentos de Contas'
        
    def __str__(self):
        return self.descricao
    
    def criar_parcelas(self):
        """
        Método para criar as parcelas automaticamente
        Implementa a regra: parcelas com data de vencimento distinto
        """
        if self.quantidade_parcelas > 1:
            valor_parcela = self.valor_total / self.quantidade_parcelas
            data_base = self.data_emissao
            
            for i in range(self.quantidade_parcelas):
                # Calcula vencimento (mês seguinte para cada parcela)
                if i == 0:
                    data_vencimento = data_base
                else:
                    # Adiciona um mês para cada parcela
                    mes = data_base.month + i
                    ano = data_base.year
                    while mes > 12:
                        mes -= 12
                        ano += 1
                    data_vencimento = data_base.replace(year=ano, month=mes)
                
                # Cria identificação única para a parcela
                identificacao = f"{self.id}-{i+1:03d}-{data_vencimento.strftime('%Y%m')}"
                
                ParcelaContas.objects.create(
                    movimento=self,
                    numero_parcela=i+1,
                    valor_parcela=valor_parcela,
                    data_vencimento=data_vencimento,
                    identificacao_unica=identificacao
                )


class ParcelaContas(models.Model):
    """
    Model para parcelas dos movimentos
    Cada movimento pode ter uma ou mais parcelas
    """
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('PAGO', 'Pago'),
    ]
    
    movimento = models.ForeignKey(MovimentoContas, on_delete=models.CASCADE, related_name='parcelas', help_text="Movimento relacionado")
    numero_parcela = models.IntegerField(help_text="Número da parcela")
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor da parcela")
    data_vencimento = models.DateField(help_text="Data de vencimento da parcela")
    data_pagamento = models.DateField(blank=True, null=True, help_text="Data de pagamento (se pago)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', help_text="Status da parcela")
    identificacao_unica = models.CharField(max_length=50, unique=True, help_text="Identificação única da parcela")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'parcelacontas'
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['numero_parcela']
        
    def __str__(self):
        return f"Parcela {self.numero_parcela} - {self.movimento}"


class MovimentoClassificacao(models.Model):
    """
    Model para relacionar movimentos com classificações
    Um movimento pode ter uma ou mais classificações
    """
    movimento = models.ForeignKey(MovimentoContas, on_delete=models.CASCADE, help_text="Movimento relacionado")
    classificacao = models.ForeignKey(Classificacao, on_delete=models.PROTECT, help_text="Classificação relacionada")
    valor_classificado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor classificado")
    
    class Meta:
        db_table = 'movimento_classificacao'
        verbose_name = 'Classificação do Movimento'
        verbose_name_plural = 'Classificações dos Movimentos'
        
    def __str__(self):
        return str(self.classificacao)
