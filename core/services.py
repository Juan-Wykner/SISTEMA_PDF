import pdfplumber
from typing import Any, Dict

from .agents.agent_1 import AgenteGemini


class ProcessadorPDF:
    def extrair_texto_pdf(self, pdf_path: str) -> str:
        texto = ""
        with pdfplumber.open(pdf_path) as pdf:
            for pagina in pdf.pages:
                try:
                    txt = pagina.extract_text() or ""
                except Exception:
                    txt = ""
                if txt:
                    texto += txt + "\n"
        return texto.strip()


def processar_pdf(pdf_path: str) -> Dict[str, Any]:
    processador = ProcessadorPDF()
    agente = AgenteGemini()
    texto = processador.extrair_texto_pdf(pdf_path)
    dados = agente.extrair_dados(texto)
    return dados
