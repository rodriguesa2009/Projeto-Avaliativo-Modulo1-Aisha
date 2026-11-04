# -*- coding: utf-8 -*-
"""Módulo 1 - Projeto Avaliativo

Transforma os dados das tabelas Raw para as tabelas Silver no PostgreSQL.
A extração e a carga das tabelas Raw são realizadas pelo script 1_extrair.py.
"""

import psycopg2
from config import POSTGRES_CONFIG


def criar_tabelas_silver(cursor):
    """Cria as tabelas Silver caso ainda não existam."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver_viagem (
            id_viagem VARCHAR(100) PRIMARY KEY NOT NULL,
            num_proposta VARCHAR(50),
            situacao VARCHAR(50),
            viagem_urgente VARCHAR(10),
            codigo_orgao_superior VARCHAR(50),
            nome_orgao_superior VARCHAR(255) NOT NULL,
            nome_viajante VARCHAR(255),
            cargo VARCHAR(255),
            data_inicio DATE,
            data_fim DATE,
            destinos VARCHAR(4000),
            motivo VARCHAR(4000),
            valor_diarias DECIMAL(12,2) CHECK (valor_diarias >= 0),
            valor_passagens DECIMAL(12,2) CHECK (valor_passagens >= 0),
            valor_devolucao DECIMAL(12,2) CHECK (valor_devolucao >= 0),
            valor_outros_gastos DECIMAL(12,2) CHECK (valor_outros_gastos >= 0),
            valor_total DECIMAL(14,2),
            duracao_dias INT CHECK (duracao_dias >= 0)
        );

        CREATE TABLE IF NOT EXISTS silver_pagamento (
            id_pagamento SERIAL PRIMARY KEY,
            id_viagem VARCHAR(100) NOT NULL REFERENCES silver_viagem(id_viagem),
            num_proposta VARCHAR(50),
            nome_orgao_pagador VARCHAR(255),
            nome_ug_pagadora VARCHAR(255),
            tipo_pagamento VARCHAR(100) NOT NULL,
            valor DECIMAL(12,2) CHECK (valor >= 0)
        );

        CREATE TABLE IF NOT EXISTS silver_passagem (
            id_passagem SERIAL PRIMARY KEY,
            id_viagem VARCHAR(100) NOT NULL REFERENCES silver_viagem(id_viagem),
            meio_transporte VARCHAR(100),
            pais_origem_ida VARCHAR(100),
            uf_origem_ida VARCHAR(100),
            cidade_origem_ida VARCHAR(150),
            pais_destino_ida VARCHAR(100),
            uf_destino_ida VARCHAR(100),
            cidade_destino_ida VARCHAR(150),
            valor_passagem DECIMAL(12,2) CHECK (valor_passagem >= 0),
            taxa_servico DECIMAL(12,2) CHECK (taxa_servico >= 0),
            data_emissao DATE
        );

        CREATE TABLE IF NOT EXISTS silver_trecho (
            id_trecho SERIAL PRIMARY KEY,
            id_viagem VARCHAR(100) NOT NULL REFERENCES silver_viagem(id_viagem),
            sequencia_trecho INT,
            origem_data DATE,
            origem_uf VARCHAR(100),
            origem_cidade VARCHAR(150),
            destino_data DATE,
            destino_uf VARCHAR(100),
            destino_cidade VARCHAR(150),
            meio_transporte VARCHAR(100),
            numero_diarias DECIMAL(12,2) CHECK (numero_diarias >= 0),
            UNIQUE (id_viagem, sequencia_trecho)
        );
    """)


def transformar_dados():
    """Lê as tabelas Raw e carrega os dados tratados nas tabelas Silver."""
    conn = None

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        criar_tabelas_silver(cursor)

        # Limpa somente as tabelas Silver. As tabelas Raw são preservadas.
        cursor.execute("""
            TRUNCATE TABLE
                silver_pagamento,
                silver_passagem,
                silver_trecho,
                silver_viagem
            RESTART IDENTITY CASCADE;
        """)

        cursor.execute("""
            INSERT INTO silver_viagem (
                id_viagem, num_proposta, situacao, viagem_urgente,
                codigo_orgao_superior, nome_orgao_superior, nome_viajante,
                cargo, data_inicio, data_fim, destinos, motivo,
                valor_diarias, valor_passagens, valor_devolucao,
                valor_outros_gastos, valor_total, duracao_dias
            )
            SELECT
                TRIM(rv."Identificador do processo de viagem"),
                TRIM(rv."Número da Proposta (PCDP)"),
                TRIM(rv."Situação"),
                TRIM(rv."Viagem Urgente"),
                TRIM(rv."Código do órgão superior"),
                TRIM(rv."Nome do órgão superior"),
                TRIM(rv."Nome"),
                TRIM(rv."Cargo"),
                TO_DATE(NULLIF(TRIM(rv."Período - Data de início"), ''), 'DD/MM/YYYY'),
                TO_DATE(NULLIF(TRIM(rv."Período - Data de fim"), ''), 'DD/MM/YYYY'),
                TRIM(rv."Destinos"),
                TRIM(rv."Motivo"),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor diárias"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor passagens"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor devolução"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor outros gastos"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                COALESCE(CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor diárias"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)), 0)
                + COALESCE(CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor passagens"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)), 0)
                + COALESCE(CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor outros gastos"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)), 0)
                - COALESCE(CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rv."Valor devolução"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)), 0),
                TO_DATE(NULLIF(TRIM(rv."Período - Data de fim"), ''), 'DD/MM/YYYY')
                - TO_DATE(NULLIF(TRIM(rv."Período - Data de início"), ''), 'DD/MM/YYYY')
            FROM "2025_Viagem" rv
            WHERE NULLIF(TRIM(rv."Identificador do processo de viagem"), '') IS NOT NULL
              AND NULLIF(TRIM(rv."Nome do órgão superior"), '') IS NOT NULL
            ON CONFLICT (id_viagem) DO NOTHING;
        """)

        cursor.execute("""
            INSERT INTO silver_trecho (
                id_viagem, sequencia_trecho, origem_data, origem_uf,
                origem_cidade, destino_data, destino_uf, destino_cidade,
                meio_transporte, numero_diarias
            )
            SELECT
                TRIM(rt."Identificador do processo de viagem "),
                CAST(NULLIF(TRIM(rt."Sequência Trecho"), '') AS INT),
                TO_DATE(NULLIF(TRIM(rt."Origem - Data"), ''), 'DD/MM/YYYY'),
                TRIM(rt."Origem - UF"),
                TRIM(rt."Origem - Cidade"),
                TO_DATE(NULLIF(TRIM(rt."Destino - Data"), ''), 'DD/MM/YYYY'),
                TRIM(rt."Destino - UF"),
                TRIM(rt."Destino - Cidade"),
                TRIM(rt."Meio de transporte"),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rt."Número Diárias"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2))
            FROM "2025_Trecho" rt
            INNER JOIN silver_viagem sv
                ON TRIM(rt."Identificador do processo de viagem ") = sv.id_viagem
            WHERE NULLIF(TRIM(rt."Sequência Trecho"), '') IS NOT NULL
            ON CONFLICT (id_viagem, sequencia_trecho) DO NOTHING;
        """)

        cursor.execute("""
            INSERT INTO silver_pagamento (
                id_viagem, num_proposta, nome_orgao_pagador,
                nome_ug_pagadora, tipo_pagamento, valor
            )
            SELECT
                TRIM(rp."Identificador do processo de viagem"),
                TRIM(rp."Número da Proposta (PCDP)"),
                TRIM(rp."Nome do órgao pagador"),
                TRIM(rp."Nome da unidade gestora pagadora"),
                TRIM(rp."Tipo de pagamento"),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rp."Valor"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2))
            FROM "2025_Pagamento" rp
            INNER JOIN silver_viagem sv
                ON TRIM(rp."Identificador do processo de viagem") = sv.id_viagem
            WHERE NULLIF(TRIM(rp."Tipo de pagamento"), '') IS NOT NULL;
        """)

        cursor.execute("""
            INSERT INTO silver_passagem (
                id_viagem, meio_transporte, pais_origem_ida,
                uf_origem_ida, cidade_origem_ida, pais_destino_ida,
                uf_destino_ida, cidade_destino_ida, valor_passagem,
                taxa_servico, data_emissao
            )
            SELECT
                TRIM(rpa."Identificador do processo de viagem"),
                TRIM(rpa."Meio de transporte"),
                TRIM(rpa."País - Origem ida"),
                TRIM(rpa."UF - Origem ida"),
                TRIM(rpa."Cidade - Origem ida"),
                TRIM(rpa."País - Destino ida"),
                TRIM(rpa."UF - Destino ida"),
                TRIM(rpa."Cidade - Destino ida"),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rpa."Valor da passagem"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                CAST(NULLIF(REPLACE(REPLACE(NULLIF(TRIM(rpa."Taxa de serviço"), ''), '.', ''), ',', '.'), '') AS DECIMAL(12,2)),
                TO_DATE(NULLIF(TRIM(rpa."Data da emissão/compra"), ''), 'DD/MM/YYYY')
            FROM "2025_Passagem" rpa
            INNER JOIN silver_viagem sv
                ON TRIM(rpa."Identificador do processo de viagem") = sv.id_viagem;
        """)

        conn.commit()
        print("Transformação concluída: dados Raw tratados e carregados nas tabelas Silver.")

    except Exception:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if conn is not None:
            conn.close()


def verificar_contagens():
    """Mostra a quantidade de registros nas tabelas Raw e Silver."""
    tabelas = [
        '"2025_Viagem"',
        '"2025_Pagamento"',
        '"2025_Passagem"',
        '"2025_Trecho"',
        "silver_viagem",
        "silver_pagamento",
        "silver_passagem",
        "silver_trecho",
    ]

    conn = None
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        with conn.cursor() as cursor:
            for tabela in tabelas:
                # Os nomes das tabelas são fixos e definidos neste próprio script.
                cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
                quantidade = cursor.fetchone()[0]
                print(f"{tabela}: {quantidade} registros")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    transformar_dados()
    verificar_contagens()
