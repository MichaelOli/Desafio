"""
Desafio 1 - Parte 2: Modelagem SQL
Converte a estrutura JSON para um modelo relacional normalizado.
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ModeladorSQL:
    """Modelador SQL para converter estrutura JSON em tabelas relacionais."""

    def __init__(self):
        self.tabelas = {}
        self.relacionamentos = []
        self.indices = []
        self.restricoes = []

    def criar_modelo_relacional(self, caminho_arquivo_json: str) -> Dict[str, Any]:
        """
        Cria modelo relacional baseado na estrutura JSON.

        Args:
            caminho_arquivo_json: Caminho para o arquivo JSON

        Returns:
            Dicionário com modelo relacional completo
        """
        logger.info("Criando modelo relacional para dados de restaurante")

        try:
            # Carregar dados JSON
            with open(caminho_arquivo_json, 'r', encoding='utf-8') as arquivo:
                dados_exemplo = json.load(arquivo)

            # Criar tabelas principais
            self._criar_tabela_comandas_cliente()
            self._criar_tabela_linhas_detalhe()
            self._criar_tabela_itens_menu()
            self._criar_tabela_impostos()
            self._criar_tabela_descontos()
            self._criar_tabela_taxas_servico()
            self._criar_tabela_meios_pagamento()
            self._criar_tabela_codigos_erro()

            # Definir relacionamentos
            self._definir_relacionamentos()

            # Criar índices
            self._criar_indices()

            # Definir restrições
            self._definir_restricoes()

            # Gerar modelo completo
            modelo = self._gerar_modelo_completo()

            logger.info("Modelo relacional criado com sucesso")
            return modelo

        except Exception as erro:
            logger.error(f"Erro ao criar modelo relacional: {erro}")
            raise

    def _criar_tabela_comandas_cliente(self):
        """Cria tabela principal de comandas."""

        self.tabelas['comandas_cliente'] = {
            'descricao': 'Tabela principal de comandas/pedidos',
            'proposito_negocio': 'Armazena informações gerais de cada pedido do cliente',
            'colunas': {
                'id_comanda_cliente': {
                    'tipo': 'UUID',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único da comanda'
                },
                'numero_comanda': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número sequencial da comanda'
                },
                'data_abertura_negocio': {
                    'tipo': 'DATE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Data de abertura da comanda'
                },
                'abertura_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Timestamp de abertura em UTC'
                },
                'abertura_local': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Timestamp de abertura local'
                },
                'data_fechamento_negocio': {
                    'tipo': 'DATE',
                    'restricoes': [],
                    'descricao': 'Data de fechamento da comanda'
                },
                'fechamento_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': [],
                    'descricao': 'Timestamp de fechamento em UTC'
                },
                'fechamento_local': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': [],
                    'descricao': 'Timestamp de fechamento local'
                },
                'ultima_transacao_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': [],
                    'descricao': 'Última transação em UTC'
                },
                'ultima_atualizacao_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Última atualização do registro'
                },
                'flag_fechada': {
                    'tipo': 'BOOLEAN',
                    'restricoes': ['DEFAULT FALSE'],
                    'descricao': 'Indica se a comanda está fechada'
                },
                'contagem_clientes': {
                    'tipo': 'INTEGER',
                    'restricoes': ['CHECK (contagem_clientes >= 0)'],
                    'descricao': 'Número de clientes na mesa'
                },
                'subtotal': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['CHECK (subtotal >= 0)'],
                    'descricao': 'Subtotal antes de impostos e descontos'
                },
                'total_vendas_nao_tributaveis': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['DEFAULT 0.00'],
                    'descricao': 'Total de vendas não tributáveis'
                },
                'total_comanda': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['CHECK (total_comanda >= 0)'],
                    'descricao': 'Total final da comanda'
                },
                'total_desconto': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['DEFAULT 0.00'],
                    'descricao': 'Total de descontos aplicados'
                },
                'total_pagamento': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['DEFAULT 0.00'],
                    'descricao': 'Total pago'
                },
                'total_saldo_devedor': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['DEFAULT 0.00'],
                    'descricao': 'Saldo devedor'
                },
                'numero_centro_receita': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número do centro de receita'
                },
                'numero_tipo_pedido': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Tipo de pedido'
                },
                'numero_canal_pedido': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Canal do pedido'
                },
                'numero_mesa': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número da mesa'
                },
                'nome_mesa': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'Nome/identificação da mesa'
                },
                'numero_funcionario': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número do funcionário responsável'
                },
                'contagem_rodadas_servico': {
                    'tipo': 'INTEGER',
                    'restricoes': ['DEFAULT 1'],
                    'descricao': 'Número de rodadas de serviço'
                },
                'contagem_impressoes_comanda': {
                    'tipo': 'INTEGER',
                    'restricoes': ['DEFAULT 0'],
                    'descricao': 'Número de vezes que a comanda foi impressa'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                },
                'atualizado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de última atualização'
                }
            }
        }

    def _criar_tabela_linhas_detalhe(self):
        """Cria tabela de linhas de detalhe."""

        self.tabelas['linhas_detalhe_comanda'] = {
            'descricao': 'Linhas de detalhe das comandas',
            'proposito_negocio': 'Cada linha representa um item, desconto, taxa ou erro na comanda',
            'colunas': {
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único da linha'
                },
                'id_comanda_cliente': {
                    'tipo': 'UUID',
                    'restricoes': ['NOT NULL', 'REFERENCES comandas_cliente(id_comanda_cliente)'],
                    'descricao': 'Referência à comanda principal'
                },
                'numero_centro_receita': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Centro de receita'
                },
                'numero_tipo_pedido_detalhe': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Tipo de pedido do detalhe'
                },
                'numero_canal_pedido_detalhe': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Canal do pedido do detalhe'
                },
                'numero_linha': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número sequencial da linha'
                },
                'id_detalhe': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'ID do detalhe'
                },
                'detalhe_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Timestamp do detalhe em UTC'
                },
                'detalhe_local': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Timestamp do detalhe local'
                },
                'ultima_atualizacao_utc': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Última atualização em UTC'
                },
                'data_negocio': {
                    'tipo': 'DATE',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Data do negócio'
                },
                'numero_estacao_trabalho': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número da estação de trabalho'
                },
                'total_exibicao': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': [],
                    'descricao': 'Total exibido'
                },
                'quantidade_exibicao': {
                    'tipo': 'DECIMAL(8,3)',
                    'restricoes': [],
                    'descricao': 'Quantidade exibida'
                },
                'total_agregado': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': [],
                    'descricao': 'Total agregado'
                },
                'quantidade_agregada': {
                    'tipo': 'DECIMAL(8,3)',
                    'restricoes': [],
                    'descricao': 'Quantidade agregada'
                },
                'id_funcionario_comanda': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'ID do funcionário da comanda'
                },
                'numero_funcionario_comanda': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número do funcionário da comanda'
                },
                'numero_rodada_servico': {
                    'tipo': 'INTEGER',
                    'restricoes': ['DEFAULT 1'],
                    'descricao': 'Número da rodada de serviço'
                },
                'numero_assento': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Número do assento/posição'
                },
                'tipo_linha': {
                    'tipo': 'VARCHAR(50)',
                    'restricoes': ['CHECK (tipo_linha IN (\'menu_item\', \'discount\', \'service_charge\', \'tender_media\', \'error_code\'))'],
                    'descricao': 'Tipo da linha de detalhe'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                },
                'atualizado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de última atualização'
                }
            }
        }

    def _criar_tabela_itens_menu(self):
        """Cria tabela de itens do menu."""

        self.tabelas['itens_menu'] = {
            'descricao': 'Itens do cardápio/menu',
            'proposito_negocio': 'Catálogo de produtos disponíveis no restaurante',
            'colunas': {
                'id_item_menu': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único do item'
                },
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['REFERENCES linhas_detalhe_comanda(id_linha_item_comanda)'],
                    'descricao': 'Referência à linha de detalhe'
                },
                'numero_item_menu': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número do item no sistema'
                },
                'flag_modificacao': {
                    'tipo': 'BOOLEAN',
                    'restricoes': ['DEFAULT FALSE'],
                    'descricao': 'Indica se o item foi modificado'
                },
                'imposto_incluido': {
                    'tipo': 'DECIMAL(10,2)',
                    'restricoes': ['DEFAULT 0.00'],
                    'descricao': 'Imposto incluído no preço'
                },
                'impostos_ativos': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'Impostos ativos para o item'
                },
                'nivel_preco': {
                    'tipo': 'INTEGER',
                    'restricoes': ['DEFAULT 1'],
                    'descricao': 'Nível de preço aplicado'
                },
                'nome_item': {
                    'tipo': 'VARCHAR(255)',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Nome do item'
                },
                'nome_categoria': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'Nome da categoria'
                },
                'id_categoria': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'ID da categoria'
                },
                'nome_grupo_familia': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'Nome do grupo familiar'
                },
                'id_grupo_familia': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': [],
                    'descricao': 'ID do grupo familiar'
                },
                'preco_unitario': {
                    'tipo': 'DECIMAL(10,2)',
                    'restricoes': ['CHECK (preco_unitario >= 0)'],
                    'descricao': 'Preço unitário'
                },
                'total_exibicao': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': [],
                    'descricao': 'Total exibido'
                },
                'quantidade_exibicao': {
                    'tipo': 'DECIMAL(8,3)',
                    'restricoes': ['CHECK (quantidade_exibicao > 0)'],
                    'descricao': 'Quantidade exibida'
                },
                'total_agregado': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': [],
                    'descricao': 'Total agregado'
                },
                'quantidade_agregada': {
                    'tipo': 'DECIMAL(8,3)',
                    'restricoes': ['CHECK (quantidade_agregada > 0)'],
                    'descricao': 'Quantidade agregada'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                },
                'atualizado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de última atualização'
                }
            }
        }

    def _criar_tabela_impostos(self):
        """Cria tabela de impostos."""

        self.tabelas['impostos_comanda_cliente'] = {
            'descricao': 'Impostos aplicados às comandas',
            'proposito_negocio': 'Registro de todos os impostos incidentes sobre as vendas',
            'colunas': {
                'id': {
                    'tipo': 'SERIAL',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Chave primária sequencial'
                },
                'id_comanda_cliente': {
                    'tipo': 'UUID',
                    'restricoes': ['NOT NULL', 'REFERENCES comandas_cliente(id_comanda_cliente)'],
                    'descricao': 'Referência à comanda'
                },
                'numero_imposto': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número do imposto'
                },
                'total_vendas_tributaveis': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['CHECK (total_vendas_tributaveis >= 0)'],
                    'descricao': 'Total de vendas tributáveis'
                },
                'total_imposto_coletado': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['CHECK (total_imposto_coletado >= 0)'],
                    'descricao': 'Total de imposto coletado'
                },
                'taxa_imposto': {
                    'tipo': 'DECIMAL(5,2)',
                    'restricoes': ['CHECK (taxa_imposto >= 0 AND taxa_imposto <= 100)'],
                    'descricao': 'Taxa de imposto em percentual'
                },
                'tipo_imposto': {
                    'tipo': 'INTEGER',
                    'restricoes': [],
                    'descricao': 'Tipo de imposto'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                }
            }
        }

    def _criar_tabela_descontos(self):
        """Cria tabela de descontos."""

        self.tabelas['descontos'] = {
            'descricao': 'Descontos aplicados',
            'proposito_negocio': 'Registro de todos os descontos concedidos',
            'colunas': {
                'id_desconto': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único do desconto'
                },
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['REFERENCES linhas_detalhe_comanda(id_linha_item_comanda)'],
                    'descricao': 'Referência à linha de detalhe'
                },
                'numero_desconto': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número do desconto'
                },
                'nome_desconto': {
                    'tipo': 'VARCHAR(255)',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Nome do desconto'
                },
                'tipo_desconto': {
                    'tipo': 'VARCHAR(50)',
                    'restricoes': ['CHECK (tipo_desconto IN (\'percentage\', \'fixed_amount\', \'buy_x_get_y\'))'],
                    'descricao': 'Tipo de desconto'
                },
                'valor_desconto': {
                    'tipo': 'DECIMAL(10,2)',
                    'restricoes': ['CHECK (valor_desconto >= 0)'],
                    'descricao': 'Valor do desconto'
                },
                'quantia_desconto': {
                    'tipo': 'DECIMAL(10,2)',
                    'restricoes': ['CHECK (quantia_desconto >= 0)'],
                    'descricao': 'Valor monetário do desconto'
                },
                'aplicado_a': {
                    'tipo': 'VARCHAR(50)',
                    'restricoes': [],
                    'descricao': 'A que o desconto foi aplicado'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                }
            }
        }

    def _criar_tabela_taxas_servico(self):
        """Cria tabela de taxas de serviço."""

        self.tabelas['taxas_servico'] = {
            'descricao': 'Taxas de serviço aplicadas',
            'proposito_negocio': 'Registro de taxas adicionais como gorjetas automáticas',
            'colunas': {
                'id_taxa_servico': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único da taxa'
                },
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['REFERENCES linhas_detalhe_comanda(id_linha_item_comanda)'],
                    'descricao': 'Referência à linha de detalhe'
                },
                'numero_taxa_servico': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número da taxa de serviço'
                },
                'nome_taxa_servico': {
                    'tipo': 'VARCHAR(255)',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Nome da taxa de serviço'
                },
                'tipo_taxa_servico': {
                    'tipo': 'VARCHAR(50)',
                    'restricoes': [],
                    'descricao': 'Tipo da taxa de serviço'
                },
                'quantia_taxa_servico': {
                    'tipo': 'DECIMAL(10,2)',
                    'restricoes': ['CHECK (quantia_taxa_servico >= 0)'],
                    'descricao': 'Valor da taxa de serviço'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                }
            }
        }

    def _criar_tabela_meios_pagamento(self):
        """Cria tabela de meios de pagamento."""

        self.tabelas['meios_pagamento'] = {
            'descricao': 'Meios de pagamento utilizados',
            'proposito_negocio': 'Registro dos métodos de pagamento das comandas',
            'colunas': {
                'id_meio_pagamento': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único do meio de pagamento'
                },
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['REFERENCES linhas_detalhe_comanda(id_linha_item_comanda)'],
                    'descricao': 'Referência à linha de detalhe'
                },
                'numero_meio_pagamento': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número do meio de pagamento'
                },
                'nome_meio_pagamento': {
                    'tipo': 'VARCHAR(255)',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Nome do meio de pagamento'
                },
                'tipo_meio_pagamento': {
                    'tipo': 'VARCHAR(50)',
                    'restricoes': ['CHECK (tipo_meio_pagamento IN (\'cash\', \'credit_card\', \'debit_card\', \'pix\', \'voucher\'))'],
                    'descricao': 'Tipo do meio de pagamento'
                },
                'quantia_pagamento': {
                    'tipo': 'DECIMAL(12,2)',
                    'restricoes': ['CHECK (quantia_pagamento > 0)'],
                    'descricao': 'Valor pago'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                }
            }
        }

    def _criar_tabela_codigos_erro(self):
        """Cria tabela de códigos de erro."""

        self.tabelas['codigos_erro'] = {
            'descricao': 'Códigos de erro registrados',
            'proposito_negocio': 'Registro de erros ocorridos durante o processamento',
            'colunas': {
                'id_codigo_erro': {
                    'tipo': 'VARCHAR(100)',
                    'restricoes': ['PRIMARY KEY'],
                    'descricao': 'Identificador único do erro'
                },
                'id_linha_item_comanda': {
                    'tipo': 'UUID',
                    'restricoes': ['REFERENCES linhas_detalhe_comanda(id_linha_item_comanda)'],
                    'descricao': 'Referência à linha de detalhe'
                },
                'numero_codigo_erro': {
                    'tipo': 'INTEGER',
                    'restricoes': ['NOT NULL'],
                    'descricao': 'Número do código de erro'
                },
                'descricao_erro': {
                    'tipo': 'TEXT',
                    'restricoes': [],
                    'descricao': 'Descrição do erro'
                },
                'severidade_erro': {
                    'tipo': 'VARCHAR(20)',
                    'restricoes': ['CHECK (severidade_erro IN (\'low\', \'medium\', \'high\', \'critical\'))'],
                    'descricao': 'Severidade do erro'
                },
                'criado_em': {
                    'tipo': 'TIMESTAMP WITH TIME ZONE',
                    'restricoes': ['DEFAULT CURRENT_TIMESTAMP'],
                    'descricao': 'Data de criação do registro'
                }
            }
        }

    def _definir_relacionamentos(self):
        """Define relacionamentos entre tabelas."""

        self.relacionamentos = [
            {
                'nome': 'fk_linhas_detalhe_comanda_cliente',
                'tabela_pai': 'comandas_cliente',
                'coluna_pai': 'id_comanda_cliente',
                'tabela_filha': 'linhas_detalhe_comanda',
                'coluna_filha': 'id_comanda_cliente',
                'tipo_relacionamento': 'um_para_muitos',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma comanda pode ter múltiplas linhas de detalhe'
            },
            {
                'nome': 'fk_itens_menu_linha_detalhe',
                'tabela_pai': 'linhas_detalhe_comanda',
                'coluna_pai': 'id_linha_item_comanda',
                'tabela_filha': 'itens_menu',
                'coluna_filha': 'id_linha_item_comanda',
                'tipo_relacionamento': 'um_para_um',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma linha de detalhe pode ter um item do menu'
            },
            {
                'nome': 'fk_impostos_comanda_cliente',
                'tabela_pai': 'comandas_cliente',
                'coluna_pai': 'id_comanda_cliente',
                'tabela_filha': 'impostos_comanda_cliente',
                'coluna_filha': 'id_comanda_cliente',
                'tipo_relacionamento': 'um_para_muitos',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma comanda pode ter múltiplos impostos'
            },
            {
                'nome': 'fk_descontos_linha_detalhe',
                'tabela_pai': 'linhas_detalhe_comanda',
                'coluna_pai': 'id_linha_item_comanda',
                'tabela_filha': 'descontos',
                'coluna_filha': 'id_linha_item_comanda',
                'tipo_relacionamento': 'um_para_um',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma linha de detalhe pode ter um desconto'
            },
            {
                'nome': 'fk_taxas_servico_linha_detalhe',
                'tabela_pai': 'linhas_detalhe_comanda',
                'coluna_pai': 'id_linha_item_comanda',
                'tabela_filha': 'taxas_servico',
                'coluna_filha': 'id_linha_item_comanda',
                'tipo_relacionamento': 'um_para_um',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma linha de detalhe pode ter uma taxa de serviço'
            },
            {
                'nome': 'fk_meios_pagamento_linha_detalhe',
                'tabela_pai': 'linhas_detalhe_comanda',
                'coluna_pai': 'id_linha_item_comanda',
                'tabela_filha': 'meios_pagamento',
                'coluna_filha': 'id_linha_item_comanda',
                'tipo_relacionamento': 'um_para_um',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma linha de detalhe pode ter um meio de pagamento'
            },
            {
                'nome': 'fk_codigos_erro_linha_detalhe',
                'tabela_pai': 'linhas_detalhe_comanda',
                'coluna_pai': 'id_linha_item_comanda',
                'tabela_filha': 'codigos_erro',
                'coluna_filha': 'id_linha_item_comanda',
                'tipo_relacionamento': 'um_para_um',
                'ao_deletar': 'CASCADE',
                'descricao': 'Uma linha de detalhe pode ter um código de erro'
            }
        ]

    def _criar_indices(self):
        """Define índices para otimização de performance."""

        self.indices = [
            {
                'nome': 'idx_comandas_cliente_data_negocio',
                'tabela': 'comandas_cliente',
                'colunas': ['data_abertura_negocio'],
                'tipo': 'btree',
                'descricao': 'Índice para consultas por data de negócio'
            },
            {
                'nome': 'idx_comandas_cliente_numero_mesa',
                'tabela': 'comandas_cliente',
                'colunas': ['numero_mesa', 'data_abertura_negocio'],
                'tipo': 'btree',
                'descricao': 'Índice para consultas por mesa e data'
            },
            {
                'nome': 'idx_linhas_detalhe_id_comanda_cliente',
                'tabela': 'linhas_detalhe_comanda',
                'colunas': ['id_comanda_cliente'],
                'tipo': 'btree',
                'descricao': 'Índice para join com tabela principal'
            },
            {
                'nome': 'idx_linhas_detalhe_data_negocio',
                'tabela': 'linhas_detalhe_comanda',
                'colunas': ['data_negocio'],
                'tipo': 'btree',
                'descricao': 'Índice para consultas por data'
            },
            {
                'nome': 'idx_itens_menu_categoria',
                'tabela': 'itens_menu',
                'colunas': ['nome_categoria'],
                'tipo': 'btree',
                'descricao': 'Índice para consultas por categoria'
            },
            {
                'nome': 'idx_impostos_id_comanda_cliente',
                'tabela': 'impostos_comanda_cliente',
                'colunas': ['id_comanda_cliente'],
                'tipo': 'btree',
                'descricao': 'Índice para join com comandas'
            }
        ]

    def _definir_restricoes(self):
        """Define restrições de integridade."""

        self.restricoes = [
            {
                'nome': 'chk_totais_comanda_cliente',
                'tabela': 'comandas_cliente',
                'tipo': 'check',
                'definicao': 'total_comanda >= 0 AND subtotal >= 0',
                'descricao': 'Garante que totais sejam não-negativos'
            },
            {
                'nome': 'chk_consistencia_flag_fechada',
                'tabela': 'comandas_cliente',
                'tipo': 'check',
                'definicao': '(flag_fechada = true AND data_fechamento_negocio IS NOT NULL) OR (flag_fechada = false)',
                'descricao': 'Se fechado, deve ter data de fechamento'
            },
            {
                'nome': 'chk_faixa_taxa_imposto',
                'tabela': 'impostos_comanda_cliente',
                'tipo': 'check',
                'definicao': 'taxa_imposto >= 0 AND taxa_imposto <= 100',
                'descricao': 'Taxa de imposto deve estar entre 0 e 100%'
            },
            {
                'nome': 'chk_quantias_positivas',
                'tabela': 'itens_menu',
                'tipo': 'check',
                'definicao': 'preco_unitario >= 0 AND quantidade_exibicao > 0',
                'descricao': 'Preços e quantidades devem ser positivos'
            }
        ]

    def _gerar_modelo_completo(self) -> Dict[str, Any]:
        """Gera modelo completo com todas as informações."""

        return {
            'metadados_modelo': {
                'criado_em': datetime.now().isoformat(),
                'versao': '1.0',
                'descricao': 'Modelo relacional para sistema ERP de restaurante',
                'nivel_normalizacao': '3NF',
                'total_tabelas': len(self.tabelas)
            },
            'tabelas': self.tabelas,
            'relacionamentos': self.relacionamentos,
            'indices': self.indices,
            'restricoes': self.restricoes,
            'regras_negocio': self._definir_regras_negocio(),
            'consideracoes_performance': self._definir_consideracoes_performance(),
            'governanca_dados': self._definir_governanca_dados()
        }

    def _definir_regras_negocio(self) -> List[Dict[str, str]]:
        """Define regras de negócio implementadas."""

        return [
            {
                'regra': 'Integridade de Totais',
                'descricao': 'O total da comanda deve ser igual ao subtotal + impostos - descontos',
                'implementacao': 'Triggers e restrições de validação'
            },
            {
                'regra': 'Sequencialidade de Linhas',
                'descricao': 'Linhas de detalhe devem ter numeração sequencial por comanda',
                'implementacao': 'Restrição UNIQUE(id_comanda_cliente, numero_linha)'
            },
            {
                'regra': 'Consistência Temporal',
                'descricao': 'Data de fechamento deve ser >= data de abertura',
                'implementacao': 'Check constraint temporal'
            },
            {
                'regra': 'Validação de Status',
                'descricao': 'Comandas fechadas devem ter todos os campos obrigatórios preenchidos',
                'implementacao': 'Trigger de validação no fechamento'
            }
        ]

    def _definir_consideracoes_performance(self) -> List[Dict[str, str]]:
        """Define considerações de performance."""

        return [
            {
                'aspecto': 'Particionamento',
                'recomendacao': 'Particionar tabelas principais por data de negócio',
                'beneficio': 'Melhora performance de consultas temporais'
            },
            {
                'aspecto': 'Índices Compostos',
                'recomendacao': 'Criar índices compostos para consultas frequentes',
                'beneficio': 'Reduz tempo de resposta em relatórios'
            },
            {
                'aspecto': 'Arquivamento',
                'recomendacao': 'Implementar estratégia de arquivamento de dados antigos',
                'beneficio': 'Mantém tabelas com tamanho gerenciável'
            },
            {
                'aspecto': 'Materialização',
                'recomendacao': 'Criar views materializadas para relatórios complexos',
                'beneficio': 'Acelera consultas analíticas'
            }
        ]

    def _definir_governanca_dados(self) -> Dict[str, Any]:
        """Define políticas de governança de dados."""

        return {
            'politicas_retencao': {
                'dados_transacionais': '7 anos (conforme legislação fiscal)',
                'logs_auditoria': '5 anos',
                'logs_erro': '2 anos'
            },
            'estrategia_backup': {
                'frequencia': 'Diário para dados transacionais',
                'retencao': '30 dias backup completo, 1 ano backup incremental',
                'teste': 'Teste de restore mensal'
            },
            'controle_acesso': {
                'principio': 'Menor privilégio',
                'papeis': ['somente_leitura', 'operador', 'gerente', 'admin'],
                'auditoria': 'Log de todos os acessos e modificações'
            },
            'qualidade_dados': {
                'validacao': 'Validação em tempo real via restrições',
                'monitoramento': 'Alertas para anomalias nos dados',
                'correcao': 'Processo formal para correção de dados'
            }
        }

    def gerar_script_ddl(self, modelo: Dict[str, Any]) -> str:
        """Gera script DDL completo."""

        script_ddl = []

        # Cabeçalho
        script_ddl.append(
            "-- =====================================================")
        script_ddl.append("-- SCRIPT DDL - SISTEMA ERP RESTAURANTE")
        script_ddl.append(
            f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        script_ddl.append(
            "-- =====================================================")
        script_ddl.append("")

        # Criar tabelas
        script_ddl.append("-- CRIAÇÃO DE TABELAS")
        script_ddl.append(
            "-- =====================================================")

        for nome_tabela, info_tabela in modelo['tabelas'].items():
            script_ddl.append(f"\n-- Tabela: {nome_tabela}")
            script_ddl.append(f"-- {info_tabela['descricao']}")
            script_ddl.append(f"CREATE TABLE {nome_tabela} (")

            colunas = []
            for nome_coluna, info_coluna in info_tabela['colunas'].items():
                definicao_coluna = f"    {nome_coluna} {info_coluna['tipo']}"
                if info_coluna['restricoes']:
                    definicao_coluna += " " + \
                        " ".join(info_coluna['restricoes'])
                colunas.append(definicao_coluna)

            script_ddl.append(",\n".join(colunas))
            script_ddl.append(");")
            script_ddl.append("")

        # Criar índices
        script_ddl.append("\n-- CRIAÇÃO DE ÍNDICES")
        script_ddl.append(
            "-- =====================================================")

        for indice in modelo['indices']:
            colunas_str = ", ".join(indice['colunas'])
            script_ddl.append(
                f"CREATE INDEX {indice['nome']} ON {indice['tabela']} ({colunas_str});")

        # Comentários
        script_ddl.append("\n-- COMENTÁRIOS NAS TABELAS E COLUNAS")
        script_ddl.append(
            "-- =====================================================")

        for nome_tabela, info_tabela in modelo['tabelas'].items():
            script_ddl.append(
                f"COMMENT ON TABLE {nome_tabela} IS '{info_tabela['descricao']}';")

            for nome_coluna, info_coluna in info_tabela['colunas'].items():
                script_ddl.append(
                    f"COMMENT ON COLUMN {nome_tabela}.{nome_coluna} IS '{info_coluna['descricao']}';")

        return "\n".join(script_ddl)


def main():
    """Função principal para executar a modelagem SQL."""

    logging.basicConfig(level=logging.INFO)

    modelador = ModeladorSQL()

    # Criar modelo relacional
    arquivo_erp = os.path.join("dados", "ERP.json")

    if not os.path.exists(arquivo_erp):
        logger.error(f"Arquivo não encontrado: {arquivo_erp}")
        return

    try:
        modelo = modelador.criar_modelo_relacional(arquivo_erp)

        # Salvar modelo
        os.makedirs("docs", exist_ok=True)
        os.makedirs("sql", exist_ok=True)

        arquivo_modelo = os.path.join("docs", "modelo_relacional.json")
        with open(arquivo_modelo, 'w', encoding='utf-8') as arquivo:
            json.dump(modelo, arquivo, indent=2,
                      ensure_ascii=False, default=str)

        # Gerar script DDL
        script_ddl = modelador.gerar_script_ddl(modelo)
        arquivo_ddl = os.path.join("sql", "criar_tabelas.sql")

        with open(arquivo_ddl, 'w', encoding='utf-8') as arquivo:
            arquivo.write(script_ddl)

        logger.info(f"Modelo salvo em: {arquivo_modelo}")
        logger.info(f"Script DDL salvo em: {arquivo_ddl}")

        # Exibir resumo
        print("\n" + "="*60)
        print("MODELO RELACIONAL - ERP RESTAURANTE")
        print("="*60)

        print(f"\nTABELAS CRIADAS: {len(modelo['tabelas'])}")
        for nome_tabela, info_tabela in modelo['tabelas'].items():
            print(f"   • {nome_tabela.upper()}: {info_tabela['descricao']}")

        print(f"\nRELACIONAMENTOS: {len(modelo['relacionamentos'])}")
        for rel in modelo['relacionamentos'][:3]:
            print(f"   • {rel['tabela_pai']} → {rel['tabela_filha']}")

        print(f"\nÍNDICES: {len(modelo['indices'])}")
        print(f"RESTRIÇÕES: {len(modelo['restricoes'])}")

        print(f"\nArquivos gerados:")
        print(f"   • {arquivo_modelo}")
        print(f"   • {arquivo_ddl}")

    except Exception as erro:
        logger.error(f"Erro na modelagem: {erro}")
        raise


if __name__ == "__main__":
    main()
