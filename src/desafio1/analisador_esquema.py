"""
Desafio 1 - Parte 1: Análise de Esquema JSON
Analisa a estrutura do arquivo ERP.json e documenta o esquema correspondente.
"""

import json
import logging
from typing import Dict, Any, List, Set
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class AnalisadorEsquema:
    """Analisador de esquema JSON para dados de ERP de restaurante."""

    def __init__(self):
        self.informacoes_esquema = {}
        self.tipos_campos = {}
        self.objetos_aninhados = {}
        self.arrays = {}

    def analisar_arquivo_json(self, caminho_arquivo: str) -> Dict[str, Any]:
        """
        Analisa um arquivo JSON e extrai informações de esquema.

        Args:
            caminho_arquivo: Caminho para o arquivo JSON

        Returns:
            Dicionário com informações detalhadas do esquema
        """
        logger.info(f"Analisando esquema do arquivo: {caminho_arquivo}")

        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)

            # Analisar estrutura principal
            self.informacoes_esquema = self._analisar_estrutura(dados, "raiz")

            # Gerar documentação do esquema
            documentacao = self._gerar_documentacao_esquema()

            logger.info("Análise de esquema concluída com sucesso")
            return documentacao

        except Exception as erro:
            logger.error(f"Erro ao analisar esquema: {erro}")
            raise

    def _analisar_estrutura(self, objeto: Any, caminho: str = "") -> Dict[str, Any]:
        """Analisa recursivamente a estrutura de um objeto JSON."""

        if isinstance(objeto, dict):
            return self._analisar_objeto(objeto, caminho)
        elif isinstance(objeto, list):
            return self._analisar_array(objeto, caminho)
        else:
            return self._analisar_primitivo(objeto, caminho)

    def _analisar_objeto(self, objeto: Dict, caminho: str) -> Dict[str, Any]:
        """Analisa um objeto JSON."""

        estrutura = {
            "tipo": "objeto",
            "caminho": caminho,
            "propriedades": {},
            "campos_obrigatorios": [],
            "campos_opcionais": []
        }

        for chave, valor in objeto.items():
            caminho_campo = f"{caminho}.{chave}" if caminho else chave
            informacoes_campo = self._analisar_estrutura(valor, caminho_campo)

            estrutura["propriedades"][chave] = informacoes_campo

            # Determinar se o campo é obrigatório (simplificação)
            if valor is not None and valor != "":
                estrutura["campos_obrigatorios"].append(chave)
            else:
                estrutura["campos_opcionais"].append(chave)

        return estrutura

    def _analisar_array(self, array: List, caminho: str) -> Dict[str, Any]:
        """Analisa um array JSON."""

        estrutura = {
            "tipo": "array",
            "caminho": caminho,
            "tamanho": len(array),
            "tipos_itens": set(),
            "item_exemplo": None
        }

        if array:
            # Analisar primeiro item como exemplo
            estrutura["item_exemplo"] = self._analisar_estrutura(
                array[0], f"{caminho}[0]")

            # Identificar tipos de itens
            for item in array:
                if isinstance(item, dict):
                    estrutura["tipos_itens"].add("objeto")
                elif isinstance(item, list):
                    estrutura["tipos_itens"].add("array")
                else:
                    estrutura["tipos_itens"].add(type(item).__name__)

        estrutura["tipos_itens"] = list(estrutura["tipos_itens"])
        return estrutura

    def _analisar_primitivo(self, valor: Any, caminho: str) -> Dict[str, Any]:
        """Analisa um valor primitivo."""

        estrutura = {
            "tipo": type(valor).__name__,
            "caminho": caminho,
            "valor": valor,
            "tipo_python": type(valor).__name__
        }

        # Detectar tipos especiais
        if isinstance(valor, str):
            estrutura.update(self._analisar_tipo_string(valor))
        elif isinstance(valor, (int, float)):
            estrutura.update(self._analisar_tipo_numerico(valor))

        return estrutura

    def _analisar_tipo_string(self, valor: str) -> Dict[str, Any]:
        """Analisa tipos específicos de string."""

        analise = {
            "tamanho": len(valor),
            "esta_vazio": len(valor) == 0
        }

        # Detectar formatos especiais
        if self._eh_uuid(valor):
            analise["formato"] = "uuid"
            analise["tipo_sql"] = "UUID"
        elif self._eh_datetime(valor):
            analise["formato"] = "datetime"
            analise["tipo_sql"] = "TIMESTAMP"
        elif self._eh_data(valor):
            analise["formato"] = "data"
            analise["tipo_sql"] = "DATE"
        elif valor.replace('.', '').replace('-', '').isdigit():
            analise["formato"] = "string_numerica"
            analise["tipo_sql"] = "VARCHAR"
        else:
            analise["formato"] = "texto"
            analise["tipo_sql"] = f"VARCHAR({max(255, len(valor) * 2)})"

        return analise

    def _analisar_tipo_numerico(self, valor) -> Dict[str, Any]:
        """Analisa tipos numéricos."""

        analise = {}

        if isinstance(valor, int):
            analise["tipo_sql"] = "INTEGER"
            if valor >= 0:
                analise["restricao"] = "CHECK (valor >= 0)"
        elif isinstance(valor, float):
            # Determinar precisão necessária
            casas_decimais = len(str(valor).split(
                '.')[-1]) if '.' in str(valor) else 0
            analise["tipo_sql"] = f"DECIMAL(10, {max(2, casas_decimais)})"

        return analise

    def _eh_uuid(self, valor: str) -> bool:
        """Verifica se uma string é um UUID."""
        try:
            import uuid
            uuid.UUID(valor)
            return True
        except (ValueError, AttributeError):
            return False

    def _eh_datetime(self, valor: str) -> bool:
        """Verifica se uma string é um datetime ISO."""
        try:
            datetime.fromisoformat(valor.replace('Z', '+00:00'))
            return 'T' in valor
        except (ValueError, AttributeError):
            return False

    def _eh_data(self, valor: str) -> bool:
        """Verifica se uma string é uma data."""
        try:
            datetime.strptime(valor, '%Y-%m-%d')
            return True
        except (ValueError, AttributeError):
            return False

    def _gerar_documentacao_esquema(self) -> Dict[str, Any]:
        """Gera documentação completa do esquema."""

        documentacao = {
            "timestamp_analise": datetime.now().isoformat(),
            "versao_esquema": "1.0",
            "descricao": "Esquema do sistema ERP de restaurante - Guest Check",
            "estrutura_raiz": self.informacoes_esquema,
            "entidades_negocio": self._identificar_entidades_negocio(),
            "relacionamentos": self._identificar_relacionamentos(),
            "regras_qualidade_dados": self._sugerir_regras_qualidade_dados(),
            "mapeamento_sql": self._gerar_mapeamento_sql()
        }

        return documentacao

    def _identificar_entidades_negocio(self) -> Dict[str, Any]:
        """Identifica entidades de negócio no esquema."""

        entidades = {
            "comanda_cliente": {
                "descricao": "Comanda/pedido do cliente",
                "chave_primaria": "guestCheckId",
                "significado_negocio": "Representa um pedido completo de um cliente",
                "campos_chave": ["guestCheckId", "chkNum", "opnBusDt", "chkTtl"]
            },
            "linha_detalhe": {
                "descricao": "Item individual da comanda",
                "chave_primaria": "guestCheckLineItemId",
                "significado_negocio": "Cada linha representa um item, desconto ou taxa",
                "campos_chave": ["guestCheckLineItemId", "lineNum", "dtlId"]
            },
            "item_menu": {
                "descricao": "Item do cardápio",
                "chave_primaria": "miNum",
                "significado_negocio": "Produto/prato disponível no restaurante",
                "campos_chave": ["miNum", "itemName", "categoryName", "unitPrice"]
            },
            "imposto": {
                "descricao": "Imposto aplicado",
                "chave_primaria": "taxNum",
                "significado_negocio": "Tributos incidentes sobre a venda",
                "campos_chave": ["taxNum", "taxRate", "taxCollTtl"]
            },
            "desconto": {
                "descricao": "Desconto aplicado",
                "chave_primaria": "dscNum",
                "significado_negocio": "Reduções no valor do pedido",
                "campos_chave": ["dscNum", "dscName", "dscValue", "dscAmount"]
            }
        }

        return entidades

    def _identificar_relacionamentos(self) -> List[Dict[str, str]]:
        """Identifica relacionamentos entre entidades."""

        relacionamentos = [
            {
                "pai": "comanda_cliente",
                "filho": "linha_detalhe",
                "tipo": "um_para_muitos",
                "chave_estrangeira": "guestCheckId",
                "descricao": "Uma comanda pode ter múltiplos itens"
            },
            {
                "pai": "comanda_cliente",
                "filho": "imposto",
                "tipo": "um_para_muitos",
                "chave_estrangeira": "guestCheckId",
                "descricao": "Uma comanda pode ter múltiplos impostos"
            },
            {
                "pai": "linha_detalhe",
                "filho": "item_menu",
                "tipo": "muitos_para_um",
                "chave_estrangeira": "miNum",
                "descricao": "Múltiplas linhas podem referenciar o mesmo item do menu"
            },
            {
                "pai": "linha_detalhe",
                "filho": "desconto",
                "tipo": "um_para_um",
                "chave_estrangeira": "guestCheckLineItemId",
                "descricao": "Uma linha pode ter um desconto associado"
            }
        ]

        return relacionamentos

    def _sugerir_regras_qualidade_dados(self) -> List[Dict[str, str]]:
        """Sugere regras de qualidade de dados."""

        regras = [
            {
                "campo": "guestCheckId",
                "regra": "NOT NULL AND formato UUID",
                "descricao": "ID único obrigatório para cada comanda"
            },
            {
                "campo": "chkTtl",
                "regra": "chkTtl >= 0 AND chkTtl = subTtl + impostos - descontos",
                "descricao": "Total deve ser positivo e consistente com cálculos"
            },
            {
                "campo": "opnBusDt",
                "regra": "Formato de data válido AND <= data_atual",
                "descricao": "Data de abertura deve ser válida e não futura"
            },
            {
                "campo": "clsdFlag",
                "regra": "Boolean AND (clsdFlag = true IMPLIES clsdBusDt IS NOT NULL)",
                "descricao": "Se fechado, deve ter data de fechamento"
            },
            {
                "campo": "unitPrice",
                "regra": "unitPrice > 0",
                "descricao": "Preço unitário deve ser positivo"
            }
        ]

        return regras

    def _gerar_mapeamento_sql(self) -> Dict[str, str]:
        """Gera mapeamento para tipos SQL."""

        mapeamento = {
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

        return mapeamento


def main():
    """Função principal para executar a análise de esquema."""

    logging.basicConfig(level=logging.INFO)

    analisador = AnalisadorEsquema()

    # Analisar o arquivo ERP.json
    arquivo_erp = os.path.join("dados", "ERP.json")

    if not os.path.exists(arquivo_erp):
        logger.error(f"Arquivo não encontrado: {arquivo_erp}")
        return

    try:
        documentacao = analisador.analisar_arquivo_json(arquivo_erp)

        # Salvar documentação
        arquivo_saida = os.path.join("docs", "analise_esquema.json")
        os.makedirs("docs", exist_ok=True)

        with open(arquivo_saida, 'w', encoding='utf-8') as arquivo:
            json.dump(documentacao, arquivo, indent=2,
                      ensure_ascii=False, default=str)

        logger.info(f"Documentação salva em: {arquivo_saida}")

        # Exibir resumo
        print("\n" + "="*60)
        print("ANÁLISE DE ESQUEMA - ERP RESTAURANTE")
        print("="*60)

        print(f"\nENTIDADES IDENTIFICADAS:")
        for entidade, info in documentacao["entidades_negocio"].items():
            print(f"   • {entidade.upper()}: {info['descricao']}")

        print(f"\nRELACIONAMENTOS:")
        for rel in documentacao["relacionamentos"]:
            print(f"   • {rel['pai']} → {rel['filho']} ({rel['tipo']})")

        print(f"\nREGRAS DE QUALIDADE:")
        for regra in documentacao["regras_qualidade_dados"][:3]:
            print(f"   • {regra['campo']}: {regra['regra']}")

        print(f"\nDocumentação completa salva em: {arquivo_saida}")

    except Exception as erro:
        logger.error(f"Erro na análise: {erro}")
        raise


if __name__ == "__main__":
    main()
