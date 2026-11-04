-- =============================================================
-- Fase 0 - Tabelas espelho dos CSVs de origem (PostgreSQL)
--
-- Quatro tabelas, uma por arquivo CSV, com os nomes das colunas
-- exatamente como estão no cabeçalho de cada arquivo. Todas as
-- colunas são VARCHAR, sem constraints, para preservar o texto
-- original (zeros à esquerda, vírgulas decimais, datas DD/MM/AAAA).
--
-- Como os nomes começam com número, ficam sempre entre aspas
-- duplas: "2025_Viagem".
--
-- Como executar (o banco portal_transparencia já deve existir):
--   PGPASSWORD=teste123 psql -h localhost -U postgres \
--       -d portal_transparencia -f 0_criar_banco.sql
-- =============================================================

-- 2025_Pagamento.csv: 10 colunas
CREATE TABLE IF NOT EXISTS public."2025_Pagamento" (
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

-- 2025_Passagem.csv: 19 colunas
CREATE TABLE IF NOT EXISTS public."2025_Passagem" (
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

-- 2025_Trecho.csv: 14 colunas
-- O espaço no fim do primeiro cabeçalho é intencional: ele existe
-- no CSV original e foi preservado.
CREATE TABLE IF NOT EXISTS public."2025_Trecho" (
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

-- 2025_Viagem.csv: 22 colunas
CREATE TABLE IF NOT EXISTS public."2025_Viagem" (
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
