# Kanban do Projeto - Checklist de Cumprimento dos Desafios

## Colunas de Progresso

### To Do (A Fazer)
- (Nenhuma tarefa pendente)

### In Progress (Em Andamento)
- (Nenhuma tarefa em andamento)

### Done (Concluído)
- **DESAFIO 1: Análise e Modelagem JSON → SQL**
  - **1. Descreva o esquema JSON correspondente ao exemplo**
    - **Onde encontrar:** `docs/analise_esquema.json`, `docs/solucao_desafio1.md`
    - **O que foi entregue:** Análise completa do esquema JSON com identificação de entidades, campos e relacionamentos.
    - **Data de conclusão:** 26/07/2025
  - **2. Transcreva o JSON para tabelas SQL**
    - **Onde encontrar:** `sql/criar_tabelas.sql`, `docs/modelo_relacional.json`
    - **O que foi entregue:** 8 tabelas normalizadas (3NF) com scripts SQL.
    - **Data de conclusão:** 27/07/2025
  - **3. Descreva a abordagem escolhida em detalhes**
    - **Onde encontrar:** `docs/solucao_desafio1.md`
    - **O que foi entregue:** Justificativa da normalização 3NF, tratamento de casos especiais e regras de negócio.
    - **Data de conclusão:** 28/07/2025

- **DESAFIO 2: Data Lake e Pipeline de APIs**
  - **1. Por que armazenar as respostas das APIs?**
    - **Onde encontrar:** `docs/solucao_desafio2.md`, `docs/documentacao_data_lake.json`
    - **O que foi entregue:** Justificativas técnicas e de negócio (auditoria, BI, recuperação).
    - **Data de conclusão:** 29/07/2025
  - **2. Como você armazenaria os dados? Estrutura de pastas**
    - **Onde encontrar:** `dados/data_lake/`, `src/desafio2/gerenciador_data_lake.py`
    - **O que foi entregue:** Estrutura com particionamento hierárquico (data/loja).
    - **Data de conclusão:** 30/07/2025
  - **3. Mudança de schema (taxes → taxation) - O que implicaria?**
    - **Onde encontrar:** `docs/solucao_desafio2.md`, `src/desafio2/gerenciador_data_lake.py`
    - **O que foi entregue:** Estratégia de versionamento e migração automática.
    - **Data de conclusão:** 31/07/2025

- **IMPLEMENTAÇÕES ADICIONAIS**
  - **Dashboard Interativo com Streamlit**
    - **Onde encontrar:** `app_streamlit.py`, `src/analisar.py`
    - **O que foi entregue:** Dashboard web com filtros e gráficos.
    - **Data de conclusão:** 30/07/2025
  - **Pipeline ETL Completo**
    - **Onde encontrar:** `src/extrair.py`, `src/transformar.py`, `src/analisar.py`
    - **O que foi entregue:** Extração, transformação e análise automatizadas.
    - **Data de conclusão:** 31/07/2025
  - **Testes de Integração**
    - **Onde encontrar:** `testes/teste_integracao.py`
    - **O que foi entregue:** 5 testes com 100% de sucesso.
    - **Data de conclusão:** 31/07/2025

## Resumo de Cumprimento
| Requisito                | Status    | Data de Conclusão | Localização               | Evidência                  |
|--------------------------|-----------|-------------------|---------------------------|----------------------------|
| Desafio 1.1 - Esquema JSON | Concluído | 26/07/2025        | `docs/analise_esquema.json` | Análise automatizada       |
| Desafio 1.2 - Tabelas SQL | Concluído | 27/07/2025        | `sql/criar_tabelas.sql`    | 8 tabelas normalizadas     |
| Desafio 1.3 - Justificativa | Concluído | 28/07/2025        | `docs/solucao_desafio1.md` | Documentação detalhada     |
| Desafio 2.1 - Por que armazenar | Concluído | 29/07/2025        | `docs/solucao_desafio2.md` | Justificativas técnicas    |
| Desafio 2.2 - Estrutura dados | Concluído | 30/07/2025        | `dados/data_lake/`         | Implementação real         |
| Desafio 2.3 - Evolução schema | Concluído | 31/07/2025        | `src/desafio2/`            | Código funcional           |
| Dashboard Interativo      | Concluído | 30/07/2025        | `app_streamlit.py`         | Interface web              |
| Pipeline ETL Completo     | Concluído | 31/07/2025        | `src/extrair.py`           | Extração e análise         |
| Testes de Integração      | Concluído | 31/07/2025        | `testes/teste_integracao.py` | 5 testes passando          |