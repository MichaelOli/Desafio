# Desafio Engenheiro de Dados 2025

Este projeto foi desenvolvido para demonstrar habilidades essenciais em engenharia de dados, incluindo:

## Objetivos do Projeto

1. **Extração e Transformação de Dados (ETL)**
   - Leitura de dados de diferentes fontes (CSV, JSON, APIs)
   - Limpeza e transformação de dados
   - Validação de qualidade dos dados

2. **Análise e Processamento de Dados**
   - Análise exploratória de dados
   - Agregações e métricas
   - Visualizações básicas

## Tecnologias Utilizadas

- **Python 3.8+**
- **Pandas** - Manipulação de dados
- **Requests** - Consumo de APIs
- **Streamlit** - Dashboard web interativo
- **Plotly** - Gráficos interativos
- **SQLite** - Banco de dados local
- **Jupyter Notebook** - Análise interativa

## Estrutura do Projeto

```
desafio-engenheiro-dados/
├── dados/                     # Dados de entrada
│   ├── vendas.csv
│   └── produtos.json
├── docs/                 
├── src/                       # Código fonte
│   ├── __init__.py
│   ├── extrair.py
│   ├── transformar.py
│   └── analisar.py
├── testes/                    # Testes unitários
│   └── teste_transformador.py
├── requirements.txt           # Dependências
└── principal.py              # Script principal
```

## Como Executar

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar o pipeline completo:**
```bash
python principal.py
```

3. **Executar dashboard interativo:**
```bash
streamlit run app_streamlit.py
```

4. **Executar análise interativa:**
```bash
jupyter notebook cadernos/analise_exploratoria.ipynb
```

## Funcionalidades Implementadas

### Dashboard Interativo com Streamlit 
- **Interface web moderna** com gráficos interativos
- **Filtros dinâmicos** por produto, região e vendedor
- **Análise de tendências** com métricas automáticas
- **Matriz de correlação** interativa
- **Insights automáticos** baseados em IA
- **Exportação de dados** em CSV
- **Design responsivo** para desktop e mobile

### Desafio 1: Pipeline de Dados de Vendas
- Extração de dados de vendas de arquivo CSV
- Limpeza e validação dos dados
- Cálculo de métricas de negócio
- Geração de relatórios

### Desafio 2: Integração com API Externa
- Consumo de API de produtos
- Enriquecimento dos dados de vendas
- Armazenamento em banco de dados
- Data Lake com arquitetura Medallion

