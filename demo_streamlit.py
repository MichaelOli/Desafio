"""
Script de demonstração das funcionalidades Streamlit
Execute este script para ver um exemplo das novas visualizações
"""

from src.analisar import AnalisadorDados
from src.transformar import TransformadorDados
from src.extrair import ExtratorDados
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def demonstrar_funcionalidades():
    """Demonstra as funcionalidades do novo sistema de análise."""

    print("DEMONSTRAÇÃO DAS NOVAS FUNCIONALIDADES STREAMLIT")
    print("=" * 60)

    # Inicializar componentes
    extrator = ExtratorDados()
    transformador = TransformadorDados()
    analisador = AnalisadorDados()

    print("Gerando dados do restaurante...")
    dados_restaurante = extrator.extrair_dados_combinados_restaurante()

    print("Limpando e transformando dados...")
    dados_limpos = transformador.limpar_dados_restaurante(dados_restaurante)

    print("Gerando relatório do restaurante...")
    relatorio = analisador.gerar_relatorio_restaurante(dados_limpos)

    print("Analisando tendências...")
    tendencias = analisador.analisar_tendencias(dados_limpos)

    print("Gerando insights automáticos...")
    insights = analisador.gerar_insights_automaticos(dados_limpos)

    # Exibir resultados
    print("\n" + "=" * 60)
    print("RESULTADOS DA DEMONSTRAÇÃO")
    print("=" * 60)

    print(f"\nMÉTRICAS PRINCIPAIS:")
    print(
        f"   • Total de Vendas: R$ {relatorio['metricas_gerais']['total_vendas']:,.2f}")
    print(
        f"   • Ticket Médio: R$ {relatorio['metricas_gerais']['ticket_medio']:,.2f}")
    print(
        f"   • Total de Comandas: {relatorio['metricas_gerais']['total_comandas']:,}")
    print(
        f"   • Total de Itens: {relatorio['metricas_gerais']['total_itens']:,}")
    print(
        f"   • Preço Médio por Item: R$ {relatorio['metricas_gerais']['preco_medio_item']:,.2f}")

    print(f"\nANÁLISE DE TENDÊNCIAS:")
    print(
        f"   • Crescimento Médio Mensal: {tendencias['crescimento_medio_mensal']:.2f}%")
    print(f"   • Tendência Geral: {tendencias['tendencia_geral'].title()}")
    print(f"   • Volatilidade: {tendencias['volatilidade']:.2f}%")

    print(f"\nTOP ITENS DO MENU:")
    for i, (item, valor) in enumerate(list(relatorio['top_itens'].items())[:3], 1):
        print(f"   {i}. {item}: R$ {valor:,.2f}")

    print(f"\nINSIGHTS AUTOMÁTICOS:")
    for i, insight in enumerate(insights[:3], 1):
        print(f"   {i}. {insight}")

    print(f"\nCOMO USAR O DASHBOARD INTERATIVO:")
    print(f"   1. Execute: streamlit run app_streamlit.py")
    print(f"   2. Abra o navegador em: http://localhost:8501")
    print(f"   3. Explore os filtros e gráficos interativos!")

    print(f"\nVANTAGENS DO STREAMLIT:")
    print(f"   • Gráficos totalmente interativos")
    print(f"   • Filtros dinâmicos em tempo real")
    print(f"   • Interface web moderna e responsiva")
    print(f"   • Exportação de dados integrada")
    print(f"   • Fácil compartilhamento via URL")

    print("\n" + "=" * 60)
    print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrar_funcionalidades()
