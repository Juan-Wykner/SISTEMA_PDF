import json
from typing import Dict, Any

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import PDFUploadForm
from .infrastructure.file_storage import (
    save_uploaded_to_temp,
    remove_file_safely,
    save_uploaded_to_temp_safe,
)
from .services import processar_pdf

def home(request):
    """
    Tela inicial com navegação para Upload e RAG.
    """
    return render(request, "core/home.html")

def upload_pdf(request):
    """
    Interface de upload de PDF + processamento visual.

    Responsabilidades:
    - Receber upload de PDF.
    - Salvar temporariamente (infra).
    - Processar conteúdo (serviço).
    - Renderizar resultado.
    """
    try:
        if request.method == "POST":
            print(f"POST request received")
            print(f"Request FILES: {request.FILES}")
            print(f"Request POST: {request.POST}")
            
            # Simplificar - verificar diretamente se tem arquivo
            if request.FILES.get("pdf_file"):
                uploaded = request.FILES["pdf_file"]
                print(f"Processing file: {uploaded.name}")
                
                try:
                    temp_path = save_uploaded_to_temp_safe(uploaded, settings.MEDIA_ROOT, uploaded.name)
                    print(f"File saved to: {temp_path}")
                    
                    # Validar que é um arquivo PDF binário válido após salvar
                    with open(temp_path, 'rb') as f:
                        header = f.read(4)
                    print(f"PDF header: {header}")
                    
                    if header != b'%PDF':
                        remove_file_safely(temp_path)
                        dados_extraidos = {"erro": "Arquivo inválido", "detalhes": "O arquivo enviado não é um PDF válido"}
                    else:
                        # Processar PDF
                        dados_extraidos: Dict[str, Any] = processar_pdf(temp_path)
                        print(f"PDF processed successfully: {dados_extraidos}")
                        
                except Exception as exc:
                    print(f"Error processing PDF: {str(exc)}")
                    dados_extraidos = {"erro": "Falha ao processar o PDF", "detalhes": str(exc)}
                finally:
                    if 'temp_path' in locals():
                        remove_file_safely(temp_path)

                print(f"Rendering result page with data: {dados_extraidos}")
                return render(
                    request,
                    "core/resultado_extracao.html",
                    {
                        "dados": dados_extraidos,
                        "dados_json": json.dumps(dados_extraidos, indent=2, ensure_ascii=False),
                    },
                )
            else:
                print("No PDF file found in request")
        else:
            form = PDFUploadForm()

        print("Rendering upload form (GET request or invalid form)")
        return render(request, "core/upload_pdf.html", {"form": form})
        
    except Exception as e:
        print(f"UNEXPECTED ERROR in upload_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a simple error response
        return JsonResponse({"erro": "Erro interno no servidor", "detalhes": str(e)}, status=500)

def extrair_dados(request):
    """
    Endpoint JSON para extração rápida de dados do PDF.
    """
    if request.method == "POST" and request.FILES.get("pdf_file"):
        uploaded = request.FILES["pdf_file"]
        
        # Validar que é um arquivo PDF binário válido
        try:
            # Ler os primeiros bytes para verificar o header PDF
            uploaded.seek(0)
            header = uploaded.read(4)
            uploaded.seek(0)
            
            if header != b'%PDF':
                return JsonResponse({
                    "erro": "Arquivo inválido", 
                    "detalhes": "O arquivo enviado não é um PDF válido"
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                "erro": "Erro ao validar arquivo", 
                "detalhes": str(e)
            }, status=400)
        
        temp_path = save_uploaded_to_temp_safe(uploaded, settings.MEDIA_ROOT, uploaded.name)

        try:
            dados_extraidos: Dict[str, Any] = processar_pdf(temp_path)
        except Exception as exc:
            dados_extraidos = {"erro": "Falha ao processar o PDF", "detalhes": str(exc)}
        finally:
            remove_file_safely(temp_path)

        return JsonResponse(dados_extraidos)

    return JsonResponse({"erro": "Arquivo não enviado"}, status=400)

def redirecionar_validacao(request):
    """
    Redireciona para a interface de validação com os dados do PDF.

    Usa `urlencode` com `doseq=True` para listas (classificações/produtos),
    evitando construir strings manualmente.
    """
    from urllib.parse import urlencode

    if request.method == "POST":
        dados = {
            "fornecedor_nome": request.POST.get("fornecedor_nome", ""),
            "fornecedor_cnpj": request.POST.get("fornecedor_cnpj", ""),
            "faturado_nome": request.POST.get("faturado_nome", ""),
            "faturado_cpf": request.POST.get("faturado_cpf", ""),
            "nf_numero": request.POST.get("nf_numero", ""),
            "nf_valor": request.POST.get("nf_valor", ""),
            "nf_data": request.POST.get("nf_data", ""),
            "classificacoes[]": request.POST.getlist("classificacoes[]"),
            "produtos[]": request.POST.getlist("produtos[]"),
        }

        # Remove chaves com valores vazios
        dados_filtrados = {k: v for k, v in dados.items() if v}
        query = urlencode(dados_filtrados, doseq=True)
        url = f"{reverse('interface_validacao')}?{query}"
        return redirect(url)

    return JsonResponse({"erro": "Método não permitido"}, status=405)

def rag(request):
    """
    Página de entrada para funcionalidades de RAG.
    """
    from .agents.agente3 import AgenteRAG

    contexto = {
        "resposta": None,
        "trechos": [],
        "evidencias": [],
        "erro": None,
        "pergunta": "",
    }

    if request.method == "POST":
        try:
            # Garantir que a pergunta esteja em UTF-8 válido
            pergunta_raw = request.POST.get("pergunta", "")
            contexto["pergunta"] = pergunta_raw
            if pergunta_raw:
                try:
                    # Sanitizar a pergunta para garantir UTF-8
                    pergunta = pergunta_raw.encode('utf-8', errors='ignore').decode('utf-8').strip()
                except (UnicodeDecodeError, UnicodeEncodeError) as e:
                    contexto["erro"] = f"Erro de encoding na pergunta: {str(e)}"
                    return render(request, "core/rag.html", contexto)
                
                # Processar com o agente RAG
                try:
                    agente = AgenteRAG()
                    resultado = agente.responder(pergunta)
                    
                    if resultado.get("resposta"):
                        contexto["resposta"] = resultado.get("resposta", "")
                        contexto["evidencias"] = resultado.get("trechos", [])
                    else:
                        contexto["erro"] = resultado.get("erro", "Erro desconhecido no processamento")
                except ValueError as e:
                    if "GEMINI_API_KEY" in str(e):
                        contexto["erro"] = "GEMINI_API_KEY não configurada. Por favor, configure a chave de API nas variáveis de ambiente."
                    else:
                        contexto["erro"] = f"Erro ao inicializar agente RAG: {str(e)}"
                except Exception as e:
                    contexto["erro"] = f"Erro ao processar com agente RAG: {str(e)}"
            else:
                contexto["erro"] = "Por favor, forneça uma pergunta."
                
        except Exception as e:
            contexto["erro"] = f"Erro ao processar requisição: {str(e)}"
    
    return render(request, "core/rag.html", contexto)

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
from .models import Pessoas, Classificacao, MovimentoContas, ParcelaContas, MovimentoClassificacao

def db_health(request):
    """
    Endpoint de saúde do banco: resolve DNS e testa SELECT 1.
    Não expõe segredos.
    """
    import os
    import socket
    from django.conf import settings
    from django.db import connections

    # Extrair host/port de DATABASE_URL ou DB_* sem expor senha
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'postgres')
    dburl = os.getenv('DATABASE_URL')
    if dburl and not host:
        try:
            from urllib.parse import urlparse
            u = urlparse(dburl)
            host = u.hostname
            port = str(u.port or '5432')
            user = u.username or user
        except Exception:
            pass

    result = {
        'host': host or '',
        'port': port,
        'user': user,
        'dns_resolved': False,
        'addresses': [],
        'db_connect': False,
        'error': None,
    }

    try:
        if host:
            infos = socket.getaddrinfo(host, int(port))
            result['dns_resolved'] = True
            result['addresses'] = list({i[4][0] for i in infos})
    except Exception as e:
        result['error'] = f'DNS error: {e}'

    # Teste de conexão SELECT 1
    try:
        conn = connections['default']
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
        result['db_connect'] = True
    except Exception as e:
        result['error'] = f'DB connect error: {e}'

    return JsonResponse(result)

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
