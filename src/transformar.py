"""
Módulo responsável pela transformação e limpeza de dados.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TransformadorDados:
    """Classe para transformar e limpar dados."""

    def __init__(self):
        self.historico_transformacoes = []

    def limpar_dados_restaurante(self, dados_df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e valida dados do restaurante.

        Args:
            dados_df: DataFrame com dados do restaurante

        Returns:
            DataFrame limpo e validado
        """
        logger.info("Iniciando limpeza dos dados do restaurante")
        dados_limpos = dados_df.copy()

        # Converter datas para datetime se ainda não foram
        if 'data_abertura' in dados_limpos.columns:
            dados_limpos['data_abertura'] = pd.to_datetime(
                dados_limpos['data_abertura'])
        if 'data_fechamento' in dados_limpos.columns:
            dados_limpos['data_fechamento'] = pd.to_datetime(
                dados_limpos['data_fechamento'])

        # Filtrar apenas registros de itens do menu para análise principal
        dados_itens = dados_limpos[dados_limpos['tipo_registro'] == 'item_menu'].copy(
        )

        # Remover registros com valores inválidos
        if 'quantidade' in dados_itens.columns:
            dados_itens = dados_itens[dados_itens['quantidade'] > 0]
        if 'preco_unitario' in dados_itens.columns:
            dados_itens = dados_itens[dados_itens['preco_unitario'] > 0]
        if 'valor_item' in dados_itens.columns:
            dados_itens = dados_itens[dados_itens['valor_item'] > 0]

        # Remover duplicatas baseadas em linha_id
        dados_itens = dados_itens.drop_duplicates(subset=['linha_id'])

        # Padronizar nomes
        if 'nome_item' in dados_itens.columns:
            dados_itens['nome_item'] = dados_itens['nome_item'].str.strip(
            ).str.title()
        if 'categoria' in dados_itens.columns:
            dados_itens['categoria'] = dados_itens['categoria'].str.strip(
            ).str.title()
        if 'nome_funcionario' in dados_itens.columns:
            dados_itens['nome_funcionario'] = dados_itens['nome_funcionario'].str.strip(
            ).str.title()

        # Adicionar colunas derivadas
        dados_itens['ano'] = dados_itens['data_abertura'].dt.year
        dados_itens['mes'] = dados_itens['data_abertura'].dt.month
        dados_itens['trimestre'] = dados_itens['data_abertura'].dt.quarter
        dados_itens['dia_semana'] = dados_itens['data_abertura'].dt.day_name()
        dados_itens['hora'] = dados_itens['data_abertura'].dt.hour

        # Calcular ticket médio por comanda
        ticket_por_comanda = dados_itens.groupby(
            'guest_check_id')['valor_item'].sum()
        dados_itens['ticket_comanda'] = dados_itens['guest_check_id'].map(
            ticket_por_comanda)

        registros_removidos = len(dados_df) - len(dados_itens)
        logger.info(
            f"Limpeza concluída. {registros_removidos} registros removidos")

        self.historico_transformacoes.append({
            'operacao': 'limpeza_restaurante',
            'registros_antes': len(dados_df),
            'registros_depois': len(dados_itens),
            'registros_removidos': registros_removidos
        })

        return dados_itens

    def calcular_metricas_restaurante(self, dados_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas agregadas específicas para restaurante.

        Args:
            dados_df: DataFrame com dados do restaurante limpos

        Returns:
            DataFrame com métricas calculadas
        """
        logger.info("Calculando métricas do restaurante")

        metricas = []

        # Métricas por item do menu
        if 'nome_item' in dados_df.columns:
            metricas_item = dados_df.groupby('nome_item').agg({
                'quantidade': 'sum',
                'valor_item': ['sum', 'mean'],
                'linha_id': 'count'
            }).round(2)

            metricas_item.columns = [
                'total_quantidade', 'total_vendas', 'preco_medio', 'numero_pedidos']
            metricas_item['categoria'] = 'item_menu'
            metricas_item = metricas_item.reset_index()
            metricas_item.rename(
                columns={'nome_item': 'dimensao'}, inplace=True)
            metricas.append(metricas_item)

        # Métricas por categoria
        if 'categoria' in dados_df.columns:
            metricas_categoria = dados_df.groupby('categoria').agg({
                'quantidade': 'sum',
                'valor_item': ['sum', 'mean'],
                'linha_id': 'count'
            }).round(2)

            metricas_categoria.columns = [
                'total_quantidade', 'total_vendas', 'preco_medio', 'numero_pedidos']
            metricas_categoria['categoria'] = 'categoria_menu'
            metricas_categoria = metricas_categoria.reset_index()
            metricas_categoria.rename(
                columns={'categoria': 'dimensao'}, inplace=True)
            metricas.append(metricas_categoria)

        # Métricas por funcionário
        if 'nome_funcionario' in dados_df.columns:
            metricas_funcionario = dados_df.groupby('nome_funcionario').agg({
                'quantidade': 'sum',
                'valor_item': ['sum', 'mean'],
                'guest_check_id': 'nunique'
            }).round(2)

            metricas_funcionario.columns = [
                'total_quantidade', 'total_vendas', 'ticket_medio', 'numero_comandas']
            metricas_funcionario['categoria'] = 'funcionario'
            metricas_funcionario = metricas_funcionario.reset_index()
            metricas_funcionario.rename(
                columns={'nome_funcionario': 'dimensao'}, inplace=True)
            metricas.append(metricas_funcionario)

        # Métricas por mesa
        if 'numero_mesa' in dados_df.columns:
            metricas_mesa = dados_df.groupby('numero_mesa').agg({
                'quantidade': 'sum',
                'valor_item': ['sum', 'mean'],
                'guest_check_id': 'nunique'
            }).round(2)

            metricas_mesa.columns = [
                'total_quantidade', 'total_vendas', 'ticket_medio', 'numero_comandas']
            metricas_mesa['categoria'] = 'mesa'
            metricas_mesa = metricas_mesa.reset_index()
            metricas_mesa['dimensao'] = 'Mesa ' + \
                metricas_mesa['numero_mesa'].astype(str)
            metricas_mesa = metricas_mesa.drop('numero_mesa', axis=1)
            metricas.append(metricas_mesa)

        # Combinar todas as métricas
        if metricas:
            metricas_df = pd.concat(metricas, ignore_index=True)
        else:
            metricas_df = pd.DataFrame()

        logger.info(
            f"Métricas do restaurante calculadas para {len(metricas_df)} dimensões")
        return metricas_df

    def criar_resumo_temporal(self, dados_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria resumo temporal das vendas.

        Args:
            dados_df: DataFrame com dados de vendas

        Returns:
            DataFrame com resumo temporal
        """
        logger.info("Criando resumo temporal das vendas")

        # Resumo mensal
        resumo_mensal = dados_df.groupby(['ano', 'mes']).agg({
            'valor_total': 'sum',
            'quantidade': 'sum',
            'id_venda': 'count'
        }).round(2)

        resumo_mensal.columns = ['vendas_total',
                                 'quantidade_total', 'numero_transacoes']
        resumo_mensal = resumo_mensal.reset_index()

        # Calcular crescimento mês a mês
        resumo_mensal = resumo_mensal.sort_values(['ano', 'mes'])
        resumo_mensal['crescimento_vendas'] = resumo_mensal['vendas_total'].pct_change(
        ).round(4)

        logger.info(
            f"Resumo temporal criado com {len(resumo_mensal)} períodos")
        return resumo_mensal

    def detectar_outliers(self, dados_df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """
        Detecta outliers usando o método IQR.

        Args:
            dados_df: DataFrame com os dados
            coluna: Nome da coluna para detectar outliers

        Returns:
            DataFrame com coluna indicando outliers
        """
        logger.info(f"Detectando outliers na coluna: {coluna}")

        dados_outliers = dados_df.copy()

        q1 = dados_df[coluna].quantile(0.25)
        q3 = dados_df[coluna].quantile(0.75)
        iqr = q3 - q1

        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr

        dados_outliers[f'{coluna}_outlier'] = (
            (dados_df[coluna] < limite_inferior) | (
                dados_df[coluna] > limite_superior)
        )

        numero_outliers = dados_outliers[f'{coluna}_outlier'].sum()
        logger.info(
            f"Detectados {numero_outliers} outliers na coluna {coluna}")

        return dados_outliers

    def validar_qualidade_dados(self, dados_df: pd.DataFrame) -> Dict:
        """
        Valida a qualidade dos dados.

        Args:
            dados_df: DataFrame para validar

        Returns:
            Dicionário com métricas de qualidade
        """
        logger.info("Validando qualidade dos dados")

        qualidade = {
            'total_registros': len(dados_df),
            'colunas': list(dados_df.columns),
            'valores_nulos': dados_df.isnull().sum().to_dict(),
            'duplicatas': dados_df.duplicated().sum(),
            'tipos_dados': dados_df.dtypes.to_dict(),
            'memoria_mb': round(dados_df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }

        # Calcular completude por coluna
        qualidade['completude'] = {}
        for coluna in dados_df.columns:
            completude = (
                1 - dados_df[coluna].isnull().sum() / len(dados_df)) * 100
            qualidade['completude'][coluna] = round(completude, 2)

        logger.info("Validação de qualidade concluída")
        return qualidade
