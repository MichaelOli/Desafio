# 📊 Dashboard de Vendas com Streamlit

Este projeto agora inclui uma aplicação web interativa construída com **Streamlit** e **Plotly** para visualização de dados de vendas.

## 🚀 Como Executar o Dashboard

### 1. Instalar Dependências
```bash
pip install streamlit plotly
```

### 2. Executar a Aplicação
```bash
streamlit run app_streamlit.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`

## 🎯 Funcionalidades do Dashboard

### 📊 Dashboard Principal
- **Métricas em tempo real**: Total de vendas, ticket médio, transações e desconto médio
- **Gráficos interativos**:
  - Evolução das vendas mensais (linha)
  - Top 5 produtos mais vendidos (barras horizontais)
  - Distribuição de vendas por região (pizza)
  - Performance dos vendedores (barras horizontais)
  - Distribuição do valor das vendas (histograma)
  - Vendas por dia da semana (barras)

### 🔍 Filtros Dinâmicos
- **Número de registros**: Controle deslizante para ajustar o volume de dados
- **Filtro por produto**: Dropdown com todos os produtos disponíveis
- **Filtro por região**: Dropdown com todas as regiões
- **Filtro por vendedor**: Dropdown com todos os vendedores

### 📈 Análise de Tendências
- Crescimento médio mensal
- Volatilidade das vendas
- Identificação do melhor e pior mês
- Tendência geral (crescente/decrescente)

### 🔥 Matriz de Correlação
- Heatmap interativo mostrando correlações entre variáveis numéricas
- Interpretação automática dos valores de correlação

### 🤖 Insights Automáticos
- Análise automatizada dos dados
- Identificação de padrões e tendências
- Recomendações baseadas nos dados

### 📥 Exportação de Dados
- Visualização dos dados brutos filtrados
- Download dos dados em formato CSV
- Timestamp automático nos arquivos exportados

## 🎨 Características da Interface

### Design Responsivo
- Layout adaptável para diferentes tamanhos de tela
- Organização em abas para melhor navegação
- Sidebar com controles e filtros

### Interatividade
- Gráficos totalmente interativos com Plotly
- Zoom, pan e hover em todos os gráficos
- Filtros em tempo real que atualizam todos os gráficos

### Experiência do Usuário
- Loading spinners durante processamento
- Mensagens informativas e de erro
- Tooltips explicativos
- CSS customizado para melhor aparência

## 🔧 Estrutura Técnica

### Arquivos Principais
- `app_streamlit.py`: Aplicação principal do Streamlit
- `src/analisar.py`: Módulo atualizado com funções para Streamlit
- `src/extrair.py`: Geração de dados de exemplo
- `src/transformar.py`: Limpeza e transformação de dados

### Tecnologias Utilizadas
- **Streamlit**: Framework para aplicações web em Python
- **Plotly**: Biblioteca para gráficos interativos
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica

### Cache de Dados
- Utiliza `@st.cache_data` para otimizar performance
- Dados são recarregados apenas quando necessário
- Melhora significativa na velocidade de resposta

## 📱 Comparação: Matplotlib vs Streamlit

### Antes (Matplotlib/Seaborn)
- ❌ Gráficos estáticos
- ❌ Necessário salvar imagens
- ❌ Sem interatividade
- ❌ Visualização limitada

### Agora (Streamlit/Plotly)
- ✅ Gráficos totalmente interativos
- ✅ Interface web moderna
- ✅ Filtros dinâmicos em tempo real
- ✅ Exportação de dados integrada
- ✅ Responsivo e mobile-friendly
- ✅ Fácil compartilhamento via URL

## 🚀 Próximos Passos

### Melhorias Possíveis
1. **Autenticação**: Sistema de login para múltiplos usuários
2. **Banco de Dados**: Integração com PostgreSQL/MySQL
3. **Deploy**: Publicação no Streamlit Cloud ou Heroku
4. **Alertas**: Notificações automáticas para anomalias
5. **Relatórios**: Geração de PDFs automatizados

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

---

**Desenvolvido com ❤️ usando Streamlit e Plotly**