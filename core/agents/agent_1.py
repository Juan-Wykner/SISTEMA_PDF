import json
import google.generativeai as genai
from decouple import config


class AgenteGemini:
    def __init__(self):
        # Usa apenas GEMINI_API_KEY do .env
        api_key = config("GEMINI_API_KEY", default=None)
        if not api_key:
            raise ValueError("Defina GEMINI_API_KEY no .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def extrair_dados(self, texto_pdf: str):
        # Sanitizar o texto de entrada para garantir UTF-8 válido
        def sanitizar_texto(texto):
            """Remove caracteres problemáticos e garante UTF-8 válido."""
            if not texto:
                return ""
            try:
                # Remove caracteres de controle e garante UTF-8
                texto_limpo = texto.encode('utf-8', errors='ignore').decode('utf-8')
                return texto_limpo.strip()
            except Exception:
                return ""
        
        # Sanitizar o texto do PDF
        texto_pdf = sanitizar_texto(texto_pdf)
        
        # Prompt direto e restritivo para garantir saída somente em JSON
        categorias = (
            "PRINCIPAIS CATEGORIAS DE DESPESAS:\n"
            "INSUMOS AGRÍCOLAS: Sementes; Fertilizantes; Defensivos Agrícolas; Corretivos.\n"
            "MANUTENÇÃO E OPERAÇÃO: Combustíveis e Lubrificantes; Peças/Parafusos/Componentes Mecânicos; "
            "Manutenção de Máquinas e Equipamentos; Pneus; Filtros; Correias; Ferramentas e Utensílios.\n"
            "RECURSOS HUMANOS: Mão de Obra Temporária; Salários e Encargos.\n"
            "SERVIÇOS OPERACIONAIS: Frete e Transporte; Colheita Terceirizada; Secagem e Armazenagem; "
            "Pulverização e Aplicação.\n"
            "INFRAESTRUTURA E UTILIDADES: Energia Elétrica; Arrendamento de Terras; Construções e Reformas; "
            "Materiais de Construção.\n"
            "ADMINISTRATIVAS: Honorários (Contábeis, Advocatícios, Agronômicos); Despesas Bancárias e Financeiras.\n"
            "SEGUROS E PROTEÇÃO: Seguro Agrícola; Seguro de Ativos (Máquinas/Veículos); Seguro Prestamista.\n"
            "IMPOSTOS E TAXAS: ITR; IPTU; IPVA; INCRA-CCIR.\n"
            "INVESTIMENTOS: Aquisição de Máquinas e Implementos; Aquisição de Veículos; Aquisição de Imóveis; "
            "Infraestrutura Rural.\n"
        )

        esquema = (
            "Retorne APENAS um JSON válido (sem markdown, sem explicações, sem texto extra) no formato EXATO:\n"
            "{\n"
            "  \"fornecedor\": {\"razao_social\": \"\", \"nome_fantasia\": \"\", \"cnpj\": \"\"},\n"
            "  \"faturado\": {\"nome_completo\": \"\", \"cpf\": \"\"},\n"
            "  \"numero_nota_fiscal\": \"\",\n"
            "  \"data_emissao\": \"\",\n"
            "  \"descricao_produtos\": [],\n"
            "  \"quantidade_parcelas\": 1,\n"
            "  \"data_vencimento\": \"\",\n"
            "  \"valor_total\": \"\",\n"
            "  \"classificacao_despesa\": []\n"
            "}\n"
            "Regras:\n"
            "- Preencha com string vazia (\"\"), lista vazia ([]) ou número conforme o tipo quando faltar informação.\n"
            "- \"classificacao_despesa\" deve conter UMA OU MAIS categorias principais listadas acima, escolhidas de acordo com as descrições dos produtos.\n"
            "- Não inclua subcategorias na saída; use-as apenas como referência para escolher as categorias principais.\n"
        )

        prompt = (
            "Você é um extrator de dados de DANFE.\n\n" +
            categorias + "\n" + esquema + "\n" +
            "Texto da nota a analisar:\n" + texto_pdf
        )

        try:
            # Sanitizar o prompt antes de enviar
            prompt = sanitizar_texto(prompt)
            
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            
            # Verificação de segurança e conteúdo
            if not raw or getattr(response.prompt_feedback, 'block_reason', None):
                return {"erro": "Resposta inválida ou bloqueada"}
            
            # Sanitizar a resposta
            raw = sanitizar_texto(raw)
            
            # Parse do JSON
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                start, end = raw.find("{"), raw.rfind("}")
                if start >= 0 and end > start:
                    json_str = raw[start:end+1]
                    # Sanitizar o JSON extraído
                    json_str = sanitizar_texto(json_str)
                    return json.loads(json_str)
                return {"erro": "JSON inválido", "resposta_bruta": raw[:400]}

        except Exception as e:
            return {"erro": "Falha na consulta", "detalhes": str(e)}