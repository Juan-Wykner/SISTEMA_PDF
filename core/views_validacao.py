from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from core.models import Pessoas, Classificacao, MovimentoContas, ParcelaContas, MovimentoClassificacao

def validar_fornecedor_api(request):
    """
    API para validar fornecedor via GET (para interface AJAX)
    """
    if request.method == 'GET':
        try:
            cnpj = request.GET.get('cnpj', '').strip()
            if not cnpj:
                return JsonResponse({'erro': 'CNPJ não fornecido'}, status=400)
            
            # Limpar CNPJ
            cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')
            
            # Verificar se existe
            fornecedor = Pessoas.objects.filter(
                cnpj_cpf=cnpj_limpo, 
                tipo='FORNECEDOR'
            ).first()
            
            if fornecedor:
                return JsonResponse({
                    'existe': True,
                    'id': fornecedor.id,
                    'nome': fornecedor.razao_social,
                    'mensagem': f'Fornecedor encontrado: {fornecedor.razao_social}'
                })
            else:
                return JsonResponse({
                    'existe': False,
                    'mensagem': 'Fornecedor não encontrado no banco de dados'
                })
                
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def validar_faturado_api(request):
    """
    API para validar faturado via GET (para interface AJAX)
    """
    if request.method == 'GET':
        try:
            cpf = request.GET.get('cpf', '').strip()
            if not cpf:
                return JsonResponse({'erro': 'CPF não fornecido'}, status=400)
            
            # Limpar CPF
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Verificar se existe
            faturado = Pessoas.objects.filter(
                cnpj_cpf=cpf_limpo, 
                tipo='FATURADO'
            ).first()
            
            if faturado:
                return JsonResponse({
                    'existe': True,
                    'id': faturado.id,
                    'nome': faturado.razao_social,
                    'mensagem': f'Faturado encontrado: {faturado.razao_social}'
                })
            else:
                return JsonResponse({
                    'existe': False,
                    'mensagem': 'Faturado não encontrado no banco de dados'
                })
                
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def validar_classificacao_api(request):
    """
    API para validar classificação via GET (para interface AJAX)
    """
    if request.method == 'GET':
        try:
            descricao = request.GET.get('descricao', '').strip()
            if not descricao:
                return JsonResponse({'erro': 'Descrição não fornecida'}, status=400)
            
            # Verificar se existe
            classificacao = Classificacao.objects.filter(
                descricao__iexact=descricao,
                tipo='DESPESA'
            ).first()
            
            if classificacao:
                return JsonResponse({
                    'existe': True,
                    'id': classificacao.id,
                    'descricao': classificacao.descricao,
                    'mensagem': f'Classificação encontrada: {classificacao.descricao}'
                })
            else:
                return JsonResponse({
                    'existe': False,
                    'mensagem': f'Classificação "{descricao}" não encontrada'
                })
                
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def interface_validacao(request):
    """
    Renderiza a interface de validação interativa com dados do PDF
    """
    import urllib.parse
    
    # Receber dados via GET (passados da extração)
    dados_pdf = {
        'fornecedor': {
            'razao_social': request.GET.get('fornecedor_nome', ''),
            'cnpj': request.GET.get('fornecedor_cnpj', ''),
        },
        'faturado': {
            'nome': request.GET.get('faturado_nome', ''),
            'cpf': request.GET.get('faturado_cpf', ''),
        },
        'nota_fiscal': {
            'numero': request.GET.get('nf_numero', ''),
            'valor': request.GET.get('nf_valor', ''),
            'data_emissao': request.GET.get('nf_data', ''),
        },
        'classificacoes': request.GET.getlist('classificacoes[]') if request.GET.getlist('classificacoes[]') else [],
        'produtos': request.GET.getlist('produtos[]') if request.GET.getlist('produtos[]') else [],
    }
    
    # Debug para verificar dados recebidos
    print("=== DADOS RECEBIDOS NA INTERFACE ===")
    print(f"Fornecedor: {dados_pdf['fornecedor']}")
    print(f"Faturado: {dados_pdf['faturado']}")
    print(f"Classificações: {dados_pdf['classificacoes']}")
    print(f"Produtos: {dados_pdf['produtos']}")
    print("=== FIM DADOS ===")
    
    context = {
        'dados_pdf': dados_pdf,
        'csrf_token': request.META.get('CSRF_COOKIE', ''),
    }
    
    return render(request, 'core/validacao_interativa.html', context)

@csrf_exempt
def criar_fornecedor(request):
    """
    View para criar um novo fornecedor no banco de dados
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Preparar dados do fornecedor
            cnpj = data.get('cnpj', '').strip()
            razao_social = data.get('razao_social', '').strip()
            nome_fantasia = data.get('nome_fantasia', '').strip()
            
            # Limpar CNPJ (remover máscaras)
            cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')
            
            # Verificar se já existe
            if Pessoas.objects.filter(cnpj_cpf=cnpj_limpo, tipo='FORNECEDOR').exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Fornecedor com este CNPJ já existe'
                })
            
            # Criar fornecedor
            with transaction.atomic():
                fornecedor = Pessoas.objects.create(
                    tipo='FORNECEDOR',
                    razao_social=razao_social,
                    nome_fantasia=nome_fantasia or razao_social,
                    cnpj_cpf=cnpj_limpo,
                    ativo=True
                )
                
                return JsonResponse({
                    'sucesso': True,
                    'id': fornecedor.id,
                    'mensagem': f'Fornecedor criado com sucesso: {razao_social}'
                })
                
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            })
    
    return JsonResponse({
        'sucesso': False,
        'erro': 'Método não permitido'
    })

@csrf_exempt
def criar_faturado(request):
    """
    View para criar um novo faturado no banco de dados
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Preparar dados do faturado
            cpf = data.get('cpf', '').strip()
            nome = data.get('nome', '').strip() or data.get('nome_completo', '').strip()
            
            # Limpar CPF (remover máscaras)
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Verificar se já existe
            if Pessoas.objects.filter(cnpj_cpf=cpf_limpo, tipo='FATURADO').exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Faturado com este CPF já existe'
                })
            
            # Criar faturado
            with transaction.atomic():
                faturado = Pessoas.objects.create(
                    tipo='FATURADO',
                    razao_social=nome,
                    cnpj_cpf=cpf_limpo,
                    ativo=True
                )
                
                return JsonResponse({
                    'sucesso': True,
                    'id': faturado.id,
                    'mensagem': f'Faturado criado com sucesso: {nome}'
                })
                
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            })
    
    return JsonResponse({
        'sucesso': False,
        'erro': 'Método não permitido'
    })

@csrf_exempt
def criar_classificacao(request):
    """
    View para criar uma nova classificação no banco de dados
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Preparar dados da classificação
            descricao = data.get('descricao', '').strip()
            tipo = data.get('tipo', 'DESPESA').upper()
            
            # Verificar se já existe
            if Classificacao.objects.filter(descricao__iexact=descricao, tipo=tipo).exists():
                return JsonResponse({
                    'sucesso': False,
                    'erro': f'Classificação "{descricao}" já existe'
                })
            
            # Criar classificação
            with transaction.atomic():
                classificacao = Classificacao.objects.create(
                    descricao=descricao,
                    tipo=tipo,
                    ativo=True
                )
                
                return JsonResponse({
                    'sucesso': True,
                    'id': classificacao.id,
                    'mensagem': f'Classificação criada com sucesso: {descricao}'
                })
                
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            })
    
    return JsonResponse({
        'sucesso': False,
        'erro': 'Método não permitido'
    })

@csrf_exempt
def criar_lancamento(request):
    """
    View para criar o lançamento completo após validações
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Obter IDs dos cadastros
            cnpj_fornecedor = data['fornecedor']['cnpj'].replace('.', '').replace('/', '').replace('-', '')
            cpf_faturado = data['faturado']['cpf'].replace('.', '').replace('-', '')

            # Buscar fornecedor
            fornecedor = Pessoas.objects.filter(
                cnpj_cpf=cnpj_fornecedor,
                tipo='FORNECEDOR'
            ).first()

            if not fornecedor:
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Fornecedor não encontrado. Por favor, valide os cadastros novamente.'
                })

            # Buscar faturado
            faturado = Pessoas.objects.filter(
                cnpj_cpf=cpf_faturado,
                tipo='FATURADO'
            ).first()

            if not faturado:
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Faturado não encontrado. Por favor, valide os cadastros novamente.'
                })

            # Criar lançamento com atomicidade
            with transaction.atomic():
                # Criar movimento de contas (removendo argumentos inválidos)
                # Extrair dados da nota fiscal
                nf = data.get('nota_fiscal', {})
                nf_numero = (nf.get('numero') or data.get('numero_nota_fiscal') or '').strip()
                nf_valor_raw = nf.get('valor') or data.get('valor_total') or 0
                nf_data_raw = nf.get('data_emissao') or data.get('data_emissao') or ''

                # Parse de data de emissão (aceita YYYY-MM-DD ou DD/MM/YYYY)
                from datetime import datetime
                data_emissao = None
                if isinstance(nf_data_raw, str) and nf_data_raw:
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                        try:
                            data_emissao = datetime.strptime(nf_data_raw, fmt).date()
                            break
                        except Exception:
                            pass
                if not data_emissao:
                    return JsonResponse({
                        'sucesso': False,
                        'erro': 'Data de emissão não informada ou inválida'
                    })

                # Parse de valor total (normaliza separadores)
                try:
                    if isinstance(nf_valor_raw, str):
                        nf_valor_raw = nf_valor_raw.strip().replace('.', '').replace(',', '.')
                    valor_total = float(nf_valor_raw)
                except Exception:
                    valor_total = 0.0

                quantidade_parcelas = int(data.get('quantidade_parcelas', 1) or 1)

                movimento = MovimentoContas.objects.create(
                    tipo='PAGAR',
                    pessoa=fornecedor,
                    data_emissao=data_emissao,
                    valor_total=valor_total,
                    descricao=f"NF {nf_numero} - {fornecedor.razao_social} - Faturado: {faturado.razao_social}",
                    quantidade_parcelas=quantidade_parcelas,
                    ativo=True
                )

                # Criar parcelas corretamente
                if quantidade_parcelas > 1:
                    movimento.criar_parcelas()
                else:
                    # Vencimento: usa data emissao se não houver outra data informada
                    data_venc_raw = nf.get('data_vencimento') or data.get('data_vencimento')
                    data_vencimento = None
                    if isinstance(data_venc_raw, str) and data_venc_raw:
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                            try:
                                data_vencimento = datetime.strptime(data_venc_raw, fmt).date()
                                break
                            except Exception:
                                pass
                    if not data_vencimento:
                        data_vencimento = movimento.data_emissao

                    valor_parcela = valor_total

                    identificacao = f"{movimento.id}-001-{data_vencimento.strftime('%Y%m')}"

                    ParcelaContas.objects.create(
                        movimento=movimento,
                        numero_parcela=1,
                        data_vencimento=data_vencimento,
                        valor_parcela=valor_parcela,
                        identificacao_unica=identificacao
                    )

                # Criar classificações corretamente
                classificacoes_despesa = data.get('classificacao_despesa', [])
                total = valor_total
                valor_por_classificacao = total / len(classificacoes_despesa) if classificacoes_despesa else total
                for classificacao_desc in classificacoes_despesa:
                    classificacao = Classificacao.objects.filter(
                        descricao__iexact=classificacao_desc,
                        tipo='DESPESA'
                    ).first()

                    if classificacao:
                        MovimentoClassificacao.objects.create(
                            movimento=movimento,
                            classificacao=classificacao,
                            valor_classificado=valor_por_classificacao
                        )

                return JsonResponse({
                    'sucesso': True,
                    'id': movimento.id,
                    'mensagem': f'Lançamento criado com sucesso! ID: {movimento.id}'
                })

        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            })

    return JsonResponse({
        'sucesso': False,
        'erro': 'Método não permitido'
    })