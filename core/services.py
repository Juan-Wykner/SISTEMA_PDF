import os
from typing import Any, Dict

import pdfplumber

from .agents.agent_1 import AgenteGemini


class ProcessadorPDF:
    """
    Responsável por extrair texto de um arquivo PDF.

    SRP: não realiza parsing semântico nem classificação; apenas leitura.
    """

    def extrair_texto_pdf(self, pdf_path: str) -> str:
        """Extrai texto bruto de todas as páginas de um PDF."""
        texto: str = ""
        try:
            # Verificar se o arquivo existe e é legível
            if not os.path.exists(pdf_path):
                return ""
                
            # Verificar se é um arquivo PDF válido lendo os primeiros bytes
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return ""
            
            # Tentar abrir o PDF com tratamento robusto de erros
            with pdfplumber.open(pdf_path) as pdf:
                for pagina in pdf.pages:
                    try:
                        txt = pagina.extract_text() or ""
                    except Exception:
                        txt = ""
                    if txt:
                        texto += txt + "\n"
                        
        except (FileNotFoundError, UnicodeDecodeError, Exception):
            # Captura todos os erros possíveis
            return ""

        return texto.strip()


def processar_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Orquestra a extração de texto e delega a análise ao agente LLM.

    Args:
        pdf_path: Caminho do arquivo PDF a ser processado.

    Returns:
        Dicionário com dados extraídos do PDF.
    """
    try:
        processador = ProcessadorPDF()
        agente = AgenteGemini()
        texto = processador.extrair_texto_pdf(pdf_path)
        if not texto:
            return {"erro": "Não foi possível extrair texto do PDF. O arquivo pode estar corrompido ou não ser um PDF válido."}

        dados_extraidos = agente.extrair_dados(texto)
        return dados_extraidos
    except Exception as e:
        return {"erro": "Erro ao processar o PDF", "detalhes": str(e)}
