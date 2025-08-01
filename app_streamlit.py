"""
Aplicação Streamlit para Dashboard de Vendas
Execute com: streamlit run app_streamlit.py
"""

from src.analisar import AnalisadorDados
from src.transformar import TransformadorDados
from src.extrair import ExtratorDados
import streamlit as st
import pandas as pd
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar_dados_restaurante(usar_dados_reais=True):
    """Carrega e processa os dados do restaurante."""
    extrator = ExtratorDados()
    transformador = TransformadorDados()

    if usar_dados_reais:
        # Tentar carregar dados reais (ERP + Data Lake)
        dados_brutos = extrator.extrair_dados_combinados_restaurante()
    else:
        # Gerar dados simulados
        dados_brutos = extrator.gerar_dados_exemplo_restaurante(200)

    # Limpar e transformar
    dados_limpos = transformador.limpar_dados_restaurante(dados_brutos)

    return dados_limpos


def main():
    """Função principal da aplicação Streamlit."""

    # Sidebar para configurações
    st.sidebar.title("Configurações do Restaurante")
    st.sidebar.markdown("---")

    # Opção para escolher fonte de dados
    usar_dados_reais = st.sidebar.checkbox(
        "Usar dados reais do ERP/Data Lake",
        value=True,
        help="Marque para usar dados reais do arquivo ERP.json e Data Lake, desmarque para dados simulados"
    )

    # Filtros adicionais
    st.sidebar.subheader("🔍 Filtros")

    # Carregar dados
    with st.spinner("Carregando dados do restaurante..."):
        dados_df = carregar_dados_restaurante(usar_dados_reais)

    # Verificar se há dados
    if dados_df.empty:
        st.error(
            "Nenhum dado encontrado. Verifique se os arquivos ERP.json e Data Lake estão disponíveis.")
        return

    # Filtros dinâmicos baseados nos dados do restaurante
    if 'nome_item' in dados_df.columns:
        itens_disponiveis = ['Todos'] + \
            sorted(dados_df['nome_item'].unique().tolist())
        item_selecionado = st.sidebar.selectbox(
            "Filtrar por Item do Menu",
            itens_disponiveis
        )
    else:
        item_selecionado = 'Todos'

    if 'categoria' in dados_df.columns:
        categorias_disponiveis = ['Todas'] + \
            sorted(dados_df['categoria'].unique().tolist())
        categoria_selecionada = st.sidebar.selectbox(
            "Filtrar por Categoria",
            categorias_disponiveis
        )
    else:
        categoria_selecionada = 'Todas'

    if 'nome_funcionario' in dados_df.columns:
        funcionarios_disponiveis = [
            'Todos'] + sorted(dados_df['nome_funcionario'].unique().tolist())
        funcionario_selecionado = st.sidebar.selectbox(
            "Filtrar por Funcionário",
            funcionarios_disponiveis
        )
    else:
        funcionario_selecionado = 'Todos'

    if 'numero_mesa' in dados_df.columns:
        mesas_disponiveis = [
            'Todas'] + sorted([f"Mesa {m}" for m in dados_df['numero_mesa'].unique()])
        mesa_selecionada = st.sidebar.selectbox(
            "Filtrar por Mesa",
            mesas_disponiveis
        )
    else:
        mesa_selecionada = 'Todas'

    # Aplicar filtros
    dados_filtrados = dados_df.copy()

    if item_selecionado != 'Todos' and 'nome_item' in dados_filtrados.columns:
        dados_filtrados = dados_filtrados[dados_filtrados['nome_item']
                                          == item_selecionado]

    if categoria_selecionada != 'Todas' and 'categoria' in dados_filtrados.columns:
        dados_filtrados = dados_filtrados[dados_filtrados['categoria']
                                          == categoria_selecionada]

    if funcionario_selecionado != 'Todos' and 'nome_funcionario' in dados_filtrados.columns:
        dados_filtrados = dados_filtrados[dados_filtrados['nome_funcionario']
                                          == funcionario_selecionado]

    if mesa_selecionada != 'Todas' and 'numero_mesa' in dados_filtrados.columns:
        numero_mesa = int(mesa_selecionada.replace('Mesa ', ''))
        dados_filtrados = dados_filtrados[dados_filtrados['numero_mesa'] == numero_mesa]

    # Verificar se ainda há dados após filtros
    if len(dados_filtrados) == 0:
        st.error(
            "Nenhum dado encontrado com os filtros selecionados. Tente ajustar os filtros.")
        return

    # Informações sobre filtros aplicados
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Resumo dos Filtros")
    st.sidebar.info(f"""
    **Registros selecionados:** {len(dados_filtrados):,} de {len(dados_df):,}
    
    **Filtros ativos:**
    - Item: {item_selecionado}
    - Categoria: {categoria_selecionada}  
    - Funcionário: {funcionario_selecionado}
    - Mesa: {mesa_selecionada}
    """)

    # Título principal
    st.markdown('<h1 class="main-header">🍽️ Dashboard do Restaurante</h1>',
                unsafe_allow_html=True)

    # Mostrar período de análise
    if 'data_abertura' in dados_filtrados.columns:
        data_inicio = dados_filtrados['data_abertura'].min().strftime(
            '%d/%m/%Y')
        data_fim = dados_filtrados['data_abertura'].max().strftime('%d/%m/%Y')
        st.markdown(f"**Período de análise:** {data_inicio} a {data_fim}")

    # Mostrar fonte dos dados
    fonte_dados = "Dados Reais (ERP + Data Lake)" if usar_dados_reais else "Dados Simulados"
    st.markdown(f"**Fonte dos dados:** {fonte_dados}")

    # Criar abas para organizar o conteúdo
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍽️ Dashboard Principal",
        "📈 Análise de Tendências",
        "🔥 Correlações",
        "🤖 Insights Automáticos"
    ])

    # Inicializar analisador
    analisador = AnalisadorDados()

    with tab1:
        # Dashboard principal do restaurante
        analisador.criar_dashboard_restaurante(dados_filtrados)

    with tab2:
        st.subheader("📈 Análise de Tendências do Restaurante")

        # Gerar análise de tendências
        tendencias = analisador.analisar_tendencias(dados_filtrados)

        # Verificar se há dados suficientes para análise de tendências
        if 'data_abertura' in dados_filtrados.columns:
            periodos_unicos = dados_filtrados['data_abertura'].dt.to_period(
                'M').nunique()
            if periodos_unicos == 1:
                st.warning(f"""
                **Dados Insuficientes para Análise de Tendências**
                
                Atualmente temos dados de apenas **1 período** ({dados_filtrados['data_abertura'].dt.to_period('M').iloc[0]}).
                
                Para uma análise de tendências significativa, precisamos de dados de **múltiplos meses**.
                
                **Sugestões:**
                - Aguarde mais dados históricos serem coletados
                - Use dados simulados (desmarque "Usar dados reais") para ver como a análise funcionaria
                - Considere analisar tendências diárias ao invés de mensais
                """)

        # Exibir métricas de tendência
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Crescimento Médio Mensal",
                f"{tendencias['crescimento_medio_mensal']:.2f}%",
                delta=f"{tendencias['crescimento_medio_mensal']:.2f}%"
            )

        with col2:
            st.metric(
                "Volatilidade",
                f"{tendencias['volatilidade']:.2f}%"
            )

        with col3:
            st.metric(
                "Tendência Geral",
                tendencias['tendencia_geral'].title(),
                delta="Positiva" if tendencias['tendencia_geral'] == 'crescente' else "Negativa"
            )

        # Informações detalhadas sobre tendências
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **🏆 Melhor Período:**
            - Período: {tendencias['melhor_mes']['periodo']}
            - Valor: R$ {tendencias['melhor_mes']['valor']:,.2f}
            """)

        with col2:
            # Verificar se melhor e pior são iguais (dados insuficientes)
            if tendencias['melhor_mes']['periodo'] == tendencias['pior_mes']['periodo']:
                st.info(f"""
                **📊 Período Único:**
                - Período: {tendencias['pior_mes']['periodo']}
                - Valor: R$ {tendencias['pior_mes']['valor']:,.2f}
                - Apenas um período disponível
                """)
            else:
                st.warning(f"""
                **📉 Pior Período:**
                - Período: {tendencias['pior_mes']['periodo']}
                - Valor: R$ {tendencias['pior_mes']['valor']:,.2f}
                """)

    with tab3:
        st.subheader("🔥 Análise de Correlações")
        analisador.criar_heatmap_correlacao(dados_filtrados)

    with tab4:
        st.subheader("🤖 Insights Automáticos do Restaurante")

        # Gerar insights específicos para restaurante
        insights = analisador.gerar_insights_automaticos(dados_filtrados)

        st.markdown(
            "**Insights descobertos automaticamente nos dados do restaurante:**")

        for i, insight in enumerate(insights, 1):
            st.markdown(f"**{i}.** {insight}")

        # Adicionar seção de dados brutos (opcional)
        st.markdown("---")
        if st.checkbox("🔍 Mostrar dados brutos"):
            st.subheader("Dados do Restaurante Filtrados")
            st.dataframe(
                dados_filtrados,
                use_container_width=True,
                height=400
            )

            # Opção para download
            csv = dados_filtrados.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados como CSV",
                data=csv,
                file_name=f"restaurante_dados_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
