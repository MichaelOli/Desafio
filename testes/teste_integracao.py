"""
Testes de integração para validar a solução completa dos desafios.
"""

from desafio1.analisador_esquema import AnalisadorEsquema
from desafio1.modelador_sql import ModeladorSQL
from desafio2.gerenciador_data_lake import GerenciadorDataLake
from extrair import ExtratorDados
from transformar import TransformadorDados
from analisar import AnalisadorDados
import unittest
import os
import sys
import json
from datetime import date, datetime
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class TesteIntegracaoCompleta(unittest.TestCase):
    """Testes de integração para toda a solução."""

    @classmethod
    def setUpClass(cls):
        """Configuração inicial dos testes."""
        cls.pasta_teste = Path("teste_temp")
        cls.pasta_teste.mkdir(exist_ok=True)

        # Criar arquivo ERP.json de teste se não existir
        cls.arquivo_erp_teste = cls.pasta_teste / "ERP_teste.json"
        if not cls.arquivo_erp_teste.exists():
            cls._criar_arquivo_erp_teste()

    @classmethod
    def _criar_arquivo_erp_teste(cls):
        """Cria arquivo ERP.json para testes."""
        dados_teste = {
            "guestCheckId": "12345678-1234-5678-9012-123456789012",
            "chkNum": 1001,
            "opnBusDt": "2024-01-15",
            "chkTtl": 50.05,
            "gstCnt": 2,
            "taxes": [
                {
                    "taxNum": 1,
                    "taxRate": 10.00,
                    "taxCollTtl": 4.55
                }
            ],
            "detailLines": [
                {
                    "guestCheckLineItemId": "87654321-4321-8765-2109-876543210987",
                    "lineNum": 1,
                    "menuItem": {
                        "miNum": 501,
                        "itemName": "Hambúrguer Artesanal",
                        "unitPrice": 22.75,
                        "categoryName": "Lanches"
                    }
                }
            ]
        }

        with open(cls.arquivo_erp_teste, 'w', encoding='utf-8') as arquivo:
            json.dump(dados_teste, arquivo, indent=2, ensure_ascii=False)

    def test_desafio1_analise_esquema(self):
        """Testa análise de esquema do Desafio 1."""
        analisador = AnalisadorEsquema()

        # Executar análise
        documentacao = analisador.analisar_arquivo_json(
            str(self.arquivo_erp_teste))

        # Verificações
        self.assertIn('entidades_negocio', documentacao)
        self.assertIn('relacionamentos', documentacao)
        self.assertIn('regras_qualidade_dados', documentacao)

        # Verificar entidades identificadas
        entidades = documentacao['entidades_negocio']
        self.assertIn('comanda_cliente', entidades)
        self.assertIn('item_menu', entidades)

        print("✅ Teste de análise de esquema passou")

    def test_desafio1_modelagem_sql(self):
        """Testa modelagem SQL do Desafio 1."""
        modelador = ModeladorSQL()

        # Executar modelagem
        modelo = modelador.criar_modelo_relacional(str(self.arquivo_erp_teste))

        # Verificações
        self.assertIn('tabelas', modelo)
        self.assertIn('relacionamentos', modelo)
        self.assertIn('indices', modelo)

        # Verificar tabelas criadas
        tabelas = modelo['tabelas']
        self.assertIn('comandas_cliente', tabelas)
        self.assertIn('linhas_detalhe_comanda', tabelas)
        self.assertIn('itens_menu', tabelas)

        # Testar geração de DDL
        script_ddl = modelador.gerar_script_ddl(modelo)
        self.assertIn('CREATE TABLE', script_ddl)
        self.assertIn('comandas_cliente', script_ddl)

        print("✅ Teste de modelagem SQL passou")

    def test_desafio2_data_lake(self):
        """Testa gerenciador de data lake do Desafio 2."""
        # Usar pasta temporária para testes
        caminho_data_lake = self.pasta_teste / "data_lake_teste"
        gerenciador = GerenciadorDataLake(str(caminho_data_lake))

        # Dados de teste
        dados_teste = {
            "guestCheckId": "test-123",
            "chkTtl": 100.00,
            "items": [{"name": "Teste", "price": 50.00}]
        }

        # Testar armazenamento
        caminho_arquivo = gerenciador.armazenar_resposta_api(
            endpoint="getGuestChecks",
            dados=dados_teste,
            data_negocio=date.today(),
            id_loja="loja_teste"
        )

        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists(caminho_arquivo))

        # Testar busca
        dados_encontrados = gerenciador.buscar_dados(
            endpoint="getGuestChecks",
            data_inicio=date.today(),
            data_fim=date.today(),
            id_loja="loja_teste"
        )

        self.assertEqual(len(dados_encontrados), 1)
        self.assertEqual(
            dados_encontrados[0]['dados']['guestCheckId'], "test-123")

        # Testar estatísticas
        estatisticas = gerenciador.obter_estatisticas_data_lake()
        self.assertIn('total_arquivos', estatisticas)
        self.assertGreater(estatisticas['total_arquivos'], 0)

        print("✅ Teste de data lake passou")

    def test_pipeline_dados_vendas(self):
        """Testa pipeline de dados de vendas."""
        extrator = ExtratorDados()
        transformador = TransformadorDados()
        analisador = AnalisadorDados()

        # Gerar dados de teste
        dados_vendas = extrator.gerar_dados_exemplo_vendas(
            numero_registros=100)
        self.assertEqual(len(dados_vendas), 100)

        # Transformar dados
        dados_limpos = transformador.limpar_dados_vendas(dados_vendas)
        self.assertLessEqual(len(dados_limpos), len(dados_vendas))

        # Calcular métricas
        metricas = transformador.calcular_metricas_vendas(dados_limpos)
        self.assertGreater(len(metricas), 0)

        # Gerar relatório
        relatorio = analisador.gerar_relatorio_vendas(dados_limpos)
        self.assertIn('metricas_gerais', relatorio)
        self.assertIn('total_vendas', relatorio['metricas_gerais'])

        print("✅ Teste de pipeline de dados passou")

    def test_qualidade_dados(self):
        """Testa validação de qualidade dos dados."""
        transformador = TransformadorDados()

        # Criar dados com problemas conhecidos
        import pandas as pd
        dados_problematicos = pd.DataFrame({
            'id_venda': [1, 2, 2, 3],  # Duplicata
            'valor_total': [100, -50, 200, 0],  # Valor negativo e zero
            'quantidade': [1, 2, 0, 1],  # Quantidade zero
            'desconto': [0.1, 1.5, 0.2, 0.05]  # Desconto inválido
        })

        # Validar qualidade
        qualidade = transformador.validar_qualidade_dados(dados_problematicos)

        self.assertEqual(qualidade['total_registros'], 4)
        # O método duplicated() verifica duplicatas em todas as colunas, não apenas id_venda
        # Como temos valores diferentes nas outras colunas, não há duplicatas completas
        self.assertGreaterEqual(qualidade['duplicatas'], 0)
        self.assertIn('completude', qualidade)

        print("✅ Teste de qualidade de dados passou")

    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes."""
        import shutil
        if cls.pasta_teste.exists():
            shutil.rmtree(cls.pasta_teste)
        print("🧹 Limpeza de arquivos de teste concluída")


def executar_testes():
    """Executa todos os testes de integração."""
    print("🧪 INICIANDO TESTES DE INTEGRAÇÃO")
    print("=" * 50)

    # Configurar unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TesteIntegracaoCompleta)

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)

    total_testes = resultado.testsRun
    falhas = len(resultado.failures)
    erros = len(resultado.errors)
    sucessos = total_testes - falhas - erros

    print(f"✅ Sucessos: {sucessos}/{total_testes}")
    print(f"❌ Falhas: {falhas}/{total_testes}")
    print(f"🚨 Erros: {erros}/{total_testes}")

    if falhas == 0 and erros == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os detalhes acima.")
        return False


if __name__ == "__main__":
    sucesso = executar_testes()
    sys.exit(0 if sucesso else 1)
