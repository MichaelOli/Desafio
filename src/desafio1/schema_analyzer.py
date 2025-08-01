"""
Desafio 1 - Parte 1: Análise de Schema JSON
Analisa a estrutura do arquivo ERP.json e documenta o schema correspondente.
"""

import json
import logging
from typing import Dict, Any, List, Set
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Analisador de schema JSON para dados de ERP de restaurante."""

    def __init__(self):
        self.schema_info = {}
        self.field_types = {}
        self.nested_objects = {}
        self.arrays = {}

    def analyze_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analisa um arquivo JSON e extrai informações de schema.

        Args:
            file_path: Caminho para o arquivo JSON

        Returns:
            Dicionário com informações detalhadas do schema
        """
        logger.info(f"Analisando schema do arquivo: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Analisar estrutura principal
            self.schema_info = self._analyze_structure(data, "root")

            # Gerar documentação do schema
            documentation = self._generate_schema_documentation()

            logger.info("Análise de schema concluída com sucesso")
            return documentation

        except Exception as e:
            logger.error(f"Erro ao analisar schema: {e}")
            raise

    def _analyze_structure(self, obj: Any, path: str = "") -> Dict[str, Any]:
        """Analisa recursivamente a estrutura de um objeto JSON."""

        if isinstance(obj, dict):
            return self._analyze_object(obj, path)
        elif isinstance(obj, list):
            return self._analyze_array(obj, path)
        else:
            return self._analyze_primitive(obj, path)

    def _analyze_object(self, obj: Dict, path: str) -> Dict[str, Any]:
        """Analisa um objeto JSON."""

        structure = {
            "type": "object",
            "path": path,
            "properties": {},
            "required_fields": [],
            "optional_fields": []
        }

        for key, value in obj.items():
            field_path = f"{path}.{key}" if path else key
            field_info = self._analyze_structure(value, field_path)

            structure["properties"][key] = field_info

            # Determinar se o campo é obrigatório (simplificação)
            if value is not None and value != "":
                structure["required_fields"].append(key)
            else:
                structure["optional_fields"].append(key)

        return structure

    def _analyze_array(self, arr: List, path: str) -> Dict[str, Any]:
        """Analisa um array JSON."""

        structure = {
            "type": "array",
            "path": path,
            "length": len(arr),
            "item_types": set(),
            "sample_item": None
        }

        if arr:
            # Analisar primeiro item como exemplo
            structure["sample_item"] = self._analyze_structure(
                arr[0], f"{path}[0]")

            # Identificar tipos de itens
            for item in arr:
                if isinstance(item, dict):
                    structure["item_types"].add("object")
                elif isinstance(item, list):
                    structure["item_types"].add("array")
                else:
                    structure["item_types"].add(type(item).__name__)

        structure["item_types"] = list(structure["item_types"])
        return structure

    def _analyze_primitive(self, value: Any, path: str) -> Dict[str, Any]:
        """Analisa um valor primitivo."""

        structure = {
            "type": type(value).__name__,
            "path": path,
            "value": value,
            "python_type": type(value).__name__
        }

        # Detectar tipos especiais
        if isinstance(value, str):
            structure.update(self._analyze_string_type(value))
        elif isinstance(value, (int, float)):
            structure.update(self._analyze_numeric_type(value))

        return structure

    def _analyze_string_type(self, value: str) -> Dict[str, Any]:
        """Analisa tipos específicos de string."""

        analysis = {
            "length": len(value),
            "is_empty": len(value) == 0
        }

        # Detectar formatos especiais
        if self._is_uuid(value):
            analysis["format"] = "uuid"
            analysis["sql_type"] = "UUID"
        elif self._is_datetime(value):
            analysis["format"] = "datetime"
            analysis["sql_type"] = "TIMESTAMP"
        elif self._is_date(value):
            analysis["format"] = "date"
            analysis["sql_type"] = "DATE"
        elif value.replace('.', '').replace('-', '').isdigit():
            analysis["format"] = "numeric_string"
            analysis["sql_type"] = "VARCHAR"
        else:
            analysis["format"] = "text"
            analysis["sql_type"] = f"VARCHAR({max(255, len(value) * 2)})"

        return analysis

    def _analyze_numeric_type(self, value) -> Dict[str, Any]:
        """Analisa tipos numéricos."""

        analysis = {}

        if isinstance(value, int):
            analysis["sql_type"] = "INTEGER"
            if value >= 0:
                analysis["constraint"] = "CHECK (value >= 0)"
        elif isinstance(value, float):
            # Determinar precisão necessária
            decimal_places = len(str(value).split(
                '.')[-1]) if '.' in str(value) else 0
            analysis["sql_type"] = f"DECIMAL(10, {max(2, decimal_places)})"

        return analysis

    def _is_uuid(self, value: str) -> bool:
        """Verifica se uma string é um UUID."""
        try:
            import uuid
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False

    def _is_datetime(self, value: str) -> bool:
        """Verifica se uma string é um datetime ISO."""
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return 'T' in value
        except (ValueError, AttributeError):
            return False

    def _is_date(self, value: str) -> bool:
        """Verifica se uma string é uma data."""
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except (ValueError, AttributeError):
            return False

    def _generate_schema_documentation(self) -> Dict[str, Any]:
        """Gera documentação completa do schema."""

        documentation = {
            "analysis_timestamp": datetime.now().isoformat(),
            "schema_version": "1.0",
            "description": "Schema do sistema ERP de restaurante - Guest Check",
            "root_structure": self.schema_info,
            "business_entities": self._identify_business_entities(),
            "relationships": self._identify_relationships(),
            "data_quality_rules": self._suggest_data_quality_rules(),
            "sql_mapping": self._generate_sql_mapping()
        }

        return documentation

    def _identify_business_entities(self) -> Dict[str, Any]:
        """Identifica entidades de negócio no schema."""

        entities = {
            "guest_check": {
                "description": "Comanda/pedido do cliente",
                "primary_key": "guestCheckId",
                "business_meaning": "Representa um pedido completo de um cliente",
                "key_fields": ["guestCheckId", "chkNum", "opnBusDt", "chkTtl"]
            },
            "detail_line": {
                "description": "Item individual da comanda",
                "primary_key": "guestCheckLineItemId",
                "business_meaning": "Cada linha representa um item, desconto ou taxa",
                "key_fields": ["guestCheckLineItemId", "lineNum", "dtlId"]
            },
            "menu_item": {
                "description": "Item do cardápio",
                "primary_key": "miNum",
                "business_meaning": "Produto/prato disponível no restaurante",
                "key_fields": ["miNum", "itemName", "categoryName", "unitPrice"]
            },
            "tax": {
                "description": "Imposto aplicado",
                "primary_key": "taxNum",
                "business_meaning": "Tributos incidentes sobre a venda",
                "key_fields": ["taxNum", "taxRate", "taxCollTtl"]
            },
            "discount": {
                "description": "Desconto aplicado",
                "primary_key": "dscNum",
                "business_meaning": "Reduções no valor do pedido",
                "key_fields": ["dscNum", "dscName", "dscValue", "dscAmount"]
            }
        }

        return entities

    def _identify_relationships(self) -> List[Dict[str, str]]:
        """Identifica relacionamentos entre entidades."""

        relationships = [
            {
                "parent": "guest_check",
                "child": "detail_line",
                "type": "one_to_many",
                "foreign_key": "guestCheckId",
                "description": "Uma comanda pode ter múltiplos itens"
            },
            {
                "parent": "guest_check",
                "child": "tax",
                "type": "one_to_many",
                "foreign_key": "guestCheckId",
                "description": "Uma comanda pode ter múltiplos impostos"
            },
            {
                "parent": "detail_line",
                "child": "menu_item",
                "type": "many_to_one",
                "foreign_key": "miNum",
                "description": "Múltiplas linhas podem referenciar o mesmo item do menu"
            },
            {
                "parent": "detail_line",
                "child": "discount",
                "type": "one_to_one",
                "foreign_key": "guestCheckLineItemId",
                "description": "Uma linha pode ter um desconto associado"
            }
        ]

        return relationships

    def _suggest_data_quality_rules(self) -> List[Dict[str, str]]:
        """Sugere regras de qualidade de dados."""

        rules = [
            {
                "field": "guestCheckId",
                "rule": "NOT NULL AND UUID format",
                "description": "ID único obrigatório para cada comanda"
            },
            {
                "field": "chkTtl",
                "rule": "chkTtl >= 0 AND chkTtl = subTtl + taxes - discounts",
                "description": "Total deve ser positivo e consistente com cálculos"
            },
            {
                "field": "opnBusDt",
                "rule": "Valid date format AND <= current_date",
                "description": "Data de abertura deve ser válida e não futura"
            },
            {
                "field": "clsdFlag",
                "rule": "Boolean AND (clsdFlag = true IMPLIES clsdBusDt IS NOT NULL)",
                "description": "Se fechado, deve ter data de fechamento"
            },
            {
                "field": "unitPrice",
                "rule": "unitPrice > 0",
                "description": "Preço unitário deve ser positivo"
            }
        ]

        return rules

    def _generate_sql_mapping(self) -> Dict[str, str]:
        """Gera mapeamento para tipos SQL."""

        mapping = {
            "guestCheckId": "UUID PRIMARY KEY",
            "chkNum": "INTEGER NOT NULL",
            "opnBusDt": "DATE NOT NULL",
            "opnUTC": "TIMESTAMP WITH TIME ZONE",
            "chkTtl": "DECIMAL(10,2) CHECK (chkTtl >= 0)",
            "clsdFlag": "BOOLEAN DEFAULT FALSE",
            "gstCnt": "INTEGER CHECK (gstCnt >= 0)",
            "itemName": "VARCHAR(255) NOT NULL",
            "unitPrice": "DECIMAL(10,2) CHECK (unitPrice > 0)",
            "taxRate": "DECIMAL(5,2) CHECK (taxRate >= 0 AND taxRate <= 100)"
        }

        return mapping


def main():
    """Função principal para executar a análise de schema."""

    logging.basicConfig(level=logging.INFO)

    analyzer = SchemaAnalyzer()

    # Analisar o arquivo ERP.json
    erp_file = os.path.join("dados", "ERP.json")

    if not os.path.exists(erp_file):
        logger.error(f"Arquivo não encontrado: {erp_file}")
        return

    try:
        documentation = analyzer.analyze_json_file(erp_file)

        # Salvar documentação
        output_file = os.path.join("docs", "schema_analysis.json")
        os.makedirs("docs", exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documentation, f, indent=2,
                      ensure_ascii=False, default=str)

        logger.info(f"Documentação salva em: {output_file}")

        # Exibir resumo
        print("\n" + "="*60)
        print("ANÁLISE DE SCHEMA - ERP RESTAURANTE")
        print("="*60)

        print(f"\nENTIDADES IDENTIFICADAS:")
        for entity, info in documentation["business_entities"].items():
            print(f"   • {entity.upper()}: {info['description']}")

        print(f"\nRELACIONAMENTOS:")
        for rel in documentation["relationships"]:
            print(f"   • {rel['parent']} → {rel['child']} ({rel['type']})")

        print(f"\nREGRAS DE QUALIDADE:")
        for rule in documentation["data_quality_rules"][:3]:
            print(f"   • {rule['field']}: {rule['rule']}")

        print(f"\nDocumentação completa salva em: {output_file}")

    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        raise


if __name__ == "__main__":
    main()
