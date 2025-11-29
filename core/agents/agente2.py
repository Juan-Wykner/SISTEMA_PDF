import json
from django.http import JsonResponse
from core.models import Pessoas, Classificacao, MovimentoContas, MovimentoClassificacao
from datetime import datetime

def processar_request(request, funcao):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        dados = json.loads(request.body) if request.body else {}
        return funcao(dados)
    except Exception:
        return JsonResponse({'erro': 'Erro no processamento'}, status=400)

def formatar_documento(numero, tipo):
    if tipo == 'CNPJ' and len(numero) == 14:
        return f"{numero[:2]}.{numero[2:5]}.{numero[5:8]}/{numero[8:12]}-{numero[12:]}"
    if tipo == 'CPF' and len(numero) == 11:
        return f"{numero[:3]}.{numero[3:6]}.{numero[6:9]}-{numero[9:]}"
    return numero

def validar_pessoa(dados, tipo_pessoa, tipo_documento):
    documento = dados.get('cnpj' if tipo_documento == 'CNPJ' else 'cpf', '').replace('.', '').replace('/', '').replace('-', '')
    nome = dados.get('razao_social' if tipo_documento == 'CNPJ' else 'nome', '')
    
    pessoa = Pessoas.objects.filter(tipo=tipo_pessoa, cnpj_cpf=documento).first()
    
    if pessoa:
        doc_formatado = formatar_documento(pessoa.cnpj_cpf, tipo_documento)
        mensagem = f"{tipo_pessoa}\n{pessoa.razao_social}\n{tipo_documento}: {doc_formatado}\nEXISTE - ID: {pessoa.id}"
        return {
            'existe': True,
            'id': pessoa.id,
            'mensagem': mensagem,
            'dados': {'id': pessoa.id, 'nome': pessoa.razao_social, tipo_documento.lower(): pessoa.cnpj_cpf}
        }
    else:
        doc_formatado = formatar_documento(documento, tipo_documento)
        mensagem = f"{tipo_pessoa}\n{nome}\n{tipo_documento}: {doc_formatado}\nNÃO EXISTE"
        return {'existe': False, 'mensagem': mensagem}

def validar_classificacao(dados, tipo):
    descricao = dados.get('descricao', '')
    classificacao = Classificacao.objects.filter(tipo=tipo, descricao__iexact=descricao).first()
    
    if classificacao:
        mensagem = f"{tipo}\n{classificacao.descricao}\nEXISTE - ID: {classificacao.id}"
        return {
            'existe': True,
            'id': classificacao.id,
            'mensagem': mensagem,
            'dados': {'id': classificacao.id, 'descricao': classificacao.descricao, 'tipo': classificacao.tipo}
        }
    else:
        mensagem = f"{tipo}\n{descricao}\nNÃO EXISTE"
        return {'existe': False, 'mensagem': mensagem}

def criar_registro(dados, modelo, campos, tipo=None):
    try:
        if modelo == Pessoas:
            documento = dados.get('cnpj' if tipo == 'FORNECEDOR' else 'cpf', '')
            documento_limpo = documento.replace('.', '').replace('/', '').replace('-', '')
            dados['cnpj_cpf'] = documento_limpo
            if tipo: dados['tipo'] = tipo
        
        novo_obj = modelo.objects.create(**{campo: dados.get(campo, '') for campo in campos})
        return {'sucesso': True, 'mensagem': f'Registro criado - ID: {novo_obj.id}', 'id': novo_obj.id}
    except Exception:
        return {'erro': 'Erro ao criar registro'}

def validar_fornecedor(request):
    def processar(dados):
        return validar_pessoa(dados, 'FORNECEDOR', 'CNPJ')
    return JsonResponse(processar_request(request, processar))

def validar_faturado(request):
    def processar(dados):
        return validar_pessoa(dados, 'FATURADO', 'CPF')
    return JsonResponse(processar_request(request, processar))

def validar_classificacao_despesa(request):
    def processar(dados):
        return validar_classificacao(dados, 'DESPESA')
    return JsonResponse(processar_request(request, processar))

def validar_classificacao_receita(request):
    def processar(dados):
        return validar_classificacao(dados, 'RECEITA')
    return JsonResponse(processar_request(request, processar))

def criar_fornecedor(request):
    def processar(dados):
        campos = ['razao_social', 'nome_fantasia', 'cnpj_cpf', 'telefone', 'email', 'endereco']
        return criar_registro(dados, Pessoas, campos, 'FORNECEDOR')
    return JsonResponse(processar_request(request, processar))

def criar_faturado(request):
    def processar(dados):
        campos = ['razao_social', 'cnpj_cpf', 'telefone', 'email', 'endereco']
        return criar_registro(dados, Pessoas, campos, 'FATURADO')
    return JsonResponse(processar_request(request, processar))

def criar_classificacao(request):
    def processar(dados):
        campos = ['tipo', 'descricao']
        return criar_registro(dados, Classificacao, campos)
    return JsonResponse(processar_request(request, processar))

def processar_lancamento(request):
    def processar(dados):
        try:
            movimento = MovimentoContas.objects.create(
                tipo=dados.get('tipo', 'PAGAR'),
                pessoa_id=dados.get('pessoa_id'),
                descricao=dados.get('descricao', ''),
                valor_total=float(dados.get('valor_total', 0)),
                quantidade_parcelas=int(dados.get('quantidade_parcelas', 1)),
                data_emissao=datetime.strptime(dados['data_emissao'], '%Y-%m-%d').date() if dados.get('data_emissao') else None
            )
            
            movimento.criar_parcelas()
            
            classificacoes = dados.get('classificacoes', [])
            if classificacoes:
                valor_por_classificacao = movimento.valor_total / len(classificacoes)
                for classificacao_id in classificacoes:
                    MovimentoClassificacao.objects.create(
                        movimento=movimento,
                        classificacao_id=classificacao_id,
                        valor_classificado=valor_por_classificacao
                    )
            
            return {'sucesso': True, 'mensagem': f'Lançado com sucesso - ID: {movimento.id}', 'movimento_id': movimento.id}
        except Exception:
            return {'erro': 'Erro no lançamento'}
    
    return JsonResponse(processar_request(request, processar))