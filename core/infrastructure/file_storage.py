from __future__ import annotations

import os
from typing import IO


def save_uploaded_to_temp(uploaded_file: IO[bytes], media_root: str, filename: str) -> str:
    """
    Salva um arquivo enviado (upload) em uma pasta temporária dentro de MEDIA_ROOT.

    Responsabilidade: lidar somente com escrita de arquivo em disco (SRP).

    Args:
        uploaded_file: Arquivo vindo de request.FILES.
        media_root: Diretório base configurado em MEDIA_ROOT.
        filename: Nome do arquivo a ser utilizado na escrita temporária.

    Returns:
        Caminho absoluto do arquivo temporário salvo.
    """
    temp_dir = os.path.join(media_root, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return temp_path


def save_uploaded_to_temp_safe(uploaded_file: IO[bytes], media_root: str, filename: str) -> str:
    """
    Versão melhorada que garante tratamento binário seguro de arquivos.
    
    Args:
        uploaded_file: Arquivo vindo de request.FILES.
        media_root: Diretório base configurado em MEDIA_ROOT.
        filename: Nome do arquivo a ser utilizado na escrita temporária.

    Returns:
        Caminho absoluto do arquivo temporário salvo.
    """
    temp_dir = os.path.join(media_root, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)

    # Garantir que o arquivo seja tratado como binário
    try:
        with open(temp_path, "wb+") as destination:
            # Processar em chunks para arquivos grandes
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    except Exception as e:
        # Se houver erro, tentar remover o arquivo parcial
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        raise Exception(f"Erro ao salvar arquivo temporário: {str(e)}")

    return temp_path


def remove_file_safely(path: str) -> None:
    """
    Remove um arquivo do disco silenciosamente, sem lançar exceções.

    Responsabilidade: remoção de arquivo sem afetar fluxo da aplicação.
    """
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        # Intencionalmente silencioso: log pode ser adicionado futuramente.
        pass