
"""
Etapa 1 do ETL: extração e carga das tabelas espelho.

- Baixa o arquivo ZIP do Google Drive, se os CSVs ainda não
  estiverem disponíveis em data/.
- Extrai os quatro CSVs originais.
- Carrega cada CSV na tabela PostgreSQL correspondente,
  preservando os valores como texto.
- É idempotente: limpa a tabela antes de carregar novamente.

Pré-requisito: o banco e as quatro tabelas espelho foram
criados previamente pelo script SQL da fase Extrair.
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
    "2025_Viagem.csv": "2025_Viagem",
    "2025_Pagamento.csv": "2025_Pagamento",
    "2025_Passagem.csv": "2025_Passagem",
    "2025_Trecho.csv": "2025_Trecho",
}


def csvs_presentes() -> bool:
    """Verifica se os quatro CSVs já estão na pasta data/."""
    return all((DATA_DIR / nome).exists() for nome in ARQUIVOS_E_TABELAS)


def baixar_e_extrair() -> None:
    """Baixa o ZIP e extrai os quatro CSVs para data/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if csvs_presentes():
        print("CSVs já estão em data/; download ignorado.")
        return

    print("Baixando o arquivo ZIP do Google Drive...")

    resultado = gdown.download(
        id=DRIVE_FILE_ID,
        output=str(ZIP_PATH),
        quiet=False
    )

    if resultado is None:
        raise RuntimeError(
            "Falha no download. Confira o DRIVE_FILE_ID no config.py "
            "e se o arquivo está compartilhado publicamente."
        )

    print("Extraindo os CSVs...")

    with zipfile.ZipFile(ZIP_PATH) as zip_file:
        for membro in zip_file.namelist():
            nome = Path(membro).name

            if nome in ARQUIVOS_E_TABELAS:
                with zip_file.open(membro) as origem:
                    with open(DATA_DIR / nome, "wb") as destino:
                        shutil.copyfileobj(origem, destino)

    faltantes = [
        nome for nome in ARQUIVOS_E_TABELAS
        if not (DATA_DIR / nome).exists()
    ]

    if faltantes:
        raise FileNotFoundError(
            f"Arquivos não encontrados dentro do ZIP: {faltantes}"
        )


def carregar_tabela(conn, arquivo: str, tabela: str) -> int:
    """Carrega um CSV na tabela espelho, em blocos."""

    caminho = DATA_DIR / arquivo
    total = 0

    with conn.cursor() as cursor:

        # Limpa a tabela para evitar duplicação na reexecução.
        # As aspas preservam exatamente o nome da tabela.
        cursor.execute(f'TRUNCATE TABLE "{tabela}";')

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
                f'COPY "{tabela}" ({colunas}) '
                "FROM STDIN WITH (FORMAT CSV)",
                buffer,
            )

            total += len(bloco)

    conn.commit()
    return total


def main() -> int:
    """Executa a extração e a carga das quatro tabelas."""

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

                total = carregar_tabela(conn, arquivo, tabela)

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

    print("\nTabelas espelho carregadas com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

