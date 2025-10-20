from django.urls import path
from . import views
from .views_validacao import (
    interface_validacao, criar_fornecedor, criar_faturado, criar_classificacao, criar_lancamento,
    validar_fornecedor_api, validar_faturado_api, validar_classificacao_api
)
from .agents import agente2

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('extrair-dados/', views.extrair_dados, name='extrair_dados'),
    
    # Interface de Validação Interativa
    path('validacao/', interface_validacao, name='interface_validacao'),
    
    # APIs de Validação - Novas rotas para interface
    path('api/validar-fornecedor/', validar_fornecedor_api, name='validar_fornecedor_api'),
    path('api/validar-faturado/', validar_faturado_api, name='validar_faturado_api'),
    path('api/validar-classificacao/', validar_classificacao_api, name='validar_classificacao_api'),
    
    # APIs de Criação - Novas rotas para interface
    path('api/criar-fornecedor/', criar_fornecedor, name='criar_fornecedor'),
    path('api/criar-faturado/', criar_faturado, name='criar_faturado'),
    path('api/criar-classificacao/', criar_classificacao, name='criar_classificacao'),
    path('api/criar-lancamento/', criar_lancamento, name='criar_lancamento'),
    
    # Redirecionamento para validação
    path('redirecionar-validacao/', views.redirecionar_validacao, name='redirecionar_validacao'),
    
    # URLs do Agente2 - Validações (mantidas para compatibilidade)
    path('agente2/validar_fornecedor/', agente2.validar_fornecedor, name='validar_fornecedor'),
    path('agente2/validar_faturado/', agente2.validar_faturado, name='validar_faturado'),
    path('agente2/validar_classificacao_despesa/', agente2.validar_classificacao_despesa, name='validar_classificacao_despesa'),
    path('agente2/validar_classificacao_receita/', agente2.validar_classificacao_receita, name='validar_classificacao_receita'),
    
    # URLs do Agente2 - Criações (mantidas para compatibilidade)
    path('agente2/criar_fornecedor/', agente2.criar_fornecedor, name='criar_fornecedor'),
    path('agente2/criar_faturado/', agente2.criar_faturado, name='criar_faturado'),
    path('agente2/criar_classificacao/', agente2.criar_classificacao, name='criar_classificacao'),
    
    # URL do Agente2 - Processar lançamento completo (mantida para compatibilidade)
    path('agente2/processar_lancamento/', agente2.processar_lancamento, name='processar_lancamento'),
]