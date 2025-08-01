# Fontes de Dados: Reais vs Simulados 

## Visão Geral

O sistema possui **3 fontes de dados** diferentes que são usadas em uma **hierarquia de prioridade**:

```
1. DADOS REAIS DO ERP.json (Prioridade Alta)
2. DADOS REAIS DO DATA LAKE (Prioridade Média)  
3. DADOS SIMULADOS (Fallback)
```

---

## **1. DADOS REAIS DO ERP.json**

### **Localização:**
```
dados/ERP.json
```

### **Conteúdo Real:**
```json
{
  "guestCheckId": "12345678-1234-5678-9012-123456789012",
  "chkNum": 1001,
  "opnBusDt": "2024-01-15",
  "chkTtl": 50.05,
  "gstCnt": 2,
  "detailLines": [
    {
      "menuItem": {
        "itemName": "Hambúrguer Artesanal",
        "categoryName": "Lanches",
        "unitPrice": 38.90
      }
    },
    {
      "menuItem": {
        "itemName": "Pizza Margherita", 
        "categoryName": "Pizzas",
        "unitPrice": 22.75
      }
    }
  ]
}
```

### **Dados Extraídos:**
- **Itens reais:** Hambúrguer Artesanal, Pizza Margherita
- **Data:** 2024-01-15 (janeiro de 2024)
- **Mesa:** Mesa 12
- **Total:** R$ 50.05
- **Registros:** 4 (2 itens + 1 desconto + 1 imposto)

### **Como é Processado:**
```python
# src/extrair.py - linha ~100
def extrair_dados_erp_restaurante(self):
    dados_erp = self.extrair_json("dados/ERP.json")
    # Processa cada item do menu, desconto e imposto
    # Retorna DataFrame com dados estruturados
```

---

## **2. DADOS REAIS DO DATA LAKE**

### **Localização:**
```
dados/data_lake/dados_brutos/
├── bilgetFiscalInvoice/ano=2025/mes=07/dia=31/loja=loja001/
├── getGuestChecks/ano=2025/mes=07/dia=31/loja=loja001/
├── getChargeBack/ano=2025/mes=07/dia=31/loja=loja001/
├── getTransactions/ano=2025/mes=07/dia=31/loja=loja001/
└── getCashManagementDetails/ano=2025/mes=07/dia=31/loja=loja001/
```

### **Conteúdo Real (Exemplo):**
```json
{
  "metadados": {
    "endpoint": "getCashManagementDetails",
    "data_negocio": "2025-07-31",
    "id_loja": "loja001"
  },
  "dados": {
    "cashManagementId": "CM-2024-001",
    "storeId": "loja001", 
    "openingBalance": 500.0,
    "closingBalance": 750.0,
    "totalSales": 1250.0
  }
}
```

### **Dados Extraídos:**
- **5 endpoints:** bilgetFiscalInvoice, getGuestChecks, getChargeBack, getTransactions, getCashManagementDetails
- **Data:** 2025-07-31 (julho de 2025)
- **Loja:** loja001
- **Registros:** 15 arquivos (3 de cada endpoint)

### **Como é Processado:**
```python
# src/extrair.py - linha ~360
def extrair_dados_data_lake(self):
    # Busca todos os arquivos JSON nos 5 endpoints
    # Extrai metadados + dados de cada arquivo
    # Consolida em DataFrame único
```

---

## **3. DADOS SIMULADOS**

### **Localização:**
```
Gerados em memória pelo código Python
```

### **Conteúdo Simulado:**
```python
# src/extrair.py - linha ~220
itens_menu = [
    {'nome': 'Hambúrguer Artesanal', 'categoria': 'Lanches', 'preco': 22.75},
    {'nome': 'Pizza Margherita', 'categoria': 'Pizzas', 'preco': 28.50},
    {'nome': 'Lasanha Bolonhesa', 'categoria': 'Massas', 'preco': 24.90},
    {'nome': 'Salmão Grelhado', 'categoria': 'Peixes', 'preco': 35.00},
    # ... mais itens realistas
]

funcionarios = [
    {'id': 1001, 'nome': 'Maria Silva'},
    {'id': 1002, 'nome': 'João Santos'},
    # ... mais funcionários
]
```

### **Dados Gerados:**
- **Período:** Últimos 90 dias (múltiplas datas)
- **Comandas:** 200 comandas simuladas
- **Itens:** 10 itens diferentes do menu
- **Funcionários:** 5 funcionários diferentes
- **Mesas:** 1-20 (aleatório)
- **Registros:** ~800-1000 (dependendo dos itens por comanda)

### **Como é Gerado:**
```python
# src/extrair.py - linha ~220
def gerar_dados_exemplo_restaurante(self, numero_comandas=200):
    # Gera comandas aleatórias com:
    # - Datas dos últimos 90 dias
    # - 1-5 itens por comanda
    # - Funcionários e mesas aleatórios
    # - 20% das comandas têm desconto
```

---

## **Lógica de Decisão: Qual Fonte Usar?**

### **Algoritmo de Prioridade:**

```python
# src/extrair.py - linha ~430
def extrair_dados_combinados_restaurante(self):
    
    # 1. TENTAR ERP.json
    try:
        dados_erp = self.extrair_dados_erp_restaurante()
        if not dados_erp.empty:
            return dados_erp  
    except:
        pass
    
    # 2. TENTAR DATA LAKE  
    try:
        dados_data_lake = self.extrair_dados_data_lake()
        if not dados_data_lake.empty:
            return processar_data_lake(dados_data_lake)  
    except:
        pass
    
    # 3. FALLBACK: DADOS SIMULADOS
    return self.gerar_dados_exemplo_restaurante(200)  
```

### **Cenários Práticos:**

#### **Cenário 1: Projeto Completo (Atual)**
```
ERP.json existe → USA DADOS REAIS DO ERP
Resultado: Hambúrguer Artesanal, Pizza Margherita, 2024-01
```

#### **Cenário 2: Só Data Lake**
```
ERP.json não existe
Data Lake existe → USA DADOS REAIS DO DATA LAKE  
Resultado: Dados dos 5 endpoints, 2025-07
```

#### **Cenário 3: Projeto Vazio**
```
ERP.json não existe
Data Lake não existe → USA DADOS SIMULADOS
Resultado: 200 comandas, múltiplos meses, 10 itens variados
```

---

## **Controle no Dashboard**

### **Checkbox "Usar dados reais do ERP/Data Lake":**

#### **Marcado (Padrão):**
```python
usar_dados_reais = True
dados_df = carregar_dados_restaurante(usar_dados_reais=True)
# → Executa algoritmo de prioridade acima
```

#### **Desmarcado:**
```python  
usar_dados_reais = False
dados_df = carregar_dados_restaurante(usar_dados_reais=False)
# → Força uso de dados simulados
```

---

## 📊 **Comparação das Fontes**

| Aspecto | ERP.json | Data Lake | Simulados |
|---------|----------|-----------|-----------|
| **Realismo** | 100% Real | 100% Real | Realista |
| **Volume** | Poucos dados | Médio | Muitos dados |
| **Períodos** | 1 mês | 1 mês | 3 meses |
| **Tendências** | Impossível | Impossível | Possível |
| **Correlações** | Limitadas | Limitadas | Ricas |
| **Insights** | Básicos | Básicos | Avançados |

---

## **Como Verificar Qual Fonte Está Sendo Usada**

### **1. Logs do Sistema:**
```bash
python demo_streamlit.py

# Saída mostra a fonte:
INFO:src.extrair:Dados ERP extraídos: 4 registros  ← ERP.json
INFO:src.extrair:Dados data lake extraídos: 15 registros  ← Data Lake  
INFO:src.extrair:Gerando dados simulados para demonstração  ← Simulados
```

### **2. Dashboard:**
```
Fonte dos dados: Dados Reais (ERP + Data Lake)  ← Reais
Fonte dos dados: Dados Simulados  ← Simulados
```

### **3. Dados Específicos:**
```
ERP.json: Hambúrguer Artesanal, Pizza Margherita, 2024-01
Simulados: Lasanha Bolonhesa, Salmão Grelhado, múltiplas datas
```

---

## **Recomendações de Uso**

### **Para Testar Funcionalidades:**
```
Desmarque "Usar dados reais"
→ Veja análise completa com tendências e correlações
```

### **Para Dados Reais do Negócio:**
```
Marque "Usar dados reais"  
→ Veja dados reais do ERP, mesmo que limitados
```

### **Para Demonstrações:**
```
Alterne entre os dois para mostrar:
- Dados reais: Autenticidade
- Dados simulados: Funcionalidades completas
```

---

## **Resumo**

**O sistema é inteligente e flexível:**

1. **Prioriza dados reais** quando disponíveis
2. **Fallback automático** para dados simulados
3. **Controle manual** via checkbox
4. **Transparência total** sobre qual fonte está sendo usada

**Resultado:** Você sempre tem dados para analisar, sejam reais ou simulados, com total controle e visibilidade sobre a fonte!

---

## **Insights Automáticos:**

### **NÃO É INTELIGÊNCIA ARTIFICIAL**

Os "insights automáticos" são gerados por **regras programáticas simples**, não por IA:

```python
# Exemplo real do código:
def gerar_insights_automaticos(self, dados_df):
    insights = []
    
    # 1. Ranking simples
    item_top = dados_df.groupby('nome_item')['valor_item'].sum().idxmax()
    insights.append(f"O item mais vendido em valor é: {item_top}")
    
    # 2. Classificação por limiar
    ticket_medio = dados_df.groupby('guest_check_id')['valor_item'].sum().mean()
    if ticket_medio > 100:
        insights.append("O ticket médio é alto, indicando bom valor por comanda")
    else:
        insights.append("O ticket médio é moderado, foco em aumentar itens")
    
    # 3. Identificação de padrões
    mes_pico = dados_df.groupby(dados_df['data_abertura'].dt.month)['valor_item'].sum().idxmax()
    insights.append(f"O mês com maior faturamento é {meses[mes_pico-1]}")
    
    return insights
```

### **Tipos de "Insights" Gerados:**

| Tipo | Exemplo | Método |
|------|---------|--------|
| **Rankings** | "Item mais vendido: Hambúrguer" | `groupby().sum().idxmax()` |
| **Classificações** | "Ticket médio é alto (R$ 45.50)" | `if valor > limiar` |
| **Padrões Temporais** | "Mês de pico: Janeiro" | `groupby(mes).sum().idxmax()` |
| **Comparações** | "Mesa 12 tem maior faturamento" | `groupby().sum().sort_values()` |

### **O que É (Regras Programáticas):**
- Agregações SQL simples (GROUP BY, MAX, AVG)
- Condicionais if/else básicas
- Templates de texto pré-definidos
- Estatísticas descritivas

### **O que NÃO É (IA Real):**
- Aprendizado de máquina
- Redes neurais
- Processamento de linguagem natural
- Análise preditiva complexa
- Reconhecimento de padrões avançados

### **Exemplo de Saída Real:**
```
Insights Automáticos:
1. O mês com maior faturamento é Jan
2. O item mais vendido em valor é: Hambúrguer Artesanal  
3. A categoria com melhor performance é: Lanches
4. O funcionário com melhor performance é: Maria Silva
5. O ticket médio é moderado (R$ 45.50), foco em aumentar itens por comanda
6. A mesa com maior faturamento é a Mesa 12
7. O preço médio dos itens é acessível (R$ 22.75), foco em volume
8. O dia da semana com maior movimento é Segunda-feira
```

**Conclusão:** São "insights automáticos inteligentes" mas baseados em regras simples, não em IA!

---

## **Análise de Correlação: Como Funciona**

### **Matriz de Correlação Melhorada**

A análise de correlação também **não usa IA**, mas sim **estatística tradicional**:

```python
# Cálculo de correlação (Pearson)
correlacao = dados_df[colunas_numericas].corr()

# Interpretação automática
for i, j in correlacao:
    valor_corr = correlacao.iloc[i, j]
    if valor_corr > 0.7:
        tipo = "Correlação muito forte positiva"
        explicacao = f"Quando {var1} aumenta, {var2} também aumenta significativamente"
```

### **Melhorias Implementadas:**

1. preco_unitario ↔ valor_item
   Correlação muito forte positiva (0.85)
   Quando preco_unitario aumenta, valor_item também aumenta significativamente

Insights Práticos:
Itens com preços mais altos geram maior faturamento - considere estratégias de upselling
```

### **Processo de Interpretação:**

1. **Cálculo:** Correlação de Pearson entre variáveis numéricas
2. **Filtragem:** Apenas correlações > 0.3 (significativas)
3. **Classificação:** Por força da correlação
4. **Interpretação:** Templates baseados em regras
5. **Insights:** Sugestões práticas para restaurante

---

## **Análise de Tendências: Limitações dos Dados Reais**

### **Problema Identificado:**

```
Dados Atuais:
- ERP.json: 2024-01-15 (janeiro de 2024)
- Data Lake: 2025-07-31 (julho de 2025)
- Resultado: Apenas 1 período após limpeza

Análise de Tendências:
Melhor Período: 2024-01 (R$ 45.50)
Pior Período: 2024-01 (R$ 45.50)  ← Iguais!
```

### **Solução Implementada:**

#### **Interface Melhorada:**
```
Dados Insuficientes para Análise de Tendências

Atualmente temos dados de apenas 1 período (2024-01).

Para uma análise de tendências significativa, precisamos de dados de múltiplos meses.

Sugestões:
- Aguarde mais dados históricos serem coletados
- Use dados simulados (desmarque "Usar dados reais") para ver como funcionaria
- Considere analisar tendências diárias ao invés de mensais
```

#### **Comparação Visual:**
```
Melhor Período: 2024-01 (R$ 45.50)
Período Único: 2024-01 (R$ 45.50)
Apenas um período disponível  ← Explicação clara!
```

### **Recomendação:**
Para ver análise de tendências completa, use **dados simulados** que cobrem 90 dias com múltiplas datas.

---

## **Processamento e Transformação de Dados**

### **Pipeline ETL Completo:**

```
1. EXTRACT (Extrair)
   ├── ERP.json → 4 registros (2 itens + 1 desconto + 1 imposto)
   ├── Data Lake → 15 registros (5 endpoints × 3 arquivos)
   └── Simulados → 800-1000 registros (200 comandas)

2. TRANSFORM (Transformar)
   ├── Limpeza: Remove registros inválidos
   ├── Padronização: Nomes, datas, valores
   ├── Enriquecimento: Colunas derivadas (ano, mês, dia_semana)
   └── Validação: Constraints de negócio

3. LOAD (Carregar)
   ├── DataFrame estruturado
   ├── Métricas calculadas
   └── Pronto para análise
```

### **Exemplo de Transformação:**

#### **Dados Brutos (ERP.json):**
```json
{
  "detailLines": [{
    "menuItem": {
      "itemName": "Hambúrguer Artesanal",
      "unitPrice": 22.75,
      "dspQty": 1
    }
  }]
}
```

#### **Dados Transformados:**
```python
{
  'nome_item': 'Hambúrguer Artesanal',
  'preco_unitario': 22.75,
  'quantidade': 1,
  'valor_item': 22.75,
  'categoria': 'Lanches',
  'ano': 2024,
  'mes': 1,
  'dia_semana': 'Monday',
  'ticket_comanda': 45.50
}
```

---

## **Controles Avançados do Dashboard**

### **Filtros Dinâmicos:**

```python
# Filtros específicos para restaurante
filtros_disponiveis = {
    'item_menu': dados_df['nome_item'].unique(),
    'categoria': dados_df['categoria'].unique(), 
    'funcionario': dados_df['nome_funcionario'].unique(),
    'mesa': dados_df['numero_mesa'].unique()
}

# Aplicação de filtros
dados_filtrados = dados_df.copy()
if item_selecionado != 'Todos':
    dados_filtrados = dados_filtrados[dados_filtrados['nome_item'] == item_selecionado]
```

### **Métricas Calculadas em Tempo Real:**

```python
# Métricas principais
metricas = {
    'faturamento_total': dados_filtrados['valor_item'].sum(),
    'total_comandas': dados_filtrados['guest_check_id'].nunique(),
    'ticket_medio': dados_filtrados.groupby('guest_check_id')['valor_item'].sum().mean(),
    'itens_vendidos': len(dados_filtrados)
}
```
## **Performance e Otimizações**

### **Cache Inteligente:**

```python
@st.cache_data
def carregar_dados_restaurante(usar_dados_reais=True):
    # Dados são carregados apenas uma vez
    # Recarregados apenas quando parâmetros mudam
```

### **Filtragem Eficiente:**

```python
# Filtros aplicados em sequência otimizada
dados_filtrados = dados_df.copy()
for filtro, valor in filtros_ativos.items():
    if valor != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados[filtro] == valor]
```

### **Processamento Sob Demanda:**

```python
# Métricas calculadas apenas quando necessário
if tab_selecionada == 'tendencias':
    tendencias = analisador.analisar_tendencias(dados_filtrados)
elif tab_selecionada == 'correlacoes':
    correlacoes = analisador.criar_heatmap_correlacao(dados_filtrados)
```

---

## **Resumo Técnico Completo**

### **Arquitetura:**
```
Interface (Streamlit) 
    ↓
Controle de Dados (app_streamlit.py)
    ↓
Pipeline ETL (src/)
    ├── Extrair (extrair.py) → ERP.json + Data Lake + Simulados
    ├── Transformar (transformar.py) → Limpeza + Enriquecimento  
    └── Analisar (analisar.py) → Insights + Correlações + Tendências
    ↓
Visualização (Plotly + Streamlit)
```

### **Funcionalidades:**
- **3 fontes de dados** com priorização automática
- **Insights automáticos** baseados em regras (não IA)
- **Correlações intuitivas** com interpretação automática
- **Análise de tendências** com tratamento de dados insuficientes
- **Dashboard interativo** com filtros dinâmicos
- **Cache inteligente** para performance


