from src.analisar import AnalisadorDados
from src.transformar import TransformadorDados
from src.extrair import ExtratorDados
from desafio2.gerenciador_data_lake import GerenciadorDataLake
from desafio1.modelador_sql import ModeladorSQL
from desafio1.analisador_esquema import AnalisadorEsquema
import os
import sys
import logging
from datetime import datetime, date

# Adicionar diretório src ao PYTHONPATH para permitir imports dos módulos
# Necessário porque os módulos estão organizados em subpastas dentro de src/
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


# Configurar sistema de logging para rastreamento de execução e debugging
# Utiliza tanto arquivo quanto console para facilitar monitoramento
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),  # Log persistente em arquivo
        logging.StreamHandler()  # Log em tempo real no console
    ]
)

logger = logging.getLogger(__name__)


def executar_desafio_1():
    """
    Executa o Desafio 1: Análise e Modelagem de Dados JSON.

    Processo:
    1. Analisa estrutura do arquivo JSON ERP
    2. Identifica entidades de negócio e relacionamentos
    3. Cria modelo relacional normalizado
    4. Gera script DDL para criação das tabelas

    Returns:
        bool: True se executado com sucesso, False caso contrário
    """

    logger.info("INICIANDO DESAFIO 1: ANÁLISE E MODELAGEM JSON")
    logger.info("=" * 60)

    try:
        # Verificar existência do arquivo de entrada antes de processar
        arquivo_erp = os.path.join("dados", "ERP.json")
        if not os.path.exists(arquivo_erp):
            logger.error(f"Arquivo ERP.json não encontrado em: {arquivo_erp}")
            return False

        # ETAPA 1: Análise de Esquema JSON
        # Analisa estrutura hierárquica e identifica padrões de dados
        logger.info("Executando análise de esquema JSON...")
        analisador_esquema = AnalisadorEsquema()
        documentacao_esquema = analisador_esquema.analisar_arquivo_json(
            arquivo_erp)

        # Salvar documentação do esquema para auditoria e referência
        os.makedirs("docs", exist_ok=True)
        arquivo_esquema = os.path.join("docs", "analise_esquema.json")

        import json
        with open(arquivo_esquema, 'w', encoding='utf-8') as arquivo:
            json.dump(documentacao_esquema, arquivo, indent=2,
                      ensure_ascii=False, default=str)

        logger.info(f"Análise de esquema salva em: {arquivo_esquema}")

        # ETAPA 2: Modelagem SQL Relacional
        # Converte estrutura JSON em modelo relacional normalizado
        logger.info("Executando modelagem SQL...")
        modelador_sql = ModeladorSQL()
        modelo_relacional = modelador_sql.criar_modelo_relacional(arquivo_erp)

        # Salvar modelo relacional para documentação técnica
        arquivo_modelo = os.path.join("docs", "modelo_relacional.json")
        with open(arquivo_modelo, 'w', encoding='utf-8') as arquivo:
            json.dump(modelo_relacional, arquivo, indent=2,
                      ensure_ascii=False, default=str)

        # Gerar script DDL para implementação em banco de dados
        os.makedirs("sql", exist_ok=True)
        script_ddl = modelador_sql.gerar_script_ddl(modelo_relacional)
        arquivo_ddl = os.path.join("sql", "criar_tabelas.sql")

        with open(arquivo_ddl, 'w', encoding='utf-8') as arquivo:
            arquivo.write(script_ddl)

        logger.info(f"Modelo relacional salvo em: {arquivo_modelo}")
        logger.info(f"Script DDL salvo em: {arquivo_ddl}")

        # Exibir resumo executivo dos resultados
        print("\n" + "="*60)
        print("RESUMO DESAFIO 1 - ANÁLISE E MODELAGEM JSON")
        print("="*60)

        print(f"\nENTIDADES IDENTIFICADAS:")
        for entidade, info in documentacao_esquema["entidades_negocio"].items():
            print(f"   - {entidade.upper()}: {info['descricao']}")

        print(f"\nTABELAS CRIADAS: {len(modelo_relacional['tabelas'])}")
        for nome_tabela in list(modelo_relacional['tabelas'].keys())[:5]:
            print(f"   - {nome_tabela}")
        if len(modelo_relacional['tabelas']) > 5:
            print(
                f"   - ... e mais {len(modelo_relacional['tabelas']) - 5} tabelas")

        print(f"\nARQUIVOS GERADOS:")
        print(f"   - {arquivo_esquema}")
        print(f"   - {arquivo_modelo}")
        print(f"   - {arquivo_ddl}")

        return True

    except Exception as erro:
        logger.error(f"Erro no Desafio 1: {erro}")
        return False


def executar_desafio_2():
    """
    Executa o Desafio 2: Data Lake e Pipeline de APIs.

    Processo:
    1. Cria estrutura do data lake seguindo arquitetura Medallion
    2. Simula ingestão de dados de múltiplas APIs
    3. Implementa sistema de particionamento e metadados
    4. Demonstra funcionalidades de busca e estatísticas

    Returns:
        bool: True se executado com sucesso, False caso contrário
    """

    logger.info("INICIANDO DESAFIO 2: DATA LAKE E PIPELINE DE APIS")
    logger.info("=" * 60)

    try:
        # Inicializar gerenciador do data lake com estrutura Medallion
        logger.info("Criando estrutura do data lake...")
        gerenciador_data_lake = GerenciadorDataLake()

        # Dados simulados de diferentes endpoints de API para demonstração
        # Representa dados reais que seriam recebidos de sistemas POS
        endpoints_dados = {
            'bilgetFiscalInvoice': {
                'invoiceId': 'INV-2024-001',
                'storeId': 'loja001',
                'totalAmount': 150.75,
                'taxAmount': 15.08,
                'items': [
                    {'description': 'Produto A', 'amount': 100.00},
                    {'description': 'Produto B', 'amount': 50.75}
                ]
            },
            'getGuestChecks': {
                'guestCheckId': '12345678-1234-5678-9012-123456789012',
                'chkNum': 1001,
                'chkTtl': 85.50,
                'items': [
                    {'name': 'Hambúrguer Artesanal', 'price': 35.00, 'qty': 1},
                    {'name': 'Batata Frita', 'price': 15.00, 'qty': 2},
                    {'name': 'Refrigerante', 'price': 8.50, 'qty': 4}
                ]
            },
            'getChargeBack': {
                'chargeBackId': 'CB-2024-001',
                'storeId': 'loja001',
                'amount': 25.00,
                'reason': 'Produto danificado',
                'status': 'approved'
            },
            'getTransactions': {
                'transactionId': 'TXN-2024-001',
                'storeId': 'loja001',
                'amount': 120.00,
                'paymentMethod': 'credit_card',
                'status': 'completed'
            },
            'getCashManagementDetails': {
                'cashManagementId': 'CM-2024-001',
                'storeId': 'loja001',
                'openingBalance': 500.00,
                'closingBalance': 750.00,
                'totalSales': 1250.00
            }
        }

        # Processar e armazenar dados de cada endpoint com metadados
        caminhos_arquivos = []
        data_hoje = date.today()

        for endpoint, dados in endpoints_dados.items():
            logger.info(f"Armazenando dados do endpoint: {endpoint}")

            # Armazenar com metadados para auditoria e rastreabilidade
            caminho_arquivo = gerenciador_data_lake.armazenar_resposta_api(
                endpoint=endpoint,
                dados=dados,
                data_negocio=data_hoje,
                id_loja='loja001',
                metadados_adicionais={
                    'versao_api': '2.1',
                    'origem': 'sistema_pos',
                    'usuario': 'operador001'
                }
            )
            caminhos_arquivos.append(caminho_arquivo)

        # Calcular estatísticas do data lake para monitoramento
        logger.info("Calculando estatísticas do data lake...")
        estatisticas = gerenciador_data_lake.obter_estatisticas_data_lake()

        # Demonstrar funcionalidade de busca por filtros
        logger.info("Testando busca de dados...")
        dados_encontrados = gerenciador_data_lake.buscar_dados(
            endpoint="getGuestChecks",
            data_inicio=data_hoje,
            data_fim=data_hoje,
            id_loja="loja001"
        )

        # Gerar documentação técnica do data lake
        os.makedirs("docs", exist_ok=True)
        arquivo_doc_data_lake = os.path.join(
            "docs", "documentacao_data_lake.json")

        documentacao_data_lake = {
            'descricao': 'Documentação da estrutura e operação do data lake',
            'estrutura_pastas': gerenciador_data_lake.estrutura_pastas,
            'endpoints_suportados': list(endpoints_dados.keys()),
            'estrategia_particionamento': 'Por data (ano/mês/dia) e loja',
            'formato_armazenamento': 'JSON com metadados',
            'estatisticas': estatisticas,
            'exemplos_uso': {
                'armazenamento': 'gerenciador.armazenar_resposta_api(endpoint, dados, data, loja)',
                'busca': 'gerenciador.buscar_dados(endpoint, data_inicio, data_fim, loja)',
                'backup': 'gerenciador.criar_backup(caminho_backup)'
            }
        }

        import json
        with open(arquivo_doc_data_lake, 'w', encoding='utf-8') as arquivo:
            json.dump(documentacao_data_lake, arquivo,
                      indent=2, ensure_ascii=False, default=str)

        # Exibir resumo executivo dos resultados
        print("\n" + "="*60)
        print("RESUMO DESAFIO 2 - DATA LAKE E PIPELINE DE APIS")
        print("="*60)

        print(f"\nESTRUTURA DO DATA LAKE:")
        for pasta_en, pasta_pt in gerenciador_data_lake.estrutura_pastas.items():
            print(f"   - {pasta_pt}/ ({pasta_en})")

        print(f"\nENDPOINTS PROCESSADOS:")
        for endpoint in endpoints_dados.keys():
            print(f"   - {endpoint}")

        print(f"\nESTATÍSTICAS:")
        print(f"   - Total de arquivos: {estatisticas['total_arquivos']}")
        print(f"   - Tamanho total: {estatisticas['tamanho_total_mb']} MB")
        print(f"   - Endpoints ativos: {len(estatisticas['endpoints'])}")

        print(f"\nTESTE DE BUSCA:")
        print(f"   - Dados encontrados: {len(dados_encontrados)} registros")

        print(f"\nARQUIVOS GERADOS:")
        print(f"   - {arquivo_doc_data_lake}")
        for i, caminho in enumerate(caminhos_arquivos[:3]):
            print(f"   - {caminho}")
        if len(caminhos_arquivos) > 3:
            print(
                f"   - ... e mais {len(caminhos_arquivos) - 3} arquivos de dados")

        return True

    except Exception as erro:
        logger.error(f"Erro no Desafio 2: {erro}")
        return False


def executar_pipeline_completo():
    """
    Executa pipeline adicional de análise de dados.

    Demonstra um pipeline ETL completo:
    1. Extract: Gera dados sintéticos de vendas
    2. Transform: Limpa e processa os dados
    3. Load: Salva resultados em múltiplos formatos
    4. Analyze: Gera relatórios e métricas

    Returns:
        bool: True se executado com sucesso, False caso contrário
    """

    logger.info("EXECUTANDO PIPELINE ADICIONAL DE ANÁLISE")
    logger.info("=" * 60)

    try:
        # Inicializar componentes do pipeline ETL
        extrator = ExtratorDados()
        transformador = TransformadorDados()
        analisador = AnalisadorDados()

        # EXTRACT: Gerar dados sintéticos para demonstração
        logger.info("Gerando dados de exemplo...")
        dados_vendas = extrator.gerar_dados_exemplo_vendas(
            numero_registros=1000)

        # TRANSFORM: Aplicar limpeza e transformações
        logger.info("Transformando e limpando dados...")
        dados_limpos = transformador.limpar_dados_vendas(dados_vendas)

        # Calcular métricas de negócio agregadas
        metricas = transformador.calcular_metricas_vendas(dados_limpos)
        resumo_temporal = transformador.criar_resumo_temporal(dados_limpos)

        # ANALYZE: Gerar relatórios analíticos
        logger.info("Gerando relatório de análise...")
        relatorio = analisador.gerar_relatorio_vendas(dados_limpos)

        # LOAD: Salvar resultados em formatos estruturados
        os.makedirs("dados", exist_ok=True)
        dados_limpos.to_csv('dados/vendas_processadas.csv', index=False)
        metricas.to_csv('dados/metricas_calculadas.csv', index=False)
        resumo_temporal.to_csv('dados/resumo_temporal.csv', index=False)

        # Exibir resumo executivo dos resultados
        print("\n" + "="*60)
        print("RESUMO PIPELINE ADICIONAL - ANÁLISE DE DADOS")
        print("="*60)

        print(f"\nDADOS PROCESSADOS:")
        print(f"   - Registros originais: {len(dados_vendas)}")
        print(f"   - Registros limpos: {len(dados_limpos)}")
        print(f"   - Métricas calculadas: {len(metricas)}")

        print(f"\nMÉTRICAS PRINCIPAIS:")
        print(
            f"   - Total de vendas: R$ {relatorio['metricas_gerais']['total_vendas']:,.2f}")
        print(
            f"   - Ticket médio: R$ {relatorio['metricas_gerais']['ticket_medio']:,.2f}")
        print(
            f"   - Total de transações: {relatorio['metricas_gerais']['total_transacoes']:,}")

        print(f"\nARQUIVOS GERADOS:")
        print(f"   - dados/vendas_processadas.csv")
        print(f"   - dados/metricas_calculadas.csv")
        print(f"   - dados/resumo_temporal.csv")

        return True

    except Exception as erro:
        logger.error(f"Erro no pipeline adicional: {erro}")
        return False


def main():
    """
    Função principal que orquestra a execução de todos os desafios.

    Executa sequencialmente:
    1. Desafio 1: Análise e modelagem JSON → SQL
    2. Desafio 2: Data Lake e pipeline de APIs
    3. Pipeline adicional: ETL de análise de vendas

    Gera relatório final com taxa de sucesso e arquivos produzidos.
    """

    print("DESAFIO ENGENHEIRO DE DADOS 2025")
    print("=" * 60)
    print("Executando solução completa dos desafios de engenharia de dados")
    print("=" * 60)

    logger.info("INICIANDO EXECUÇÃO COMPLETA DOS DESAFIOS")

    # Rastrear sucesso de cada componente para relatório final
    resultados = {
        'desafio_1': False,
        'desafio_2': False,
        'pipeline_adicional': False
    }

    try:
        # Executar cada desafio sequencialmente
        resultados['desafio_1'] = executar_desafio_1()
        resultados['desafio_2'] = executar_desafio_2()
        resultados['pipeline_adicional'] = executar_pipeline_completo()

        # Gerar relatório final de execução
        print("\n" + "="*60)
        print("RESUMO FINAL DA EXECUÇÃO")
        print("="*60)

        print(f"\nRESULTADOS:")
        for desafio, sucesso in resultados.items():
            status = "SUCESSO" if sucesso else "FALHOU"
            print(f"   - {desafio.replace('_', ' ').title()}: {status}")

        total_sucessos = sum(resultados.values())
        print(
            f"\nTAXA DE SUCESSO: {total_sucessos}/3 ({total_sucessos/3*100:.0f}%)")

        if all(resultados.values()):
            print(f"\nTODOS OS DESAFIOS EXECUTADOS COM SUCESSO!")
            print(f"Verifique os arquivos gerados nas pastas:")
            print(f"   - docs/ - Documentações e análises")
            print(f"   - sql/ - Scripts de banco de dados")
            print(f"   - dados/ - Dados processados e data lake")
            print(f"   - pipeline.log - Log de execução")
        else:
            print(
                f"\nAlguns desafios apresentaram problemas. Verifique o log para detalhes.")

        logger.info("EXECUÇÃO COMPLETA FINALIZADA")

    except Exception as erro:
        logger.error(f"ERRO CRÍTICO NA EXECUÇÃO: {erro}")
        print(f"\nERRO CRÍTICO: {erro}")
        print(f"Verifique o arquivo pipeline.log para mais detalhes.")


if __name__ == "__main__":
    main()
