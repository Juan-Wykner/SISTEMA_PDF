import json
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from .forms import PDFUploadForm
from .services import processar_pdf

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', pdf_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            
            try:
                dados = processar_pdf(temp_path)
            except Exception as e:
                dados = {"erro": "Falha ao processar o PDF", "detalhes": str(e)}
            finally:
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            
            return render(request, 'core/resultado_extracao.html', {
                'dados': dados,
                'dados_json': json.dumps(dados, indent=2, ensure_ascii=False)
            })
    else:
        form = PDFUploadForm()
    
    return render(request, 'core/upload_pdf.html', {'form': form})

def extrair_dados(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', pdf_file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        try:
            dados = processar_pdf(temp_path)
        except Exception as e:
            dados = {"erro": "Falha ao processar o PDF", "detalhes": str(e)}
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
        
        return JsonResponse(dados)
    
    return JsonResponse({'erro': 'Arquivo não enviado'})

def redirecionar_validacao(request):
    """
    Redireciona para a interface de validação com os dados do PDF
    """
    if request.method == 'POST':
        # Receber dados do formulário
        dados = {
            'fornecedor_nome': request.POST.get('fornecedor_nome', ''),
            'fornecedor_cnpj': request.POST.get('fornecedor_cnpj', ''),
            'faturado_nome': request.POST.get('faturado_nome', ''),
            'faturado_cpf': request.POST.get('faturado_cpf', ''),
            'nf_numero': request.POST.get('nf_numero', ''),
            'nf_valor': request.POST.get('nf_valor', ''),
            'nf_data': request.POST.get('nf_data', ''),
        }
        
        # Adicionar classificações
        classificacoes = request.POST.getlist('classificacoes[]')
        
        # Adicionar produtos
        produtos = request.POST.getlist('produtos[]')
        
        # Construir URL com parâmetros
        url_parts = []
        for k, v in dados.items():
            if v:
                url_parts.append(f'{k}={v}')
        
        # Adicionar classificações como lista
        for classificacao in classificacoes:
            url_parts.append(f'classificacoes[]={classificacao}')
            
        # Adicionar produtos como lista
        for produto in produtos:
            url_parts.append(f'produtos[]={produto}')
        
        url = reverse('interface_validacao') + '?' + '&'.join(url_parts)
        
        return redirect(url)
    
    return JsonResponse({'erro': 'Método não permitido'})