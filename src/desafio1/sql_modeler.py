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


class SQLModeler:
    """Modelador SQL para converter estrutura JSON em tabelas relacionais."""

    def __init__(self):
        self.tables = {}
        self.relationships = []
        self.indexes = []
        self.constraints = []

    def create_relational_model(self, json_file_path: str) -> Dict[str, Any]:
        """
        Cria modelo relacional baseado na estrutura JSON.

        Args:
            json_file_path: Caminho para o arquivo JSON

        Returns:
            Dicionário com modelo relacional completo
        """
        logger.info("Criando modelo relacional para dados de restaurante")

        try:
            # Carregar dados JSON
            with open(json_file_path, 'r', encoding='utf-8') as file:
                sample_data = json.load(file)

            # Criar tabelas principais
            self._create_guest_check_table()
            self._create_detail_lines_table()
            self._create_menu_items_table()
            self._create_taxes_table()
            self._create_discounts_table()
            self._create_service_charges_table()
            self._create_tender_media_table()
            self._create_error_codes_table()

            # Definir relacionamentos
            self._define_relationships()

            # Criar índices
            self._create_indexes()

            # Definir constraints
            self._define_constraints()

            # Gerar modelo completo
            model = self._generate_complete_model()

            logger.info("Modelo relacional criado com sucesso")
            return model

        except Exception as e:
            logger.error(f"Erro ao criar modelo relacional: {e}")
            raise

    def _create_guest_check_table(self):
        """Cria tabela principal de comandas."""

        self.tables['guest_checks'] = {
            'description': 'Tabela principal de comandas/pedidos',
            'business_purpose': 'Armazena informações gerais de cada pedido do cliente',
            'columns': {
                'guest_check_id': {
                    'type': 'UUID',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único da comanda'
                },
                'check_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número sequencial da comanda'
                },
                'open_business_date': {
                    'type': 'DATE',
                    'constraints': ['NOT NULL'],
                    'description': 'Data de abertura da comanda'
                },
                'open_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['NOT NULL'],
                    'description': 'Timestamp de abertura em UTC'
                },
                'open_local': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['NOT NULL'],
                    'description': 'Timestamp de abertura local'
                },
                'closed_business_date': {
                    'type': 'DATE',
                    'constraints': [],
                    'description': 'Data de fechamento da comanda'
                },
                'closed_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': [],
                    'description': 'Timestamp de fechamento em UTC'
                },
                'closed_local': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': [],
                    'description': 'Timestamp de fechamento local'
                },
                'last_transaction_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': [],
                    'description': 'Última transação em UTC'
                },
                'last_updated_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Última atualização do registro'
                },
                'closed_flag': {
                    'type': 'BOOLEAN',
                    'constraints': ['DEFAULT FALSE'],
                    'description': 'Indica se a comanda está fechada'
                },
                'guest_count': {
                    'type': 'INTEGER',
                    'constraints': ['CHECK (guest_count >= 0)'],
                    'description': 'Número de clientes na mesa'
                },
                'subtotal': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['CHECK (subtotal >= 0)'],
                    'description': 'Subtotal antes de impostos e descontos'
                },
                'non_taxable_sales_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['DEFAULT 0.00'],
                    'description': 'Total de vendas não tributáveis'
                },
                'check_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['CHECK (check_total >= 0)'],
                    'description': 'Total final da comanda'
                },
                'discount_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['DEFAULT 0.00'],
                    'description': 'Total de descontos aplicados'
                },
                'payment_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['DEFAULT 0.00'],
                    'description': 'Total pago'
                },
                'balance_due_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['DEFAULT 0.00'],
                    'description': 'Saldo devedor'
                },
                'revenue_center_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número do centro de receita'
                },
                'order_type_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Tipo de pedido'
                },
                'order_channel_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Canal do pedido'
                },
                'table_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número da mesa'
                },
                'table_name': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'Nome/identificação da mesa'
                },
                'employee_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número do funcionário responsável'
                },
                'service_rounds_count': {
                    'type': 'INTEGER',
                    'constraints': ['DEFAULT 1'],
                    'description': 'Número de rodadas de serviço'
                },
                'check_printed_count': {
                    'type': 'INTEGER',
                    'constraints': ['DEFAULT 0'],
                    'description': 'Número de vezes que a comanda foi impressa'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                },
                'updated_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de última atualização'
                }
            }
        }

    def _create_detail_lines_table(self):
        """Cria tabela de linhas de detalhe."""

        self.tables['guest_check_detail_lines'] = {
            'description': 'Linhas de detalhe das comandas',
            'business_purpose': 'Cada linha representa um item, desconto, taxa ou erro na comanda',
            'columns': {
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único da linha'
                },
                'guest_check_id': {
                    'type': 'UUID',
                    'constraints': ['NOT NULL', 'REFERENCES guest_checks(guest_check_id)'],
                    'description': 'Referência à comanda principal'
                },
                'revenue_center_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Centro de receita'
                },
                'detail_order_type_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Tipo de pedido do detalhe'
                },
                'detail_order_channel_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Canal do pedido do detalhe'
                },
                'line_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número sequencial da linha'
                },
                'detail_id': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'ID do detalhe'
                },
                'detail_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['NOT NULL'],
                    'description': 'Timestamp do detalhe em UTC'
                },
                'detail_local': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['NOT NULL'],
                    'description': 'Timestamp do detalhe local'
                },
                'last_update_utc': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Última atualização em UTC'
                },
                'business_date': {
                    'type': 'DATE',
                    'constraints': ['NOT NULL'],
                    'description': 'Data do negócio'
                },
                'workstation_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número da estação de trabalho'
                },
                'display_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': [],
                    'description': 'Total exibido'
                },
                'display_quantity': {
                    'type': 'DECIMAL(8,3)',
                    'constraints': [],
                    'description': 'Quantidade exibida'
                },
                'aggregate_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': [],
                    'description': 'Total agregado'
                },
                'aggregate_quantity': {
                    'type': 'DECIMAL(8,3)',
                    'constraints': [],
                    'description': 'Quantidade agregada'
                },
                'check_employee_id': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'ID do funcionário da comanda'
                },
                'check_employee_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número do funcionário da comanda'
                },
                'service_round_number': {
                    'type': 'INTEGER',
                    'constraints': ['DEFAULT 1'],
                    'description': 'Número da rodada de serviço'
                },
                'seat_number': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Número do assento/posição'
                },
                'line_type': {
                    'type': 'VARCHAR(50)',
                    'constraints': ['CHECK (line_type IN (\'menu_item\', \'discount\', \'service_charge\', \'tender_media\', \'error_code\'))'],
                    'description': 'Tipo da linha de detalhe'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                },
                'updated_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de última atualização'
                }
            }
        }

    def _create_menu_items_table(self):
        """Cria tabela de itens do menu."""

        self.tables['menu_items'] = {
            'description': 'Itens do cardápio/menu',
            'business_purpose': 'Catálogo de produtos disponíveis no restaurante',
            'columns': {
                'menu_item_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único do item'
                },
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['REFERENCES guest_check_detail_lines(guest_check_line_item_id)'],
                    'description': 'Referência à linha de detalhe'
                },
                'menu_item_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número do item no sistema'
                },
                'modification_flag': {
                    'type': 'BOOLEAN',
                    'constraints': ['DEFAULT FALSE'],
                    'description': 'Indica se o item foi modificado'
                },
                'included_tax': {
                    'type': 'DECIMAL(10,2)',
                    'constraints': ['DEFAULT 0.00'],
                    'description': 'Imposto incluído no preço'
                },
                'active_taxes': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'Impostos ativos para o item'
                },
                'price_level': {
                    'type': 'INTEGER',
                    'constraints': ['DEFAULT 1'],
                    'description': 'Nível de preço aplicado'
                },
                'item_name': {
                    'type': 'VARCHAR(255)',
                    'constraints': ['NOT NULL'],
                    'description': 'Nome do item'
                },
                'category_name': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'Nome da categoria'
                },
                'category_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'ID da categoria'
                },
                'family_group_name': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'Nome do grupo familiar'
                },
                'family_group_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': [],
                    'description': 'ID do grupo familiar'
                },
                'unit_price': {
                    'type': 'DECIMAL(10,2)',
                    'constraints': ['CHECK (unit_price >= 0)'],
                    'description': 'Preço unitário'
                },
                'display_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': [],
                    'description': 'Total exibido'
                },
                'display_quantity': {
                    'type': 'DECIMAL(8,3)',
                    'constraints': ['CHECK (display_quantity > 0)'],
                    'description': 'Quantidade exibida'
                },
                'aggregate_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': [],
                    'description': 'Total agregado'
                },
                'aggregate_quantity': {
                    'type': 'DECIMAL(8,3)',
                    'constraints': ['CHECK (aggregate_quantity > 0)'],
                    'description': 'Quantidade agregada'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                },
                'updated_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de última atualização'
                }
            }
        }

    def _create_taxes_table(self):
        """Cria tabela de impostos."""

        self.tables['guest_check_taxes'] = {
            'description': 'Impostos aplicados às comandas',
            'business_purpose': 'Registro de todos os impostos incidentes sobre as vendas',
            'columns': {
                'id': {
                    'type': 'SERIAL',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Chave primária sequencial'
                },
                'guest_check_id': {
                    'type': 'UUID',
                    'constraints': ['NOT NULL', 'REFERENCES guest_checks(guest_check_id)'],
                    'description': 'Referência à comanda'
                },
                'tax_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número do imposto'
                },
                'taxable_sales_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['CHECK (taxable_sales_total >= 0)'],
                    'description': 'Total de vendas tributáveis'
                },
                'tax_collected_total': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['CHECK (tax_collected_total >= 0)'],
                    'description': 'Total de imposto coletado'
                },
                'tax_rate': {
                    'type': 'DECIMAL(5,2)',
                    'constraints': ['CHECK (tax_rate >= 0 AND tax_rate <= 100)'],
                    'description': 'Taxa de imposto em percentual'
                },
                'tax_type': {
                    'type': 'INTEGER',
                    'constraints': [],
                    'description': 'Tipo de imposto'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                }
            }
        }

    def _create_discounts_table(self):
        """Cria tabela de descontos."""

        self.tables['discounts'] = {
            'description': 'Descontos aplicados',
            'business_purpose': 'Registro de todos os descontos concedidos',
            'columns': {
                'discount_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único do desconto'
                },
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['REFERENCES guest_check_detail_lines(guest_check_line_item_id)'],
                    'description': 'Referência à linha de detalhe'
                },
                'discount_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número do desconto'
                },
                'discount_name': {
                    'type': 'VARCHAR(255)',
                    'constraints': ['NOT NULL'],
                    'description': 'Nome do desconto'
                },
                'discount_type': {
                    'type': 'VARCHAR(50)',
                    'constraints': ['CHECK (discount_type IN (\'percentage\', \'fixed_amount\', \'buy_x_get_y\'))'],
                    'description': 'Tipo de desconto'
                },
                'discount_value': {
                    'type': 'DECIMAL(10,2)',
                    'constraints': ['CHECK (discount_value >= 0)'],
                    'description': 'Valor do desconto'
                },
                'discount_amount': {
                    'type': 'DECIMAL(10,2)',
                    'constraints': ['CHECK (discount_amount >= 0)'],
                    'description': 'Valor monetário do desconto'
                },
                'applied_to': {
                    'type': 'VARCHAR(50)',
                    'constraints': [],
                    'description': 'A que o desconto foi aplicado'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                }
            }
        }

    def _create_service_charges_table(self):
        """Cria tabela de taxas de serviço."""

        self.tables['service_charges'] = {
            'description': 'Taxas de serviço aplicadas',
            'business_purpose': 'Registro de taxas adicionais como gorjetas automáticas',
            'columns': {
                'service_charge_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único da taxa'
                },
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['REFERENCES guest_check_detail_lines(guest_check_line_item_id)'],
                    'description': 'Referência à linha de detalhe'
                },
                'service_charge_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número da taxa de serviço'
                },
                'service_charge_name': {
                    'type': 'VARCHAR(255)',
                    'constraints': ['NOT NULL'],
                    'description': 'Nome da taxa de serviço'
                },
                'service_charge_type': {
                    'type': 'VARCHAR(50)',
                    'constraints': [],
                    'description': 'Tipo da taxa de serviço'
                },
                'service_charge_amount': {
                    'type': 'DECIMAL(10,2)',
                    'constraints': ['CHECK (service_charge_amount >= 0)'],
                    'description': 'Valor da taxa de serviço'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                }
            }
        }

    def _create_tender_media_table(self):
        """Cria tabela de meios de pagamento."""

        self.tables['tender_media'] = {
            'description': 'Meios de pagamento utilizados',
            'business_purpose': 'Registro dos métodos de pagamento das comandas',
            'columns': {
                'tender_media_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único do meio de pagamento'
                },
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['REFERENCES guest_check_detail_lines(guest_check_line_item_id)'],
                    'description': 'Referência à linha de detalhe'
                },
                'tender_media_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número do meio de pagamento'
                },
                'tender_media_name': {
                    'type': 'VARCHAR(255)',
                    'constraints': ['NOT NULL'],
                    'description': 'Nome do meio de pagamento'
                },
                'tender_media_type': {
                    'type': 'VARCHAR(50)',
                    'constraints': ['CHECK (tender_media_type IN (\'cash\', \'credit_card\', \'debit_card\', \'pix\', \'voucher\'))'],
                    'description': 'Tipo do meio de pagamento'
                },
                'tender_amount': {
                    'type': 'DECIMAL(12,2)',
                    'constraints': ['CHECK (tender_amount > 0)'],
                    'description': 'Valor pago'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                }
            }
        }

    def _create_error_codes_table(self):
        """Cria tabela de códigos de erro."""

        self.tables['error_codes'] = {
            'description': 'Códigos de erro registrados',
            'business_purpose': 'Registro de erros ocorridos durante o processamento',
            'columns': {
                'error_code_id': {
                    'type': 'VARCHAR(100)',
                    'constraints': ['PRIMARY KEY'],
                    'description': 'Identificador único do erro'
                },
                'guest_check_line_item_id': {
                    'type': 'UUID',
                    'constraints': ['REFERENCES guest_check_detail_lines(guest_check_line_item_id)'],
                    'description': 'Referência à linha de detalhe'
                },
                'error_code_number': {
                    'type': 'INTEGER',
                    'constraints': ['NOT NULL'],
                    'description': 'Número do código de erro'
                },
                'error_description': {
                    'type': 'TEXT',
                    'constraints': [],
                    'description': 'Descrição do erro'
                },
                'error_severity': {
                    'type': 'VARCHAR(20)',
                    'constraints': ['CHECK (error_severity IN (\'low\', \'medium\', \'high\', \'critical\'))'],
                    'description': 'Severidade do erro'
                },
                'created_at': {
                    'type': 'TIMESTAMP WITH TIME ZONE',
                    'constraints': ['DEFAULT CURRENT_TIMESTAMP'],
                    'description': 'Data de criação do registro'
                }
            }
        }

    def _define_relationships(self):
        """Define relacionamentos entre tabelas."""

        self.relationships = [
            {
                'name': 'fk_detail_lines_guest_check',
                'parent_table': 'guest_checks',
                'parent_column': 'guest_check_id',
                'child_table': 'guest_check_detail_lines',
                'child_column': 'guest_check_id',
                'relationship_type': 'one_to_many',
                'on_delete': 'CASCADE',
                'description': 'Uma comanda pode ter múltiplas linhas de detalhe'
            },
            {
                'name': 'fk_menu_items_detail_line',
                'parent_table': 'guest_check_detail_lines',
                'parent_column': 'guest_check_line_item_id',
                'child_table': 'menu_items',
                'child_column': 'guest_check_line_item_id',
                'relationship_type': 'one_to_one',
                'on_delete': 'CASCADE',
                'description': 'Uma linha de detalhe pode ter um item do menu'
            },
            {
                'name': 'fk_taxes_guest_check',
                'parent_table': 'guest_checks',
                'parent_column': 'guest_check_id',
                'child_table': 'guest_check_taxes',
                'child_column': 'guest_check_id',
                'relationship_type': 'one_to_many',
                'on_delete': 'CASCADE',
                'description': 'Uma comanda pode ter múltiplos impostos'
            },
            {
                'name': 'fk_discounts_detail_line',
                'parent_table': 'guest_check_detail_lines',
                'parent_column': 'guest_check_line_item_id',
                'child_table': 'discounts',
                'child_column': 'guest_check_line_item_id',
                'relationship_type': 'one_to_one',
                'on_delete': 'CASCADE',
                'description': 'Uma linha de detalhe pode ter um desconto'
            },
            {
                'name': 'fk_service_charges_detail_line',
                'parent_table': 'guest_check_detail_lines',
                'parent_column': 'guest_check_line_item_id',
                'child_table': 'service_charges',
                'child_column': 'guest_check_line_item_id',
                'relationship_type': 'one_to_one',
                'on_delete': 'CASCADE',
                'description': 'Uma linha de detalhe pode ter uma taxa de serviço'
            },
            {
                'name': 'fk_tender_media_detail_line',
                'parent_table': 'guest_check_detail_lines',
                'parent_column': 'guest_check_line_item_id',
                'child_table': 'tender_media',
                'child_column': 'guest_check_line_item_id',
                'relationship_type': 'one_to_one',
                'on_delete': 'CASCADE',
                'description': 'Uma linha de detalhe pode ter um meio de pagamento'
            },
            {
                'name': 'fk_error_codes_detail_line',
                'parent_table': 'guest_check_detail_lines',
                'parent_column': 'guest_check_line_item_id',
                'child_table': 'error_codes',
                'child_column': 'guest_check_line_item_id',
                'relationship_type': 'one_to_one',
                'on_delete': 'CASCADE',
                'description': 'Uma linha de detalhe pode ter um código de erro'
            }
        ]

    def _create_indexes(self):
        """Define índices para otimização de performance."""

        self.indexes = [
            {
                'name': 'idx_guest_checks_business_date',
                'table': 'guest_checks',
                'columns': ['open_business_date'],
                'type': 'btree',
                'description': 'Índice para consultas por data de negócio'
            },
            {
                'name': 'idx_guest_checks_table_number',
                'table': 'guest_checks',
                'columns': ['table_number', 'open_business_date'],
                'type': 'btree',
                'description': 'Índice para consultas por mesa e data'
            },
            {
                'name': 'idx_detail_lines_guest_check_id',
                'table': 'guest_check_detail_lines',
                'columns': ['guest_check_id'],
                'type': 'btree',
                'description': 'Índice para join com tabela principal'
            },
            {
                'name': 'idx_detail_lines_business_date',
                'table': 'guest_check_detail_lines',
                'columns': ['business_date'],
                'type': 'btree',
                'description': 'Índice para consultas por data'
            },
            {
                'name': 'idx_menu_items_category',
                'table': 'menu_items',
                'columns': ['category_name'],
                'type': 'btree',
                'description': 'Índice para consultas por categoria'
            },
            {
                'name': 'idx_taxes_guest_check_id',
                'table': 'guest_check_taxes',
                'columns': ['guest_check_id'],
                'type': 'btree',
                'description': 'Índice para join com comandas'
            }
        ]

    def _define_constraints(self):
        """Define constraints de integridade."""

        self.constraints = [
            {
                'name': 'chk_guest_check_totals',
                'table': 'guest_checks',
                'type': 'check',
                'definition': 'check_total >= 0 AND subtotal >= 0',
                'description': 'Garante que totais sejam não-negativos'
            },
            {
                'name': 'chk_closed_flag_consistency',
                'table': 'guest_checks',
                'type': 'check',
                'definition': '(closed_flag = true AND closed_business_date IS NOT NULL) OR (closed_flag = false)',
                'description': 'Se fechado, deve ter data de fechamento'
            },
            {
                'name': 'chk_tax_rate_range',
                'table': 'guest_check_taxes',
                'type': 'check',
                'definition': 'tax_rate >= 0 AND tax_rate <= 100',
                'description': 'Taxa de imposto deve estar entre 0 e 100%'
            },
            {
                'name': 'chk_positive_amounts',
                'table': 'menu_items',
                'type': 'check',
                'definition': 'unit_price >= 0 AND display_quantity > 0',
                'description': 'Preços e quantidades devem ser positivos'
            }
        ]

    def _generate_complete_model(self) -> Dict[str, Any]:
        """Gera modelo completo com todas as informações."""

        return {
            'model_metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'description': 'Modelo relacional para sistema ERP de restaurante',
                'normalization_level': '3NF',
                'total_tables': len(self.tables)
            },
            'tables': self.tables,
            'relationships': self.relationships,
            'indexes': self.indexes,
            'constraints': self.constraints,
            'business_rules': self._define_business_rules(),
            'performance_considerations': self._define_performance_considerations(),
            'data_governance': self._define_data_governance()
        }

    def _define_business_rules(self) -> List[Dict[str, str]]:
        """Define regras de negócio implementadas."""

        return [
            {
                'rule': 'Integridade de Totais',
                'description': 'O total da comanda deve ser igual ao subtotal + impostos - descontos',
                'implementation': 'Triggers e constraints de validação'
            },
            {
                'rule': 'Sequencialidade de Linhas',
                'description': 'Linhas de detalhe devem ter numeração sequencial por comanda',
                'implementation': 'Constraint UNIQUE(guest_check_id, line_number)'
            },
            {
                'rule': 'Consistência Temporal',
                'description': 'Data de fechamento deve ser >= data de abertura',
                'implementation': 'Check constraint temporal'
            },
            {
                'rule': 'Validação de Status',
                'description': 'Comandas fechadas devem ter todos os campos obrigatórios preenchidos',
                'implementation': 'Trigger de validação no fechamento'
            }
        ]

    def _define_performance_considerations(self) -> List[Dict[str, str]]:
        """Define considerações de performance."""

        return [
            {
                'aspect': 'Particionamento',
                'recommendation': 'Particionar tabelas principais por data de negócio',
                'benefit': 'Melhora performance de consultas temporais'
            },
            {
                'aspect': 'Índices Compostos',
                'recommendation': 'Criar índices compostos para consultas frequentes',
                'benefit': 'Reduz tempo de resposta em relatórios'
            },
            {
                'aspect': 'Arquivamento',
                'recommendation': 'Implementar estratégia de arquivamento de dados antigos',
                'benefit': 'Mantém tabelas com tamanho gerenciável'
            },
            {
                'aspect': 'Materialização',
                'recommendation': 'Criar views materializadas para relatórios complexos',
                'benefit': 'Acelera consultas analíticas'
            }
        ]

    def _define_data_governance(self) -> Dict[str, Any]:
        """Define políticas de governança de dados."""

        return {
            'retention_policies': {
                'transactional_data': '7 anos (conforme legislação fiscal)',
                'audit_logs': '5 anos',
                'error_logs': '2 anos'
            },
            'backup_strategy': {
                'frequency': 'Diário para dados transacionais',
                'retention': '30 dias backup completo, 1 ano backup incremental',
                'testing': 'Teste de restore mensal'
            },
            'access_control': {
                'principle': 'Least privilege',
                'roles': ['read_only', 'operator', 'manager', 'admin'],
                'audit': 'Log de todos os acessos e modificações'
            },
            'data_quality': {
                'validation': 'Validação em tempo real via constraints',
                'monitoring': 'Alertas para anomalias nos dados',
                'correction': 'Processo formal para correção de dados'
            }
        }

    def generate_ddl_script(self, model: Dict[str, Any]) -> str:
        """Gera script DDL completo."""

        ddl_script = []

        # Header
        ddl_script.append(
            "-- =====================================================")
        ddl_script.append("-- SCRIPT DDL - SISTEMA ERP RESTAURANTE")
        ddl_script.append(
            f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        ddl_script.append(
            "-- =====================================================")
        ddl_script.append("")

        # Criar tabelas
        ddl_script.append("-- CRIAÇÃO DE TABELAS")
        ddl_script.append(
            "-- =====================================================")

        for table_name, table_info in model['tables'].items():
            ddl_script.append(f"\n-- Tabela: {table_name}")
            ddl_script.append(f"-- {table_info['description']}")
            ddl_script.append(f"CREATE TABLE {table_name} (")

            columns = []
            for col_name, col_info in table_info['columns'].items():
                col_def = f"    {col_name} {col_info['type']}"
                if col_info['constraints']:
                    col_def += " " + " ".join(col_info['constraints'])
                columns.append(col_def)

            ddl_script.append(",\n".join(columns))
            ddl_script.append(");")
            ddl_script.append("")

        # Criar índices
        ddl_script.append("\n-- CRIAÇÃO DE ÍNDICES")
        ddl_script.append(
            "-- =====================================================")

        for index in model['indexes']:
            columns_str = ", ".join(index['columns'])
            ddl_script.append(
                f"CREATE INDEX {index['name']} ON {index['table']} ({columns_str});")

        # Comentários
        ddl_script.append("\n-- COMENTÁRIOS NAS TABELAS E COLUNAS")
        ddl_script.append(
            "-- =====================================================")

        for table_name, table_info in model['tables'].items():
            ddl_script.append(
                f"COMMENT ON TABLE {table_name} IS '{table_info['description']}';")

            for col_name, col_info in table_info['columns'].items():
                ddl_script.append(
                    f"COMMENT ON COLUMN {table_name}.{col_name} IS '{col_info['description']}';")

        return "\n".join(ddl_script)


def main():
    """Função principal para executar a modelagem SQL."""

    logging.basicConfig(level=logging.INFO)

    modeler = SQLModeler()

    # Criar modelo relacional
    erp_file = os.path.join("dados", "ERP.json")

    if not os.path.exists(erp_file):
        logger.error(f"Arquivo não encontrado: {erp_file}")
        return

    try:
        model = modeler.create_relational_model(erp_file)

        # Salvar modelo
        os.makedirs("docs", exist_ok=True)
        os.makedirs("sql", exist_ok=True)

        model_file = os.path.join("docs", "relational_model.json")
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(model, f, indent=2, ensure_ascii=False, default=str)

        # Gerar script DDL
        ddl_script = modeler.generate_ddl_script(model)
        ddl_file = os.path.join("sql", "create_tables.sql")

        with open(ddl_file, 'w', encoding='utf-8') as f:
            f.write(ddl_script)

        logger.info(f"Modelo salvo em: {model_file}")
        logger.info(f"Script DDL salvo em: {ddl_file}")

        # Exibir resumo
        print("\n" + "="*60)
        print("MODELO RELACIONAL - ERP RESTAURANTE")
        print("="*60)

        print(f"\nTABELAS CRIADAS: {len(model['tables'])}")
        for table_name, table_info in model['tables'].items():
            print(f"   • {table_name.upper()}: {table_info['description']}")

        print(f"\nRELACIONAMENTOS: {len(model['relationships'])}")
        for rel in model['relationships'][:3]:
            print(f"   • {rel['parent_table']} → {rel['child_table']}")

        print(f"\nÍNDICES: {len(model['indexes'])}")
        print(f"CONSTRAINTS: {len(model['constraints'])}")

        print(f"\nArquivos gerados:")
        print(f"   • {model_file}")
        print(f"   • {ddl_file}")

    except Exception as e:
        logger.error(f"Erro na modelagem: {e}")
        raise


if __name__ == "__main__":
    main()
