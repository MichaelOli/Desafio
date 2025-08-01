"""
Módulo responsável pela análise e visualização de dados usando Streamlit.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Importações condicionais para Streamlit e Plotly
try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    logger.warning(
        "Streamlit/Plotly não disponível. Funcionalidades de dashboard desabilitadas.")


class AnalisadorDados:
    """Classe para análise e visualização de dados."""

    def __init__(self):
        self.figuras_salvas = []

    def gerar_relatorio_restaurante(self, dados_df: pd.DataFrame) -> Dict:
        """
        Gera relatório completo do restaurante.

        Args:
            dados_df: DataFrame com dados do restaurante

        Returns:
            Dicionário com métricas do relatório
        """
        logger.info("Gerando relatório do restaurante")

        relatorio = {
            'periodo_analise': {
                'data_inicio': dados_df['data_abertura'].min().strftime('%Y-%m-%d'),
                'data_fim': dados_df['data_abertura'].max().strftime('%Y-%m-%d'),
                'total_dias': (dados_df['data_abertura'].max() - dados_df['data_abertura'].min()).days
            },
            'metricas_gerais': {
                'total_vendas': round(dados_df['valor_item'].sum(), 2),
                'total_comandas': dados_df['guest_check_id'].nunique(),
                'total_itens': len(dados_df),
                'ticket_medio': round(dados_df.groupby('guest_check_id')['valor_item'].sum().mean(), 2),
                'quantidade_total': dados_df['quantidade'].sum(),
                'preco_medio_item': round(dados_df['preco_unitario'].mean(), 2)
            },
            'top_itens': dados_df.groupby('nome_item')['valor_item'].sum().sort_values(ascending=False).head().to_dict(),
            'top_categorias': dados_df.groupby('categoria')['valor_item'].sum().sort_values(ascending=False).head().to_dict(),
            'performance_funcionarios': dados_df.groupby('nome_funcionario')['valor_item'].sum().sort_values(ascending=False).head().to_dict() if 'nome_funcionario' in dados_df.columns else {},
            'vendas_por_mesa': dados_df.groupby('numero_mesa')['valor_item'].sum().sort_values(ascending=False).head().to_dict()
        }

        logger.info("Relatório do restaurante gerado com sucesso")
        return relatorio

    def criar_dashboard_restaurante(self, dados_df: pd.DataFrame) -> None:
        """
        Cria dashboard interativo específico para restaurante usando Streamlit.

        Args:
            dados_df: DataFrame com dados do restaurante
        """
        if not STREAMLIT_AVAILABLE:
            logger.warning(
                "Streamlit não disponível. Dashboard não pode ser criado.")
            return

        logger.info("Criando dashboard do restaurante com Streamlit")

        st.title("Dashboard do Restaurante - Análise Operacional")
        st.markdown("---")

        # Métricas principais no topo
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_vendas = dados_df['valor_item'].sum()
            st.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")

        with col2:
            total_comandas = dados_df['guest_check_id'].nunique()
            st.metric("Total de Comandas", f"{total_comandas:,}")

        with col3:
            ticket_medio = dados_df.groupby('guest_check_id')[
                'valor_item'].sum().mean()
            st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

        with col4:
            total_itens = len(dados_df)
            st.metric("Itens Vendidos", f"{total_itens:,}")

        st.markdown("---")

        # Layout em duas colunas
        col1, col2 = st.columns(2)

        with col1:
            # 1. Vendas por dia
            st.subheader("Faturamento por Dia")
            vendas_diarias = dados_df.groupby(dados_df['data_abertura'].dt.date)[
                'valor_item'].sum().reset_index()
            vendas_diarias['data_abertura'] = pd.to_datetime(
                vendas_diarias['data_abertura'])

            fig_vendas_dia = px.line(
                vendas_diarias,
                x='data_abertura',
                y='valor_item',
                title="Evolução do Faturamento Diário",
                markers=True
            )
            fig_vendas_dia.update_layout(
                xaxis_title="Data",
                yaxis_title="Faturamento (R$)",
                showlegend=False
            )
            st.plotly_chart(fig_vendas_dia, use_container_width=True)

            # 2. Top 5 itens do menu
            st.subheader("Top 5 Itens Mais Vendidos")
            top_itens = dados_df.groupby('nome_item')['valor_item'].sum(
            ).sort_values(ascending=False).head().reset_index()

            fig_itens = px.bar(
                top_itens,
                x='valor_item',
                y='nome_item',
                orientation='h',
                title="Itens Mais Vendidos por Faturamento"
            )
            fig_itens.update_layout(
                xaxis_title="Faturamento (R$)",
                yaxis_title="Item do Menu"
            )
            st.plotly_chart(fig_itens, use_container_width=True)

            # 3. Distribuição de preços dos itens
            st.subheader("Distribuição de Preços dos Itens")
            fig_hist = px.histogram(
                dados_df,
                x='preco_unitario',
                nbins=20,
                title="Distribuição dos Preços dos Itens"
            )
            fig_hist.update_layout(
                xaxis_title="Preço Unitário (R$)",
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            # 4. Vendas por categoria
            st.subheader("Faturamento por Categoria")
            vendas_categoria = dados_df.groupby(
                'categoria')['valor_item'].sum().reset_index()

            fig_categoria = px.pie(
                vendas_categoria,
                values='valor_item',
                names='categoria',
                title="Distribuição do Faturamento por Categoria"
            )
            st.plotly_chart(fig_categoria, use_container_width=True)

            # 5. Performance por funcionário (se disponível)
            if 'nome_funcionario' in dados_df.columns:
                st.subheader("Performance dos Funcionários")
                vendas_funcionario = dados_df.groupby('nome_funcionario')[
                    'valor_item'].sum().sort_values(ascending=True).reset_index()

                fig_funcionarios = px.bar(
                    vendas_funcionario,
                    x='valor_item',
                    y='nome_funcionario',
                    orientation='h',
                    title="Faturamento por Funcionário"
                )
                fig_funcionarios.update_layout(
                    xaxis_title="Faturamento (R$)",
                    yaxis_title="Funcionário"
                )
                st.plotly_chart(fig_funcionarios, use_container_width=True)

            # 6. Vendas por dia da semana
            st.subheader("Faturamento por Dia da Semana")
            ordem_dias = ['Monday', 'Tuesday', 'Wednesday',
                          'Thursday', 'Friday', 'Saturday', 'Sunday']
            nomes_dias = ['Segunda', 'Terça', 'Quarta',
                          'Quinta', 'Sexta', 'Sábado', 'Domingo']

            vendas_dia_semana = dados_df.groupby(
                'dia_semana')['valor_item'].sum().reindex(ordem_dias).reset_index()
            vendas_dia_semana['dia_nome'] = nomes_dias

            fig_dias = px.bar(
                vendas_dia_semana,
                x='dia_nome',
                y='valor_item',
                title="Faturamento por Dia da Semana"
            )
            fig_dias.update_layout(
                xaxis_title="Dia da Semana",
                yaxis_title="Faturamento (R$)"
            )
            st.plotly_chart(fig_dias, use_container_width=True)

        # Seção adicional: Análise de mesas
        st.markdown("---")
        st.subheader("Análise de Ocupação das Mesas")

        col1, col2 = st.columns(2)

        with col1:
            # Faturamento por mesa
            vendas_mesa = dados_df.groupby('numero_mesa')['valor_item'].sum(
            ).sort_values(ascending=False).head(10).reset_index()
            vendas_mesa['mesa_nome'] = 'Mesa ' + \
                vendas_mesa['numero_mesa'].astype(str)

            fig_mesas = px.bar(
                vendas_mesa,
                x='mesa_nome',
                y='valor_item',
                title="Top 10 Mesas por Faturamento"
            )
            fig_mesas.update_layout(
                xaxis_title="Mesa",
                yaxis_title="Faturamento (R$)"
            )
            st.plotly_chart(fig_mesas, use_container_width=True)

        with col2:
            # Número de comandas por mesa
            comandas_mesa = dados_df.groupby('numero_mesa')['guest_check_id'].nunique(
            ).sort_values(ascending=False).head(10).reset_index()
            comandas_mesa['mesa_nome'] = 'Mesa ' + \
                comandas_mesa['numero_mesa'].astype(str)

            fig_comandas_mesa = px.bar(
                comandas_mesa,
                x='mesa_nome',
                y='guest_check_id',
                title="Top 10 Mesas por Número de Comandas"
            )
            fig_comandas_mesa.update_layout(
                xaxis_title="Mesa",
                yaxis_title="Número de Comandas"
            )
            st.plotly_chart(fig_comandas_mesa, use_container_width=True)

    def analisar_tendencias(self, dados_df: pd.DataFrame) -> Dict:
        """
        Analisa tendências nos dados do restaurante.

        Args:
            dados_df: DataFrame com dados do restaurante

        Returns:
            Dicionário com análise de tendências
        """
        logger.info("Analisando tendências do restaurante")

        # Determinar coluna de data e valor
        coluna_data = 'data_abertura' if 'data_abertura' in dados_df.columns else 'data_venda'
        coluna_valor = 'valor_item' if 'valor_item' in dados_df.columns else 'valor_total'

        if coluna_data not in dados_df.columns or coluna_valor not in dados_df.columns:
            logger.warning(
                "Colunas necessárias não encontradas para análise de tendências")
            return {
                'crescimento_medio_mensal': 0.0,
                'melhor_mes': {'periodo': 'N/A', 'valor': 0.0},
                'pior_mes': {'periodo': 'N/A', 'valor': 0.0},
                'volatilidade': 0.0,
                'tendencia_geral': 'estável'
            }

        # Vendas mensais
        vendas_mensais = dados_df.groupby(dados_df[coluna_data].dt.to_period('M'))[
            coluna_valor].sum()

        if len(vendas_mensais) < 2:
            logger.warning("Dados insuficientes para análise de tendências")
            return {
                'crescimento_medio_mensal': 0.0,
                'melhor_mes': {'periodo': str(vendas_mensais.index[0]) if len(vendas_mensais) > 0 else 'N/A',
                               'valor': round(vendas_mensais.iloc[0], 2) if len(vendas_mensais) > 0 else 0.0},
                'pior_mes': {'periodo': str(vendas_mensais.index[0]) if len(vendas_mensais) > 0 else 'N/A',
                             'valor': round(vendas_mensais.iloc[0], 2) if len(vendas_mensais) > 0 else 0.0},
                'volatilidade': 0.0,
                'tendencia_geral': 'estável'
            }

        # Calcular crescimento
        crescimento = vendas_mensais.pct_change().dropna()

        tendencias = {
            'crescimento_medio_mensal': round(crescimento.mean() * 100, 2) if len(crescimento) > 0 else 0.0,
            'melhor_mes': {
                'periodo': str(vendas_mensais.idxmax()),
                'valor': round(vendas_mensais.max(), 2)
            },
            'pior_mes': {
                'periodo': str(vendas_mensais.idxmin()),
                'valor': round(vendas_mensais.min(), 2)
            },
            'volatilidade': round(crescimento.std() * 100, 2) if len(crescimento) > 0 else 0.0,
            'tendencia_geral': 'crescente' if len(crescimento) > 0 and crescimento.mean() > 0 else 'decrescente' if len(crescimento) > 0 and crescimento.mean() < 0 else 'estável'
        }

        logger.info("Análise de tendências do restaurante concluída")
        return tendencias

    def criar_heatmap_correlacao(self, dados_df: pd.DataFrame) -> None:
        """
        Cria análise de correlação mais intuitiva e explicativa usando Streamlit.

        Args:
            dados_df: DataFrame com dados
        """
        if not STREAMLIT_AVAILABLE:
            logger.warning(
                "Streamlit não disponível. Análise de correlação não pode ser criada.")
            return

        logger.info("Criando análise de correlação com Streamlit")

        st.subheader("Análise de Relacionamentos entre Variáveis")

        # Selecionar apenas colunas numéricas relevantes
        colunas_numericas = dados_df.select_dtypes(include=[np.number]).columns

        # Filtrar colunas mais relevantes para restaurante
        colunas_relevantes = []
        for col in colunas_numericas:
            if any(palavra in col.lower() for palavra in ['valor', 'preco', 'quantidade', 'total', 'mesa', 'cliente']):
                colunas_relevantes.append(col)

        if len(colunas_relevantes) < 2:
            colunas_relevantes = list(colunas_numericas)[
                :6]  # Pegar até 6 colunas

        if len(colunas_relevantes) < 2:
            st.warning("Dados insuficientes para análise de correlação.")
            return

        # Calcular correlação apenas para colunas relevantes
        dados_correlacao = dados_df[colunas_relevantes]
        correlacao = dados_correlacao.corr()

        # Layout em duas colunas
        col1, col2 = st.columns([2, 1])

        with col1:
            # Criar heatmap mais limpo
            fig_heatmap = px.imshow(
                correlacao,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="Matriz de Correlação - Variáveis do Restaurante",
                labels=dict(color="Correlação")
            )

            fig_heatmap.update_layout(
                width=600,
                height=500,
                font=dict(size=10)
            )

            # Melhorar formatação dos números
            fig_heatmap.update_traces(
                texttemplate="%{z:.2f}",
                textfont={"size": 10}
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

        with col2:
            st.markdown("### 📖 Como Interpretar")

            # Explicação visual com cores
            st.markdown("""
            **Escala de Correlação:**
            
            🔴 **0.7 a 1.0**: Correlação muito forte
            - Quando uma variável aumenta, a outra também aumenta muito
            
            🟠 **0.3 a 0.7**: Correlação moderada  
            - Há uma relação, mas não tão forte
            
            🟡 **-0.3 a 0.3**: Correlação fraca
            - Pouca ou nenhuma relação entre as variáveis
            
            🔵 **-0.7 a -0.3**: Correlação negativa moderada
            - Quando uma aumenta, a outra diminui
            
            🟣 **-1.0 a -0.7**: Correlação negativa forte
            - Relação inversa muito forte
            """)

        # Análise automática das correlações mais importantes
        st.markdown("---")
        st.subheader("Principais Descobertas")

        # Encontrar correlações mais fortes (excluindo diagonal)
        correlacoes_importantes = []

        for i in range(len(correlacao.columns)):
            for j in range(i+1, len(correlacao.columns)):
                var1 = correlacao.columns[i]
                var2 = correlacao.columns[j]
                valor_corr = correlacao.iloc[i, j]

                if not pd.isna(valor_corr) and abs(valor_corr) > 0.3:
                    correlacoes_importantes.append({
                        'var1': var1,
                        'var2': var2,
                        'correlacao': valor_corr,
                        'abs_correlacao': abs(valor_corr)
                    })

        # Ordenar por correlação mais forte
        correlacoes_importantes.sort(
            key=lambda x: x['abs_correlacao'], reverse=True)

        if correlacoes_importantes:
            st.markdown("**Relacionamentos mais significativos encontrados:**")

            for i, corr in enumerate(correlacoes_importantes[:5], 1):  # Top 5
                var1 = corr['var1']
                var2 = corr['var2']
                valor = corr['correlacao']

                # Interpretar o tipo de correlação
                if valor > 0.7:
                    tipo = "🔴 **Correlação muito forte positiva**"
                    explicacao = f"Quando {var1} aumenta, {var2} também aumenta significativamente"
                elif valor > 0.3:
                    tipo = "🟠 **Correlação moderada positiva**"
                    explicacao = f"Há uma tendência de {var1} e {var2} aumentarem juntos"
                elif valor < -0.7:
                    tipo = "🟣 **Correlação muito forte negativa**"
                    explicacao = f"Quando {var1} aumenta, {var2} diminui significativamente"
                elif valor < -0.3:
                    tipo = "🔵 **Correlação moderada negativa**"
                    explicacao = f"Há uma tendência inversa entre {var1} e {var2}"
                else:
                    continue

                st.markdown(f"""
                **{i}. {var1} ↔ {var2}**
                - {tipo} ({valor:.2f})
                - {explicacao}
                """)
        else:
            st.info(
                "Não foram encontradas correlações significativas (> 0.3) entre as variáveis analisadas.")

        # Seção de insights práticos para o restaurante
        st.markdown("---")
        st.subheader("Insights Práticos para o Restaurante")

        insights_correlacao = []

        # Verificar correlações específicas do restaurante
        for corr in correlacoes_importantes[:3]:
            var1, var2, valor = corr['var1'], corr['var2'], corr['correlacao']

            # Insights específicos baseados nas variáveis
            if 'preco' in var1.lower() and 'valor' in var2.lower() and valor > 0.5:
                insights_correlacao.append(
                    "Itens com preços mais altos geram maior faturamento - considere estratégias de upselling")

            elif 'quantidade' in var1.lower() and 'valor' in var2.lower() and valor > 0.5:
                insights_correlacao.append(
                    "Maior quantidade vendida resulta em maior faturamento - foque em promoções de volume")

            elif 'mesa' in var1.lower() and 'valor' in var2.lower():
                if valor > 0.3:
                    insights_correlacao.append(
                        "🪑 Certas mesas geram mais receita - analise localização e ambiente")
                elif valor < -0.3:
                    insights_correlacao.append(
                        "🪑 Algumas mesas têm performance inferior - verifique localização e conforto")

            elif 'cliente' in var1.lower() and 'valor' in var2.lower() and valor > 0.3:
                insights_correlacao.append(
                    "👥 Mesas com mais clientes tendem a gerar mais receita - otimize ocupação")

        if insights_correlacao:
            for insight in insights_correlacao:
                st.success(insight)
        else:
            st.info(
                "Para obter insights mais específicos, são necessários mais dados históricos do restaurante.")

        # Dica final
        st.markdown("---")
        st.info("""
        **Dica:** Use essas correlações para:
        - Identificar quais fatores mais influenciam o faturamento
        - Otimizar o layout do restaurante (posicionamento de mesas)
        - Desenvolver estratégias de precificação
        - Melhorar a experiência do cliente
        """)

    def gerar_insights_automaticos(self, dados_df: pd.DataFrame) -> List[str]:
        """
        Gera insights automáticos baseados nos dados do restaurante.

        Args:
            dados_df: DataFrame com dados do restaurante

        Returns:
            Lista de insights descobertos
        """
        logger.info("Gerando insights automáticos do restaurante")

        insights = []

        # Determinar colunas disponíveis
        coluna_data = 'data_abertura' if 'data_abertura' in dados_df.columns else 'data_venda'
        coluna_valor = 'valor_item' if 'valor_item' in dados_df.columns else 'valor_total'

        try:
            # Insight sobre sazonalidade
            if coluna_data in dados_df.columns and coluna_valor in dados_df.columns:
                vendas_por_mes = dados_df.groupby(dados_df[coluna_data].dt.month)[
                    coluna_valor].sum()
                if not vendas_por_mes.empty:
                    mes_pico = vendas_por_mes.idxmax()
                    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    insights.append(
                        f"O mês com maior faturamento é {meses[mes_pico-1]}")

            # Insight sobre itens do menu
            if 'nome_item' in dados_df.columns and coluna_valor in dados_df.columns:
                item_top = dados_df.groupby('nome_item')[
                    coluna_valor].sum().idxmax()
                insights.append(f"O item mais vendido em valor é: {item_top}")

            # Insight sobre categorias
            if 'categoria' in dados_df.columns and coluna_valor in dados_df.columns:
                categoria_top = dados_df.groupby(
                    'categoria')[coluna_valor].sum().idxmax()
                insights.append(
                    f"A categoria com melhor performance é: {categoria_top}")

            # Insight sobre funcionários
            if 'nome_funcionario' in dados_df.columns and coluna_valor in dados_df.columns:
                funcionario_top = dados_df.groupby('nome_funcionario')[
                    coluna_valor].sum().idxmax()
                insights.append(
                    f"O funcionário com melhor performance é: {funcionario_top}")

            # Insight sobre ticket médio
            if 'guest_check_id' in dados_df.columns and coluna_valor in dados_df.columns:
                ticket_medio = dados_df.groupby('guest_check_id')[
                    coluna_valor].sum().mean()
                if ticket_medio > 100:
                    insights.append(
                        f"O ticket médio é alto (R$ {ticket_medio:.2f}), indicando bom valor por comanda")
                else:
                    insights.append(
                        f"O ticket médio é moderado (R$ {ticket_medio:.2f}), foco em aumentar itens por comanda")

            # Insight sobre mesas
            if 'numero_mesa' in dados_df.columns and coluna_valor in dados_df.columns:
                mesa_top = dados_df.groupby('numero_mesa')[
                    coluna_valor].sum().idxmax()
                insights.append(
                    f"A mesa com maior faturamento é a Mesa {mesa_top}")

            # Insight sobre horários (se disponível)
            if 'hora' in dados_df.columns and coluna_valor in dados_df.columns:
                hora_pico = dados_df.groupby(
                    'hora')[coluna_valor].sum().idxmax()
                insights.append(f"O horário de pico é às {hora_pico}h")

            # Insight sobre dias da semana
            if 'dia_semana' in dados_df.columns and coluna_valor in dados_df.columns:
                dias_semana_pt = {
                    'Monday': 'Segunda-feira',
                    'Tuesday': 'Terça-feira',
                    'Wednesday': 'Quarta-feira',
                    'Thursday': 'Quinta-feira',
                    'Friday': 'Sexta-feira',
                    'Saturday': 'Sábado',
                    'Sunday': 'Domingo'
                }
                dia_top = dados_df.groupby('dia_semana')[
                    coluna_valor].sum().idxmax()
                dia_nome = dias_semana_pt.get(dia_top, dia_top)
                insights.append(
                    f"O dia da semana com maior movimento é {dia_nome}")

            # Insight sobre preços
            if 'preco_unitario' in dados_df.columns:
                preco_medio = dados_df['preco_unitario'].mean()
                if preco_medio > 30:
                    insights.append(
                        f"O preço médio dos itens é alto (R$ {preco_medio:.2f}), posicionamento premium")
                else:
                    insights.append(
                        f"O preço médio dos itens é acessível (R$ {preco_medio:.2f}), foco em volume")

        except Exception as erro:
            logger.warning(f"Erro ao gerar insights: {erro}")
            insights.append(
                "Dados insuficientes para gerar insights detalhados")

        if not insights:
            insights.append(
                "Nenhum insight específico pôde ser gerado com os dados disponíveis")

        logger.info(
            f"Gerados {len(insights)} insights automáticos do restaurante")
        return insights
