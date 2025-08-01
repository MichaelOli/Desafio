"""
Módulo responsável pela extração de dados de diferentes fontes.
"""

import pandas as pd
import requests
import json
import sqlite3
from typing import Dict, List, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtratorDados:
    """Classe para extrair dados de diferentes fontes."""

    def __init__(self):
        self.dados_extraidos = {}

    def extrair_csv(self, caminho_arquivo: str, codificacao: str = 'utf-8') -> pd.DataFrame:
        """
        Extrai dados de um arquivo CSV.

        Args:
            caminho_arquivo: Caminho para o arquivo CSV
            codificacao: Codificação do arquivo

        Returns:
            DataFrame com os dados extraídos
        """
        try:
            logger.info(f"Extraindo dados do arquivo CSV: {caminho_arquivo}")
            dados_df = pd.read_csv(caminho_arquivo, encoding=codificacao)
            logger.info(
                f"Dados extraídos com sucesso. Formato: {dados_df.shape}")
            return dados_df
        except Exception as erro:
            logger.error(f"Erro ao extrair dados do CSV: {erro}")
            raise

    def extrair_json(self, caminho_arquivo: str) -> List[Dict]:
        """
        Extrai dados de um arquivo JSON.

        Args:
            caminho_arquivo: Caminho para o arquivo JSON

        Returns:
            Lista de dicionários com os dados
        """
        try:
            logger.info(f"Extraindo dados do arquivo JSON: {caminho_arquivo}")
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
            logger.info(
                f"Dados JSON extraídos com sucesso. {len(dados)} registros")
            return dados
        except Exception as erro:
            logger.error(f"Erro ao extrair dados do JSON: {erro}")
            raise

    def extrair_api(self, url: str, cabecalhos: Optional[Dict] = None) -> Dict:
        """
        Extrai dados de uma API REST.

        Args:
            url: URL da API
            cabecalhos: Cabeçalhos opcionais para a requisição

        Returns:
            Dados da API em formato de dicionário
        """
        try:
            logger.info(f"Fazendo requisição para API: {url}")
            resposta = requests.get(url, headers=cabecalhos or {})
            resposta.raise_for_status()

            dados = resposta.json()
            logger.info(f"Dados da API extraídos com sucesso")
            return dados
        except Exception as erro:
            logger.error(f"Erro ao extrair dados da API: {erro}")
            raise

    def extrair_sqlite(self, caminho_bd: str, consulta: str) -> pd.DataFrame:
        """
        Extrai dados de um banco SQLite.

        Args:
            caminho_bd: Caminho para o arquivo do banco
            consulta: Query SQL para extrair os dados

        Returns:
            DataFrame com os dados extraídos
        """
        try:
            logger.info(f"Conectando ao banco SQLite: {caminho_bd}")
            conexao = sqlite3.connect(caminho_bd)
            dados_df = pd.read_sql_query(consulta, conexao)
            conexao.close()
            logger.info(
                f"Dados extraídos do SQLite. Formato: {dados_df.shape}")
            return dados_df
        except Exception as erro:
            logger.error(f"Erro ao extrair dados do SQLite: {erro}")
            raise

    def extrair_dados_erp_restaurante(self, caminho_arquivo: str = "dados/ERP.json") -> pd.DataFrame:
        """
        Extrai e processa dados do ERP de restaurante.

        Args:
            caminho_arquivo: Caminho para o arquivo ERP.json

        Returns:
            DataFrame com dados processados do restaurante
        """
        try:
            logger.info(
                f"Extraindo dados do ERP de restaurante: {caminho_arquivo}")

            # Carregar dados JSON
            dados_erp = self.extrair_json(caminho_arquivo)

            # Processar dados para análise
            registros_processados = []

            # Informações da comanda
            comanda_info = {
                'guest_check_id': dados_erp['guestCheckId'],
                'numero_comanda': dados_erp['chkNum'],
                'data_abertura': dados_erp['opnBusDt'],
                'data_fechamento': dados_erp['clsdBusDt'],
                'numero_mesa': dados_erp['tblNum'],
                'nome_mesa': dados_erp['tblName'],
                'numero_funcionario': dados_erp['empNum'],
                'numero_clientes': dados_erp['gstCnt'],
                'subtotal': dados_erp['subTtl'],
                'total_comanda': dados_erp['chkTtl'],
                'total_desconto': dados_erp['dscTtl'],
                'total_pago': dados_erp['payTtl'],
                'saldo_devido': dados_erp['balDueTtl']
            }

            # Processar itens do menu
            for item in dados_erp['detailLines']:
                if 'menuItem' in item:
                    menu_item = item['menuItem']
                    registro = {
                        **comanda_info,
                        'linha_id': item['guestCheckLineItemId'],
                        'numero_linha': item['lineNum'],
                        'numero_assento': item['seatNum'],
                        'item_id': menu_item['miNum'],
                        'nome_item': menu_item['itemName'],
                        'categoria': menu_item['categoryName'],
                        'grupo_familia': menu_item['familyGroupName'],
                        'preco_unitario': menu_item['unitPrice'],
                        'quantidade': menu_item['dspQty'],
                        'valor_item': menu_item['dspTtl'],
                        'imposto_incluso': menu_item['inclTax'],
                        'tipo_registro': 'item_menu'
                    }
                    registros_processados.append(registro)

                # Processar descontos
                elif 'discount' in item:
                    desconto = item['discount']
                    registro = {
                        **comanda_info,
                        'linha_id': item['guestCheckLineItemId'],
                        'numero_linha': item['lineNum'],
                        'numero_assento': item['seatNum'],
                        'desconto_id': desconto['dscNum'],
                        'nome_desconto': desconto['dscName'],
                        'tipo_desconto': desconto['dscType'],
                        'valor_desconto': desconto['dscValue'],
                        'valor_aplicado': abs(desconto['dscAmount']),
                        'aplicado_em': desconto['appliedTo'],
                        'tipo_registro': 'desconto'
                    }
                    registros_processados.append(registro)

            # Processar impostos
            for imposto in dados_erp['taxes']:
                registro = {
                    **comanda_info,
                    'numero_imposto': imposto['taxNum'],
                    'total_tributavel': imposto['txblSlsTtl'],
                    'valor_imposto': imposto['taxCollTtl'],
                    'aliquota_imposto': imposto['taxRate'],
                    'tipo_imposto': imposto['type'],
                    'tipo_registro': 'imposto'
                }
                registros_processados.append(registro)

            dados_df = pd.DataFrame(registros_processados)

            # Converter datas
            dados_df['data_abertura'] = pd.to_datetime(
                dados_df['data_abertura'])
            dados_df['data_fechamento'] = pd.to_datetime(
                dados_df['data_fechamento'])

            logger.info(
                f"Dados do ERP processados com sucesso. {len(dados_df)} registros criados")
            return dados_df

        except Exception as erro:
            logger.error(f"Erro ao extrair dados do ERP: {erro}")
            raise

    def gerar_dados_exemplo_restaurante(self, numero_comandas: int = 100) -> pd.DataFrame:
        """
        Gera dados de exemplo para restaurante baseados na estrutura real do ERP.

        Args:
            numero_comandas: Número de comandas a gerar

        Returns:
            DataFrame com dados simulados de restaurante
        """
        import random
        from datetime import datetime, timedelta

        logger.info(
            f"Gerando {numero_comandas} comandas de exemplo para restaurante")

        # Dados base realistas para restaurante
        itens_menu = [
            {'nome': 'Hambúrguer Artesanal', 'categoria': 'Lanches', 'preco': 22.75},
            {'nome': 'Pizza Margherita', 'categoria': 'Pizzas', 'preco': 28.50},
            {'nome': 'Lasanha Bolonhesa', 'categoria': 'Massas', 'preco': 24.90},
            {'nome': 'Salmão Grelhado', 'categoria': 'Peixes', 'preco': 35.00},
            {'nome': 'Risotto de Camarão', 'categoria': 'Risotos', 'preco': 32.00},
            {'nome': 'Salada Caesar', 'categoria': 'Saladas', 'preco': 18.50},
            {'nome': 'Coca-Cola', 'categoria': 'Bebidas', 'preco': 6.50},
            {'nome': 'Suco Natural', 'categoria': 'Bebidas', 'preco': 8.00},
            {'nome': 'Cerveja Artesanal', 'categoria': 'Bebidas', 'preco': 12.00},
            {'nome': 'Tiramisu', 'categoria': 'Sobremesas', 'preco': 15.00}
        ]

        funcionarios = [
            {'id': 1001, 'nome': 'Maria Silva'},
            {'id': 1002, 'nome': 'João Santos'},
            {'id': 1003, 'nome': 'Ana Costa'},
            {'id': 1004, 'nome': 'Pedro Lima'},
            {'id': 1005, 'nome': 'Carla Oliveira'}
        ]

        dados = []
        data_inicio = datetime.now() - timedelta(days=90)

        for i in range(numero_comandas):
            # Dados da comanda
            data_comanda = data_inicio + timedelta(days=random.randint(0, 90))
            funcionario = random.choice(funcionarios)
            numero_mesa = random.randint(1, 20)
            numero_clientes = random.randint(1, 6)

            # Número de itens na comanda (1-5 itens)
            num_itens = random.randint(1, 5)
            itens_comanda = random.sample(
                itens_menu, min(num_itens, len(itens_menu)))

            subtotal = 0

            for j, item in enumerate(itens_comanda):
                quantidade = random.randint(1, 3)
                valor_item = item['preco'] * quantidade
                subtotal += valor_item

                registro = {
                    'guest_check_id': f"check-{i+1:04d}",
                    'numero_comanda': 2000 + i,
                    'data_abertura': data_comanda.strftime('%Y-%m-%d'),
                    'data_fechamento': data_comanda.strftime('%Y-%m-%d'),
                    'numero_mesa': numero_mesa,
                    'nome_mesa': f"Mesa {numero_mesa}",
                    'numero_funcionario': funcionario['id'],
                    'nome_funcionario': funcionario['nome'],
                    'numero_clientes': numero_clientes,
                    'linha_id': f"line-{i+1:04d}-{j+1}",
                    'numero_linha': j + 1,
                    'numero_assento': random.randint(1, numero_clientes),
                    'item_id': 500 + (j * 10),
                    'nome_item': item['nome'],
                    'categoria': item['categoria'],
                    'preco_unitario': item['preco'],
                    'quantidade': quantidade,
                    'valor_item': valor_item,
                    'imposto_incluso': round(valor_item * 0.1, 2),
                    'tipo_registro': 'item_menu'
                }
                dados.append(registro)

            # Aplicar desconto ocasionalmente (20% das comandas)
            if random.random() < 0.2:
                desconto_valor = round(
                    subtotal * random.uniform(0.05, 0.15), 2)
                registro_desconto = {
                    'guest_check_id': f"check-{i+1:04d}",
                    'numero_comanda': 2000 + i,
                    'data_abertura': data_comanda.strftime('%Y-%m-%d'),
                    'data_fechamento': data_comanda.strftime('%Y-%m-%d'),
                    'numero_mesa': numero_mesa,
                    'nome_mesa': f"Mesa {numero_mesa}",
                    'numero_funcionario': funcionario['id'],
                    'nome_funcionario': funcionario['nome'],
                    'numero_clientes': numero_clientes,
                    'linha_id': f"discount-{i+1:04d}",
                    'numero_linha': len(itens_comanda) + 1,
                    'desconto_id': 101,
                    'nome_desconto': 'Desconto Promocional',
                    'tipo_desconto': 'percentage',
                    'valor_desconto': round((desconto_valor / subtotal) * 100, 2),
                    'valor_aplicado': desconto_valor,
                    'aplicado_em': 'total',
                    'tipo_registro': 'desconto'
                }
                dados.append(registro_desconto)

            # Calcular totais da comanda
            total_desconto = sum([d['valor_aplicado'] for d in dados if d.get(
                'tipo_registro') == 'desconto' and d['guest_check_id'] == f"check-{i+1:04d}"])
            total_comanda = subtotal - total_desconto
            imposto_total = round(total_comanda * 0.1, 2)

            # Atualizar registros com totais
            for registro in dados:
                if registro['guest_check_id'] == f"check-{i+1:04d}":
                    registro.update({
                        'subtotal': subtotal,
                        'total_comanda': total_comanda + imposto_total,
                        'total_desconto': total_desconto,
                        'total_pago': total_comanda + imposto_total,
                        'saldo_devido': 0.00
                    })

        dados_df = pd.DataFrame(dados)

        # Converter datas
        dados_df['data_abertura'] = pd.to_datetime(dados_df['data_abertura'])
        dados_df['data_fechamento'] = pd.to_datetime(
            dados_df['data_fechamento'])

        logger.info(
            f"Dados de restaurante gerados com sucesso. {len(dados_df)} registros criados")
        return dados_df

    def extrair_dados_data_lake(self, caminho_data_lake: str = "dados/data_lake") -> pd.DataFrame:
        """
        Extrai dados de todos os endpoints do data lake.

        Args:
            caminho_data_lake: Caminho para o data lake

        Returns:
            DataFrame consolidado com dados de todos os endpoints
        """
        import os
        import glob
        from pathlib import Path

        logger.info(f"Extraindo dados do data lake: {caminho_data_lake}")

        dados_consolidados = []

        # Endpoints disponíveis
        endpoints = [
            'bilgetFiscalInvoice',
            'getGuestChecks',
            'getChargeBack',
            'getTransactions',
            'getCashManagementDetails'
        ]

        for endpoint in endpoints:
            caminho_endpoint = os.path.join(
                caminho_data_lake, "dados_brutos", endpoint)

            if os.path.exists(caminho_endpoint):
                # Buscar todos os arquivos JSON do endpoint
                pattern = os.path.join(caminho_endpoint, "**", "*.json")
                arquivos = glob.glob(pattern, recursive=True)

                logger.info(
                    f"Encontrados {len(arquivos)} arquivos para endpoint {endpoint}")

                for arquivo in arquivos:
                    try:
                        dados_arquivo = self.extrair_json(arquivo)

                        # Extrair dados do arquivo (que tem estrutura com metadados e dados)
                        if 'dados' in dados_arquivo and 'metadados' in dados_arquivo:
                            registro = {
                                'endpoint': endpoint,
                                'data_negocio': dados_arquivo['metadados']['data_negocio'],
                                'id_loja': dados_arquivo['metadados']['id_loja'],
                                'timestamp_ingestao': dados_arquivo['metadados']['timestamp_ingestao'],
                                # Expandir dados específicos do endpoint
                                **dados_arquivo['dados']
                            }
                            dados_consolidados.append(registro)

                    except Exception as erro:
                        logger.warning(
                            f"Erro ao processar arquivo {arquivo}: {erro}")
                        continue

        if dados_consolidados:
            dados_df = pd.DataFrame(dados_consolidados)

            # Converter datas
            dados_df['data_negocio'] = pd.to_datetime(dados_df['data_negocio'])
            dados_df['timestamp_ingestao'] = pd.to_datetime(
                dados_df['timestamp_ingestao'])

            logger.info(
                f"Dados do data lake extraídos com sucesso. {len(dados_df)} registros de {len(endpoints)} endpoints")
            return dados_df
        else:
            logger.warning("Nenhum dado encontrado no data lake")
            return pd.DataFrame()

    def extrair_dados_combinados_restaurante(self) -> pd.DataFrame:
        """
        Combina dados do ERP.json com dados do data lake para análise completa.

        Returns:
            DataFrame combinado com dados do restaurante
        """
        logger.info("Extraindo dados combinados do restaurante")

        # Extrair dados do ERP principal
        try:
            dados_erp = self.extrair_dados_erp_restaurante()
            logger.info(f"Dados ERP extraídos: {len(dados_erp)} registros")
        except Exception as erro:
            logger.warning(
                f"Erro ao extrair dados ERP: {erro}. Usando dados simulados.")
            dados_erp = pd.DataFrame()

        # Extrair dados do data lake
        try:
            dados_data_lake = self.extrair_dados_data_lake()
            logger.info(
                f"Dados data lake extraídos: {len(dados_data_lake)} registros")
        except Exception as erro:
            logger.warning(f"Erro ao extrair dados do data lake: {erro}")
            dados_data_lake = pd.DataFrame()

        # Se não há dados reais, gerar dados simulados
        if dados_erp.empty and dados_data_lake.empty:
            logger.info("Gerando dados simulados para demonstração")
            return self.gerar_dados_exemplo_restaurante(200)

        # Se há dados do ERP, usar eles como base
        if not dados_erp.empty:
            return dados_erp

        # Caso contrário, processar dados do data lake
        if not dados_data_lake.empty:
            # Converter dados do data lake para formato similar ao ERP
            dados_processados = []

            for _, row in dados_data_lake.iterrows():
                if row['endpoint'] == 'getGuestChecks':
                    # Processar dados de comandas
                    registro = {
                        'guest_check_id': row.get('guestCheckId', f"check-{row.name}"),
                        'numero_comanda': row.get('chkNum', 1000 + row.name),
                        'data_abertura': row['data_negocio'],
                        'data_fechamento': row['data_negocio'],
                        'numero_mesa': row.get('tblNum', 1),
                        'nome_mesa': row.get('tblName', f"Mesa {row.get('tblNum', 1)}"),
                        'numero_funcionario': row.get('empNum', 1001),
                        'numero_clientes': row.get('gstCnt', 2),
                        'subtotal': row.get('subTtl', 0),
                        'total_comanda': row.get('chkTtl', 0),
                        'total_desconto': row.get('dscTtl', 0),
                        'total_pago': row.get('payTtl', 0),
                        'saldo_devido': row.get('balDueTtl', 0),
                        'tipo_registro': 'comanda_data_lake',
                        'endpoint_origem': row['endpoint'],
                        'id_loja': row['id_loja']
                    }
                    dados_processados.append(registro)

                elif row['endpoint'] == 'getCashManagementDetails':
                    # Processar dados de gestão de caixa
                    registro = {
                        'cash_management_id': row.get('cashManagementId', f"CM-{row.name}"),
                        'data_abertura': row['data_negocio'],
                        'saldo_abertura': row.get('openingBalance', 0),
                        'saldo_fechamento': row.get('closingBalance', 0),
                        'total_vendas_caixa': row.get('totalSales', 0),
                        'tipo_registro': 'gestao_caixa',
                        'endpoint_origem': row['endpoint'],
                        'id_loja': row['id_loja']
                    }
                    dados_processados.append(registro)

            if dados_processados:
                dados_df = pd.DataFrame(dados_processados)
                dados_df['data_abertura'] = pd.to_datetime(
                    dados_df['data_abertura'])
                return dados_df

        # Fallback para dados simulados
        logger.info("Usando dados simulados como fallback")
        return self.gerar_dados_exemplo_restaurante(200)
