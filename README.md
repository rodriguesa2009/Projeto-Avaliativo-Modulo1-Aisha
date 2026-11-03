# Projeto Avaliativo – Análise de Dados com Python

## 1. Sobre o projeto

Este projeto foi desenvolvido como parte do Projeto Avaliativo do Módulo 1 do curso de Análise de Dados com Python.

O objetivo é construir um pipeline de dados utilizando Python e SQL, aplicando a arquitetura Medallion para extrair, transformar, organizar e analisar dados relacionados a viagens, passagens, trechos e pagamentos.

A proposta é transformar os dados brutos em informações estruturadas que permitam responder a perguntas de negócio e gerar indicadores relevantes.

## 2. Ambiente de desenvolvimento

O projeto foi inicialmente desenvolvido no **Google Colab**, ambiente que permite escrever e executar códigos Python diretamente no navegador, utilizando notebooks.

Posteriormente, os arquivos foram organizados em um repositório no GitHub para facilitar o versionamento, a documentação e o acompanhamento do desenvolvimento.

O projeto também utiliza arquivos Python, SQL e Jupyter Notebook para organizar as diferentes etapas do pipeline.

## 3. Tecnologias utilizadas

- **Python:** linguagem utilizada para extração, transformação e análise dos dados.
- **Pandas:** biblioteca utilizada para manipulação e análise de dados.
- **SQL:** linguagem utilizada para criação e consulta das tabelas do banco de dados.
- **MySQL ou PostgreSQL:** sistema gerenciador de banco de dados.
- **Jupyter Notebook:** ambiente utilizado para documentar e executar as análises.
- **Google Colab:** ambiente utilizado inicialmente no desenvolvimento.
- **Git e GitHub:** ferramentas utilizadas para versionamento e armazenamento do projeto.

## 4. Conjuntos de dados

O projeto utiliza quatro arquivos CSV:

| Arquivo | Descrição |
|---|---|
| `2025_Pagamento.csv` | Informações relacionadas aos pagamentos. |
| `2025_Passagem.csv` | Informações relacionadas às passagens. |
| `2025_Trecho.csv` | Informações relacionadas aos trechos das viagens. |
| `2025_Viagem.csv` | Informações relacionadas às viagens. |

Os arquivos possuem as seguintes características:

- Separador de colunas: ponto e vírgula (`;`).
- Codificação: `latin-1`.
- Separador decimal: vírgula.
- Formato de data: `DD/MM/AAAA`.

Os quatro conjuntos de dados são utilizados nas etapas de extração, transformação e análise.

## 5. Arquitetura Medallion

O pipeline utiliza a arquitetura Medallion, organizada em três camadas:

### Raw – Dados brutos

É a camada responsável por armazenar os dados originais, preservando seu conteúdo durante a extração.

### Silver – Dados tratados

É a camada responsável pela limpeza e transformação dos dados. Nessa etapa são realizadas conversões de tipos, verificações de integridade e cálculos necessários.

### Gold – Dados analíticos

É a camada destinada à organização dos dados para análises de negócio. Utiliza consultas SQL, relacionamentos entre tabelas, agrupamentos e indicadores.

## 6. Estrutura do projeto

```text
Projeto-Avaliativo-Modulo1-Aisha/
│
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── 3_analise.ipynb
│
├── config.py
├── banco.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── data/
```

### Descrição dos arquivos

- `0_criar_banco.sql`: criação do banco de dados e das tabelas das camadas Raw e Silver.
- `1_extrair.py`: extração dos arquivos CSV e carregamento dos dados na camada Raw.
- `2_transformar.py`: tratamento e transformação dos dados da camada Raw para a camada Silver.
- `3_analise.ipynb`: realização das consultas, análises e visualizações dos dados.
- `config.py`: organização das configurações e leitura das variáveis de ambiente.
- `banco.py`: funções auxiliares para conexão e operações com o banco de dados.
- `requirements.txt`: lista de dependências necessárias para executar o projeto.
- `.env.example`: modelo das variáveis de ambiente necessárias para a configuração.
- `.gitignore`: definição dos arquivos e diretórios que não devem ser enviados ao GitHub.

## 7. Etapas de desenvolvimento

O desenvolvimento está dividido em quatro etapas principais:

1. **Criação do banco de dados:** preparação da estrutura do banco e das tabelas.
2. **Extração:** leitura dos arquivos CSV e carregamento dos dados na camada Raw.
3. **Transformação:** tratamento dos dados e carregamento na camada Silver.
4. **Análise:** consultas SQL, criação de indicadores e visualizações na camada Gold.

## 8. Perguntas de negócio

O projeto busca responder às seguintes perguntas:

1. Quais são as cinco agências com maior custo total?
2. Quais são os três destinos com maior custo médio por viagem?
3. Qual foi a viagem mais longa e qual foi seu custo total?
4. Qual tipo de pagamento apresenta o maior valor médio?
5. Qual é o meio de transporte mais utilizado nos trechos?
6. Qual UF de destino aparece na maior quantidade de trechos?
7. Qual agência realizou o maior pagamento no total?

As respostas são obtidas por meio da análise dos dados e da utilização de consultas SQL.

## 9. Como executar o projeto

### Pré-requisitos

Antes de executar o projeto, é necessário ter:

- Python instalado.
- MySQL ou PostgreSQL configurado.
- Bibliotecas Python necessárias instaladas.
- Acesso ao arquivo ZIP contendo os conjuntos de dados.
- Configurações de conexão com o banco de dados.

### Instalação das dependências

No terminal, execute:

```bash
pip install -r requirements.txt
```

### Configuração do ambiente

1. Utilize o arquivo `.env.example` como modelo.
2. Crie um arquivo `.env` com as configurações necessárias.
3. Informe as credenciais e os parâmetros de conexão do banco de dados.
4. Configure o identificador do arquivo ZIP disponibilizado no Google Drive, quando necessário.

**Importante:** o arquivo `.env` contém informações privadas e não deve ser enviado ao GitHub.

### Ordem de execução

Execute os arquivos na seguinte ordem:

```text
1. 0_criar_banco.sql
2. 1_extrair.py
3. 2_transformar.py
4. 3_analise.ipynb
```

Essa sequência garante que o banco de dados seja preparado antes da extração, transformação e análise das informações.

## 10. Possíveis melhorias

Como possíveis melhorias futuras, destacam-se:

- Automatização da execução do pipeline.
- Implementação de testes automatizados para validar os dados.
- Criação de dashboards interativos.
- Aprimoramento do tratamento de dados ausentes e inconsistentes.
- Monitoramento de erros durante as etapas de extração e transformação.
- Desenvolvimento de novas consultas e indicadores de negócio.

## 11. Conclusão

O projeto permite aplicar conceitos de programação em Python, manipulação de dados, banco de dados relacionais, consultas SQL e visualização de informações.

A utilização da arquitetura Medallion organiza o fluxo de dados em etapas, facilitando o tratamento e a análise das informações.

Além disso, o projeto proporciona experiência prática na construção de um pipeline de dados, desde a extração dos arquivos originais até a geração de informações úteis para apoiar decisões de negócio.

---

**Projeto desenvolvido para fins acadêmicos – Análise de Dados com Python, Módulo 1.**
