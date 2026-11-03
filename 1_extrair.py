"""Etapa 1 do ETL: extração e carga da camada Raw.

- Baixa o arquivo .zip do Google Drive (se os CSVs ainda não estiverem em data/).
- Lê cada CSV em blocos e carrega na tabela Raw correspondente, sem alterar
  o conteúdo (tudo como texto).
- É idempotente: faz TRUNCATE da tabela antes de carregar, então reexecutar
  não duplica registros.

Pré-requisito: o banco e as tabelas já foram criados com 0_criar_banco.sql.
"""

import shutil
import sys
import zipfile
from io import StringIO
from pathlib import Path

import gdown
import pandas as pd

from banco import conectar
from config import DRIVE_FILE_ID

DATA_DIR = Path(__file__).resolve().parent / "data"
ZIP_PATH = DATA_DIR / "viagens_2025.zip"

CSV_SEP = ";"
CSV_ENCODING = "ISO-8859-1"
TAMANHO_BLOCO = 50_000

ARQUIVOS_E_TABELAS = {
    "2025_Viagem.csv": "raw_viagem",
    "2025_Pagamento.csv": "raw_pagamento",
    "2025_Passagem.csv": "raw_passagem",
    "2025_Trecho.csv": "raw_trecho",
}


def csvs_presentes() -> bool:
    """Verifica se os 4 CSVs já estão na pasta data/."""
    return all((DATA_DIR / nome).exists() for nome in ARQUIVOS_E_TABELAS)


def baixar_e_extrair() -> None:
    """Baixa o zip do Google Drive e extrai os CSVs para data/."""
    DATA_DIR.mkdir(exist_ok=True)

    if csvs_presentes():
        print("CSVs já estão em data/; download ignorado.")
        return

    print("Baixando o arquivo zip do Google Drive...")
    resultado = gdown.download(
        id=DRIVE_FILE_ID, output=str(ZIP_PATH), quiet=False
    )
    if resultado is None:
        raise RuntimeError(
            "Falha no download. Confira o DRIVE_FILE_ID no config.py e se "
            "o arquivo está compartilhado publicamente."
        )

    print("Extraindo os CSVs...")
    with zipfile.ZipFile(ZIP_PATH) as zip_file:
        for membro in zip_file.namelist():
            nome = Path(membro).name
            if nome in ARQUIVOS_E_TABELAS:
                with zip_file.open(membro) as origem:
                    with open(DATA_DIR / nome, "wb") as destino:
                        shutil.copyfileobj(origem, destino)

    faltantes = [n for n in ARQUIVOS_E_TABELAS if not (DATA_DIR / n).exists()]
    if faltantes:
        raise FileNotFoundError(
            f"Arquivos não encontrados dentro do zip: {faltantes}"
        )


def carregar_raw(conn, arquivo: str, tabela: str) -> int:
    """Carrega um CSV na tabela Raw, em blocos. Retorna o total de linhas."""
    caminho = DATA_DIR / arquivo
    total = 0

    with conn.cursor() as cursor:
        # Idempotência: limpa a tabela antes de carregar
        cursor.execute(f"TRUNCATE TABLE {tabela};")

        blocos = pd.read_csv(
            caminho,
            sep=CSV_SEP,
            encoding=CSV_ENCODING,
            dtype=str,
            keep_default_na=False,
            chunksize=TAMANHO_BLOCO,
        )

        for bloco in blocos:
            colunas = ", ".join(
                '"' + coluna.replace('"', '""') + '"'
                for coluna in bloco.columns
            )
            buffer = StringIO()
            bloco.to_csv(buffer, index=False, header=False)
            buffer.seek(0)
            cursor.copy_expert(
                f"COPY {tabela} ({colunas}) FROM STDIN WITH (FORMAT CSV)",
                buffer,
            )
            total += len(bloco)

    conn.commit()
    return total


def main() -> int:
    """Executa a extração e a carga Raw. Retorna 0 em sucesso, 1 em falha."""
    try:
        baixar_e_extrair()
    except Exception as erro:
        print(f"Erro na extração: {erro}")
        return 1

    conn = None
    falhas = []

    try:
        conn = conectar()
        for arquivo, tabela in ARQUIVOS_E_TABELAS.items():
            try:
                print(f"Carregando {arquivo} em {tabela}...")
                total = carregar_raw(conn, arquivo, tabela)
                print(f"{tabela}: {total} registros carregados")
            except Exception as erro:
                conn.rollback()
                falhas.append(tabela)
                print(f"Erro ao carregar {tabela}: {erro}")
    except Exception as erro:
        print(f"Erro de conexão com o banco: {erro}")
        return 1
    finally:
        if conn is not None:
            conn.close()

    if falhas:
        print(f"\nCarga incompleta. Tabelas com erro: {falhas}")
        return 1

    print("\nCamada Raw carregada com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
