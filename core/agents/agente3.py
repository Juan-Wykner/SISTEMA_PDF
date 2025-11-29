import json
import google.generativeai as genai
from decouple import config
from core.models import MovimentoContas, MovimentoClassificacao, Pessoas, Classificacao
from django.db.models import Sum, Q
from datetime import datetime, timedelta


class AgenteRAG:
    def __init__(self, top_k=5):
        """
        Agente RAG para responder perguntas sobre dados financeiros.
        """
        self.top_k = top_k
        api_key = config("GEMINI_API_KEY", default=None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def buscar_trechos_relevantes(self, pergunta):
        """
        Busca trechos relevantes no banco de dados baseado na pergunta.
        """
        trechos = []
        
        try:
            # Converter pergunta para minúsculas para busca
            pergunta_lower = pergunta.lower()
            
            # Buscar por despesas/receitas por período
            if any(palavra in pergunta_lower for palavra in ['mês', 'mes', 'semana', 'dia', 'ano', 'último', 'ultimo']):
                trechos.extend(self._buscar_por_periodo(pergunta_lower))
            
            # Buscar por valores específicos
            if any(palavra in pergunta_lower for palavra in ['valor', 'total', 'soma', 'quanto']):
                trechos.extend(self._buscar_valores(pergunta_lower))
            
            # Buscar por fornecedores/faturados
            if any(palavra in pergunta_lower for palavra in ['fornecedor', 'faturado', 'cliente', 'empresa']):
                trechos.extend(self._buscar_pessoas(pergunta_lower))
            
            # Buscar por classificações
            if any(palavra in pergunta_lower for palavra in ['classificação', 'classificacao', 'categoria', 'tipo']):
                trechos.extend(self._buscar_classificacoes(pergunta_lower))
            
            # Buscar por descrições
            if any(palavra in pergunta_lower for palavra in ['descrição', 'descricao', 'sobre', 'referente']):
                trechos.extend(self._buscar_descricoes(pergunta_lower))
            
            # Se não encontrou nada específico, buscar movimentos recentes
            if not trechos:
                trechos.extend(self._buscar_movimentos_recentes())
            
            return trechos[:self.top_k]
            
        except Exception as e:
            return [{"titulo": "Erro na busca", "texto": f"Erro ao buscar dados: {str(e)}"}]
    
    def _buscar_por_periodo(self, pergunta):
        """Busca movimentos por período."""
        trechos = []
        
        try:
            hoje = datetime.now().date()
            
            # Determinar período
            if 'mês' in pergunta or 'mes' in pergunta:
                if 'último' in pergunta or 'ultimo' in pergunta:
                    data_inicio = hoje.replace(day=1) - timedelta(days=1)
                    data_inicio = data_inicio.replace(day=1)
                    data_fim = hoje.replace(day=1) - timedelta(days=1)
                else:
                    data_inicio = hoje.replace(day=1)
                    data_fim = hoje
            elif 'semana' in pergunta:
                data_inicio = hoje - timedelta(days=hoje.weekday())
                data_fim = hoje
            elif 'dia' in pergunta:
                data_inicio = hoje
                data_fim = hoje
            else:
                # Últimos 30 dias por padrão
                data_inicio = hoje - timedelta(days=30)
                data_fim = hoje
            
            movimentos = MovimentoContas.objects.filter(
                data_emissao__range=[data_inicio, data_fim]
            ).select_related('pessoa').order_by('-data_emissao')[:10]
            
            if movimentos:
                total_despesas = movimentos.filter(tipo='PAGAR').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
                total_receitas = movimentos.filter(tipo='RECEBER').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
                
                trechos.append({
                    "titulo": f"Resumo do período ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})",
                    "texto": f"Total de Despesas: R$ {total_despesas:,.2f}\nTotal de Receitas: R$ {total_receitas:,.2f}\nQuantidade de movimentos: {movimentos.count()}"
                })
                
                # Detalhes dos principais movimentos
                for movimento in movimentos[:5]:
                    trechos.append({
                        "titulo": f"{movimento.tipo} - {movimento.pessoa.razao_social if movimento.pessoa else 'Sem pessoa'}",
                        "texto": f"Descrição: {movimento.descricao}\nValor: R$ {movimento.valor_total:,.2f}\nData: {movimento.data_emissao.strftime('%d/%m/%Y')}"
                    })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar por período", "texto": str(e)})
        
        return trechos
    
    def _buscar_valores(self, pergunta):
        """Busca valores e totais."""
        trechos = []
        
        try:
            # Buscar maiores despesas
            maiores_despesas = MovimentoContas.objects.filter(
                tipo='PAGAR'
            ).select_related('pessoa').order_by('-valor_total')[:5]
            
            if maiores_despesas:
                trechos.append({
                    "titulo": "Maiores Despesas",
                    "texto": "\n".join([
                        f"{d.pessoa.razao_social if d.pessoa else 'Sem pessoa'}: R$ {d.valor_total:,.2f}"
                        for d in maiores_despesas
                    ])
                })
            
            # Buscar maiores receitas
            maiores_receitas = MovimentoContas.objects.filter(
                tipo='RECEBER'
            ).select_related('pessoa').order_by('-valor_total')[:5]
            
            if maiores_receitas:
                trechos.append({
                    "titulo": "Maiores Receitas",
                    "texto": "\n".join([
                        f"{r.pessoa.razao_social if r.pessoa else 'Sem pessoa'}: R$ {r.valor_total:,.2f}"
                        for r in maiores_receitas
                    ])
                })
            
            # Totais gerais
            total_despesas = MovimentoContas.objects.filter(tipo='PAGAR').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
            total_receitas = MovimentoContas.objects.filter(tipo='RECEBER').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
            
            trechos.append({
                "titulo": "Totais Gerais",
                "texto": f"Total de Despesas: R$ {total_despesas:,.2f}\nTotal de Receitas: R$ {total_receitas:,.2f}"
            })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar valores", "texto": str(e)})
        
        return trechos
    
    def _buscar_pessoas(self, pergunta):
        """Busca informações sobre fornecedores e faturados."""
        trechos = []
        
        try:
            # Buscar fornecedores mais frequentes
            fornecedores = Pessoas.objects.filter(
                tipo='FORNECEDOR'
            ).annotate(
                total_despesas=Sum('movimentocontas__valor_total', filter=Q(movimentocontas__tipo='PAGAR'))
            ).order_by('-total_despesas')[:5]
            
            if fornecedores:
                trechos.append({
                    "titulo": "Principais Fornecedores",
                    "texto": "\n".join([
                        f"{f.razao_social}: R$ {f.total_despesas or 0:,.2f}"
                        for f in fornecedores if f.total_despesas
                    ])
                })
            
            # Buscar faturados mais frequentes
            faturados = Pessoas.objects.filter(
                tipo='FATURADO'
            ).annotate(
                total_receitas=Sum('movimentocontas__valor_total', filter=Q(movimentocontas__tipo='RECEBER'))
            ).order_by('-total_receitas')[:5]
            
            if faturados:
                trechos.append({
                    "titulo": "Principais Faturados",
                    "texto": "\n".join([
                        f"{f.razao_social}: R$ {f.total_receitas or 0:,.2f}"
                        for f in faturados if f.total_receitas
                    ])
                })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar pessoas", "texto": str(e)})
        
        return trechos
    
    def _buscar_classificacoes(self, pergunta):
        """Busca classificações de despesas/receitas."""
        trechos = []
        
        try:
            # Buscar classificações mais usadas
            classificacoes = Classificacao.objects.annotate(
                total_valor=Sum('movimentoclassificacao__valor_classificado')
            ).order_by('-total_valor')[:10]
            
            if classificacoes:
                trechos.append({
                    "titulo": "Classificações Mais Usadas",
                    "texto": "\n".join([
                        f"{c.descricao} ({c.tipo}): R$ {c.total_valor or 0:,.2f}"
                        for c in classificacoes if c.total_valor
                    ])
                })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar classificações", "texto": str(e)})
        
        return trechos
    
    def _buscar_descricoes(self, pergunta):
        """Busca por palavras-chave nas descrições."""
        trechos = []
        
        try:
            # Extrair palavras-chave da pergunta
            palavras_chave = [palavra for palavra in pergunta.split() 
                            if len(palavra) > 3 and palavra not in ['qual', 'quais', 'como', 'quando', 'onde']]
            
            if palavras_chave:
                # Criar query com OR para todas as palavras-chave
                query = Q()
                for palavra in palavras_chave:
                    query |= Q(descricao__icontains=palavra)
                
                movimentos = MovimentoContas.objects.filter(query).select_related('pessoa')[:10]
                
                if movimentos:
                    trechos.append({
                        "titulo": f"Movimentos relacionados a: {', '.join(palavras_chave[:3])}",
                        "texto": "\n".join([
                            f"{m.descricao[:50]}... - R$ {m.valor_total:,.2f}"
                            for m in movimentos
                        ])
                    })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar descrições", "texto": str(e)})
        
        return trechos
    
    def _buscar_movimentos_recentes(self):
        """Busca movimentos mais recentes."""
        trechos = []
        
        try:
            movimentos = MovimentoContas.objects.select_related('pessoa').order_by('-data_emissao')[:10]
            
            if movimentos:
                trechos.append({
                    "titulo": "Movimentos Recentes",
                    "texto": "\n".join([
                        f"{m.descricao[:40]}... - R$ {m.valor_total:,.2f} ({m.data_emissao.strftime('%d/%m')})"
                        for m in movimentos
                    ])
                })
            
        except Exception as e:
            trechos.append({"titulo": "Erro ao buscar movimentos recentes", "texto": str(e)})
        
        return trechos
    
    def gerar_resposta_llm(self, pergunta, trechos):
        """
        Gera resposta usando LLM baseada nos trechos encontrados.
        """
        if not trechos:
            return "Não encontrei informações relevantes no banco de dados para responder sua pergunta."
        
        try:
            # Construir contexto com os trechos
            contexto = "\n\n".join([
                f"**{trecho['titulo']}:**\n{trecho['texto']}"
                for trecho in trechos
            ])
            
            prompt = f"""
            Você é um assistente financeiro que analisa dados de notas fiscais e movimentos financeiros.
            
            Contexto dos dados encontrados:
            {contexto}
            
            Pergunta do usuário: {pergunta}
            
            Com base nos dados acima, forneça uma resposta clara e objetiva em português.
            Se os dados não forem suficientes para responder completamente, indique o que foi encontrado e o que falta.
            Use formato legível com valores em reais quando aplicável.
            """
            
            response = self.model.generate_content(prompt)
            resposta = response.text.strip()
            
            # Sanitizar resposta
            resposta = resposta.encode('utf-8', errors='ignore').decode('utf-8')
            
            return resposta
            
        except Exception as e:
            return f"Erro ao gerar resposta com IA: {str(e)}"
    
    def responder(self, pergunta):
        """
        Método principal para responder perguntas.
        """
        try:
            # Buscar trechos relevantes
            trechos = self.buscar_trechos_relevantes(pergunta)
            
            # Gerar resposta com LLM
            resposta = self.gerar_resposta_llm(pergunta, trechos)
            
            return {
                "resposta": resposta,
                "trechos": trechos
            }
            
        except Exception as e:
            return {
                "resposta": f"Erro ao processar pergunta: {str(e)}",
                "trechos": [],
                "erro": str(e)
            }