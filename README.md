# Desafio Engenheiro de Dados 2025

Este projeto implementa uma solução completa para os desafios de engenharia de dados focados em **sistemas de restaurante**, demonstrando análise de esquemas JSON, modelagem relacional, arquitetura de data lake e pipeline ETL.

## Desafios Implementados

### **Desafio 1: Análise e Modelagem JSON → SQL**
- **Análise de esquema JSON** do sistema ERP de restaurante
- **Modelagem relacional normalizada** (3NF) com 8 tabelas
- **Script DDL completo** para criação das tabelas
- **Documentação técnica** detalhada da abordagem

### **Desafio 2: Data Lake e Pipeline de APIs**
- **Arquitetura de data lake** com padrão Medallion
- **Particionamento hierárquico** por data e loja
- **Sistema de metadados** para auditoria e rastreabilidade
- **Estratégia de evolução de schema** com versionamento automático

## Tecnologias Utilizadas

- **Python 3.11+** - Linguagem principal
- **Pandas** - Manipulação e análise de dados
- **Streamlit** - Dashboard web interativo
- **Plotly** - Visualizações interativas
- **JSON** - Formato de dados e metadados
- **SQL** - Modelagem relacional

## Estrutura do Projeto

```
desafio-engenheiro-dados/
├── dados/                          # Dados e data lake
│   ├── ERP.json                   # Dados reais do sistema ERP
│   ├── data_lake/                 # Data lake estruturado
│   │   ├── dados_brutos/          # Raw data (5 endpoints)
│   │   ├── dados_processados/     # Processed data
│   │   ├── esquemas/              # Schema definitions
│   │   └── metadados/             # Metadata store
│   ├── vendas_processadas.csv     # Dados transformados
│   └── metricas_calculadas.csv    # Métricas de negócio
├── src/                           # Código fonte
│   ├── desafio1/                  # Análise JSON → SQL
│   │   ├── analisador_esquema.py  # Análise de esquema
│   │   └── modelador_sql.py       # Modelagem relacional
│   ├── desafio2/                  # Data lake e APIs
│   │   └── gerenciador_data_lake.py # Gerenciamento do data lake
│   ├── extrair.py                 # Extração de dados
│   ├── transformar.py             # Transformação e limpeza
│   └── analisar.py                # Análise e visualização
├── docs/                          # Documentação técnica
│   ├── analise_esquema.json       # Análise automatizada
│   ├── modelo_relacional.json     # Modelo normalizado
│   ├── documentacao_data_lake.json # Documentação do data lake
│   ├── solucao_desafio1.md        # Solução detalhada D1
│   └── solucao_desafio2.md        # Solução detalhada D2
├── sql/                           # Scripts SQL
│   └── criar_tabelas.sql          # DDL das 8 tabelas
├── testes/                        # Testes automatizados
│   └── teste_integracao.py        # Suite de testes
├── app_streamlit.py               # Dashboard interativo
├── principal.py                   # Pipeline principal
└── requirements.txt               # Dependências
```

## Como Executar

### 1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

### 2. **Executar pipeline completo dos desafios:**
```bash
python principal.py
```

### 3. **Executar dashboard interativo:**
```bash
streamlit run app_streamlit.py
```

### 4. **Executar testes automatizados:**
```bash
python testes/teste_integracao.py
```

## Funcionalidades Implementadas

### **Dashboard Interativo de Restaurante**
- **Interface web moderna** específica para dados de restaurante
- **Filtros dinâmicos** por item do menu, categoria, funcionário e mesa
- **Métricas de negócio** (faturamento, ticket médio, ocupação)
- **Análise de tendências** com dados históricos
- **Matriz de correlação** com interpretação automática
- **Insights automáticos** baseados em regras de negócio
- **Exportação de dados** em CSV
- **Suporte a dados reais e simulados**

### **Pipeline ETL Completo**
- **Extração inteligente** com 3 fontes de dados:
  - Dados reais do ERP.json
  - Dados reais do data lake (5 endpoints)
  - Dados simulados (fallback)
- **Transformação robusta** com limpeza e validação
- **Análise avançada** com métricas específicas para restaurante

### **Data Lake Funcional**
- **Arquitetura Medallion** (bronze, silver, gold)
- **Particionamento otimizado** por ano/mês/dia/loja
- **Metadados ricos** para auditoria e governança
- **Sistema de busca** por filtros múltiplos
- **Backup e arquivamento** automatizados

## Dados Processados

### **Dados Reais do ERP:**
- **Fonte:** `dados/ERP.json`
- **Conteúdo:** Comanda real com Hambúrguer Artesanal e Pizza Margherita
- **Período:** Janeiro 2024
- **Registros:** 4 (2 itens + desconto + imposto)

### **Dados do Data Lake:**
- **Endpoints:** 5 APIs simuladas (bilgetFiscalInvoice, getGuestChecks, etc.)
- **Período:** Julho 2025
- **Arquivos:** 15 (3 por endpoint)
- **Formato:** JSON com metadados completos

### **Dados Simulados:**
- **Comandas:** 200 comandas realistas
- **Período:** Últimos 90 dias
- **Itens:** 10 itens variados do menu
- **Funcionários:** 5 funcionários diferentes

## Evidências de Funcionamento

### **Análise de Esquema (Desafio 1.1):**
```json
{
  "entidades_negocio": {
    "comanda_cliente": {
      "descricao": "Comanda/pedido do cliente",
      "chave_primaria": "guestCheckId"
    },
    "item_menu": {
      "descricao": "Item do cardápio", 
      "chave_primaria": "miNum"
    }
  }
}
```

### **Modelo Relacional (Desafio 1.2):**
- **8 tabelas normalizadas** (3NF)
- **Relacionamentos com integridade referencial**
- **Constraints de validação de negócio**
- **Índices otimizados para consultas**

### **Data Lake (Desafio 2.2):**
```
dados/data_lake/dados_brutos/
├── bilgetFiscalInvoice/ano=2025/mes=07/dia=31/loja=loja001/
├── getGuestChecks/ano=2025/mes=07/dia=31/loja=loja001/
└── ... (5 endpoints com particionamento completo)
```

## Status dos Desafios

| Desafio | Status | Localização | Evidência |
|---------|--------|-------------|-----------|
| **1.1** - Esquema JSON | Completo | `docs/analise_esquema.json` | Análise automatizada |
| **1.2** - Tabelas SQL | Completo | `sql/criar_tabelas.sql` | 8 tabelas normalizadas |
| **1.3** - Justificativa | Completo | `docs/solucao_desafio1.md` | Documentação detalhada |
| **2.1** - Por que armazenar | Completo | `docs/solucao_desafio2.md` | Justificativas técnicas |
| **2.2** - Estrutura dados | Completo | `dados/data_lake/` | Implementação real |
| **2.3** - Evolução schema | Completo | `src/desafio2/` | Código funcional |

## Funcionalidades Extras

- **Dashboard web interativo** com Streamlit
- **Pipeline ETL completo** com 3 fontes de dados
- **Testes automatizados** com 100% de sucesso
- **Documentação técnica** completa
- **Insights automáticos** para restaurante
- **Sistema de cache** para performance

