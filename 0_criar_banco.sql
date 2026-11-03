-- =============================================================
-- Fase 0 - Banco e tabelas (Arquitetura Medallion: Raw e Silver)
--
-- Como executar (no terminal):
--   sudo -u postgres psql -f 0_criar_banco.sql
--
-- A senha do usuário e demais credenciais ficam no arquivo .env
-- (nunca neste script).
-- =============================================================

-- Cria o database somente se ele ainda não existir
SELECT 'CREATE DATABASE portal_transparencia'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'portal_transparencia')
\gexec

-- Conecta ao database criado: as tabelas abaixo ficam nele
\c portal_transparencia


-- =============================================================
-- CAMADA RAW: cópia fiel dos CSVs (todas as colunas VARCHAR,
-- sem constraints)
-- =============================================================

CREATE TABLE IF NOT EXISTS raw_pagamento (
    "Identificador do processo de viagem" VARCHAR,
    "Número da Proposta (PCDP)" VARCHAR,
    "Código do órgão superior" VARCHAR,
    "Nome do órgão superior" VARCHAR,
    "Codigo do órgão pagador" VARCHAR,
    "Nome do órgao pagador" VARCHAR,
    "Código da unidade gestora pagadora" VARCHAR,
    "Nome da unidade gestora pagadora" VARCHAR,
    "Tipo de pagamento" VARCHAR,
    "Valor" VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_passagem (
    "Identificador do processo de viagem" VARCHAR,
    "Número da Proposta (PCDP)" VARCHAR,
    "Meio de transporte" VARCHAR,
    "País - Origem ida" VARCHAR,
    "UF - Origem ida" VARCHAR,
    "Cidade - Origem ida" VARCHAR,
    "País - Destino ida" VARCHAR,
    "UF - Destino ida" VARCHAR,
    "Cidade - Destino ida" VARCHAR,
    "País - Origem volta" VARCHAR,
    "UF - Origem volta" VARCHAR,
    "Cidade - Origem volta" VARCHAR,
    "Pais - Destino volta" VARCHAR,
    "UF - Destino volta" VARCHAR,
    "Cidade - Destino volta" VARCHAR,
    "Valor da passagem" VARCHAR,
    "Taxa de serviço" VARCHAR,
    "Data da emissão/compra" VARCHAR,
    "Hora da emissão/compra" VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_trecho (
    "Identificador do processo de viagem " VARCHAR,
    "Número da Proposta (PCDP)" VARCHAR,
    "Sequência Trecho" VARCHAR,
    "Origem - Data" VARCHAR,
    "Origem - País" VARCHAR,
    "Origem - UF" VARCHAR,
    "Origem - Cidade" VARCHAR,
    "Destino - Data" VARCHAR,
    "Destino - País" VARCHAR,
    "Destino - UF" VARCHAR,
    "Destino - Cidade" VARCHAR,
    "Meio de transporte" VARCHAR,
    "Número Diárias" VARCHAR,
    "Missao?" VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_viagem (
    "Identificador do processo de viagem" VARCHAR,
    "Número da Proposta (PCDP)" VARCHAR,
    "Situação" VARCHAR,
    "Viagem Urgente" VARCHAR,
    "Justificativa Urgência Viagem" VARCHAR,
    "Código do órgão superior" VARCHAR,
    "Nome do órgão superior" VARCHAR,
    "Código órgão solicitante" VARCHAR,
    "Nome órgão solicitante" VARCHAR,
    "CPF viajante" VARCHAR,
    "Nome" VARCHAR,
    "Cargo" VARCHAR,
    "Função" VARCHAR,
    "Descrição Função" VARCHAR,
    "Período - Data de início" VARCHAR,
    "Período - Data de fim" VARCHAR,
    "Destinos" VARCHAR,
    "Motivo" VARCHAR,
    "Valor diárias" VARCHAR,
    "Valor passagens" VARCHAR,
    "Valor devolução" VARCHAR,
    "Valor outros gastos" VARCHAR
);


-- =============================================================
-- CAMADA SILVER: dados tipados, com PK, FK e constraints
-- =============================================================

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
