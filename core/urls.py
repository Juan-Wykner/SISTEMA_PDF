from django.urls import path
from . import views
from .agents import agente2

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('extrair-dados/', views.extrair_dados, name='extrair_dados'),
    
    # Interface de Validação Interativa
    path('validacao/', views.interface_validacao, name='interface_validacao'),
    
    # APIs de Validação - Novas rotas para interface
    path('api/validar-fornecedor/', views.validar_fornecedor_api, name='validar_fornecedor_api'),
    path('api/validar-faturado/', views.validar_faturado_api, name='validar_faturado_api'),
    path('api/validar-classificacao/', views.validar_classificacao_api, name='validar_classificacao_api'),
    
    # APIs de Criação - Novas rotas para interface
    path('api/criar-fornecedor/', views.criar_fornecedor, name='criar_fornecedor'),
    path('api/criar-faturado/', views.criar_faturado, name='criar_faturado'),
    path('api/criar-classificacao/', views.criar_classificacao, name='criar_classificacao'),
    path('api/criar-lancamento/', views.criar_lancamento, name='criar_lancamento'),
    # Health
    path('health/db/', views.db_health, name='db_health'),
    
    # Redirecionamento para validação
    path('redirecionar-validacao/', views.redirecionar_validacao, name='redirecionar_validacao'),
    path('rag/', views.rag, name='rag'),
    # Gerenciamento BD
    path('gerenciamento-bd/', views.gerenciamento_bd, name='gerenciamento_bd'),
    # APIs Gerenciamento
    path('api/gbd/pessoas/', views.gbd_pessoas_list_create, name='gbd_pessoas_list_create'),
    path('api/gbd/pessoas/<int:pid>/', views.gbd_pessoas_update_delete, name='gbd_pessoas_update_delete'),
    path('api/gbd/pessoas/<int:pid>/reativar/', views.gbd_pessoas_reativar, name='gbd_pessoas_reativar'),
    path('api/gbd/classificacao/', views.gbd_class_list_create, name='gbd_class_list_create'),
    path('api/gbd/classificacao/<int:cid>/', views.gbd_class_update_delete, name='gbd_class_update_delete'),
    path('api/gbd/classificacao/<int:cid>/reativar/', views.gbd_class_reativar, name='gbd_class_reativar'),
    path('api/gbd/contas/', views.gbd_contas_list_create, name='gbd_contas_list_create'),
    path('api/gbd/contas/<int:mid>/', views.gbd_contas_update_delete, name='gbd_contas_update_delete'),
    path('api/gbd/contas/<int:mid>/reativar/', views.gbd_contas_reativar, name='gbd_contas_reativar'),
    
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
