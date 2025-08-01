"""
Desafio 2 - Gerenciador de Data Lake
Implementa estrutura e gerenciamento do data lake para dados de APIs de restaurante.
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import hashlib
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class GerenciadorDataLake:
    """Gerenciador para estrutura e operações do data lake."""

    def __init__(self, caminho_base: str = "dados/data_lake"):
        self.caminho_base = Path(caminho_base)
        self.estrutura_pastas = {
            'raw': 'dados_brutos',
            'processed': 'dados_processados',
            'schemas': 'esquemas',
            'metadata': 'metadados',
            'archive': 'arquivo',
            'temp': 'temporario'
        }
        self._criar_estrutura_base()

    def _criar_estrutura_base(self):
        """Cria a estrutura base de pastas do data lake."""

        logger.info("Criando estrutura base do data lake")

        # Criar pasta raiz
        self.caminho_base.mkdir(parents=True, exist_ok=True)

        # Criar estrutura de pastas
        for pasta_en, pasta_pt in self.estrutura_pastas.items():
            caminho_pasta = self.caminho_base / pasta_pt
            caminho_pasta.mkdir(exist_ok=True)

            # Criar subpastas para dados brutos e processados
            if pasta_en in ['raw', 'processed']:
                self._criar_estrutura_api(caminho_pasta)

        logger.info(f"Estrutura do data lake criada em: {self.caminho_base}")

    def _criar_estrutura_api(self, caminho_base: Path):
        """Cria estrutura de pastas para cada endpoint de API."""

        endpoints_api = [
            'bilgetFiscalInvoice',
            'getGuestChecks',
            'getChargeBack',
            'getTransactions',
            'getCashManagementDetails'
        ]

        for endpoint in endpoints_api:
            caminho_endpoint = caminho_base / endpoint
            caminho_endpoint.mkdir(exist_ok=True)

            # Criar estrutura de particionamento por ano/mês/dia
            # Exemplo: dados_brutos/getGuestChecks/ano=2024/mes=01/dia=15/
            exemplo_data = datetime.now()
            caminho_particao = (caminho_endpoint /
                                f"ano={exemplo_data.year}" /
                                f"mes={exemplo_data.month:02d}" /
                                f"dia={exemplo_data.day:02d}")
            caminho_particao.mkdir(parents=True, exist_ok=True)

    def armazenar_resposta_api(self,
                               endpoint: str,
                               dados: Dict[str, Any],
                               data_negocio: date,
                               id_loja: str,
                               metadados_adicionais: Optional[Dict] = None) -> str:
        """
        Armazena resposta de API no data lake.

        Args:
            endpoint: Nome do endpoint da API
            dados: Dados da resposta da API
            data_negocio: Data do negócio
            id_loja: ID da loja
            metadados_adicionais: Metadados extras

        Returns:
            Caminho do arquivo salvo
        """
        logger.info(
            f"Armazenando dados do endpoint {endpoint} para loja {id_loja}")

        try:
            # Gerar timestamp único
            timestamp = datetime.now()

            # Criar estrutura de pastas particionada
            caminho_particao = (self.caminho_base /
                                self.estrutura_pastas['raw'] /
                                endpoint /
                                f"ano={data_negocio.year}" /
                                f"mes={data_negocio.month:02d}" /
                                f"dia={data_negocio.day:02d}" /
                                f"loja={id_loja}")

            caminho_particao.mkdir(parents=True, exist_ok=True)

            # Gerar nome do arquivo com timestamp
            nome_arquivo = f"{endpoint}_{id_loja}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            caminho_arquivo = caminho_particao / nome_arquivo

            # Preparar dados com metadados
            dados_completos = {
                'metadados': {
                    'endpoint': endpoint,
                    'data_negocio': data_negocio.isoformat(),
                    'id_loja': id_loja,
                    'timestamp_ingestao': timestamp.isoformat(),
                    'versao_esquema': '1.0',
                    'hash_dados': self._calcular_hash(dados),
                    'tamanho_bytes': len(json.dumps(dados).encode('utf-8'))
                },
                'dados': dados
            }

            # Adicionar metadados extras se fornecidos
            if metadados_adicionais:
                dados_completos['metadados'].update(metadados_adicionais)

            # Salvar arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_completos, arquivo, indent=2,
                          ensure_ascii=False, default=str)

            # Salvar metadados separadamente
            self._salvar_metadados(
                endpoint, dados_completos['metadados'], caminho_arquivo)

            logger.info(f"Dados salvos em: {caminho_arquivo}")
            return str(caminho_arquivo)

        except Exception as erro:
            logger.error(f"Erro ao armazenar dados: {erro}")
            raise

    def _calcular_hash(self, dados: Any) -> str:
        """Calcula hash MD5 dos dados para detecção de mudanças."""

        dados_str = json.dumps(dados, sort_keys=True, default=str)
        return hashlib.md5(dados_str.encode('utf-8')).hexdigest()

    def _salvar_metadados(self, endpoint: str, metadados: Dict, caminho_arquivo: Path):
        """Salva metadados em arquivo separado para consultas rápidas."""

        caminho_metadados = (self.caminho_base /
                             self.estrutura_pastas['metadata'] /
                             endpoint)
        caminho_metadados.mkdir(parents=True, exist_ok=True)

        # Nome do arquivo de metadados baseado no arquivo original
        nome_metadados = f"meta_{caminho_arquivo.stem}.json"
        arquivo_metadados = caminho_metadados / nome_metadados

        # Adicionar informações do arquivo
        metadados_completos = metadados.copy()
        metadados_completos['caminho_arquivo'] = str(caminho_arquivo)
        metadados_completos['nome_arquivo'] = caminho_arquivo.name

        with open(arquivo_metadados, 'w', encoding='utf-8') as arquivo:
            json.dump(metadados_completos, arquivo, indent=2,
                      ensure_ascii=False, default=str)

    def buscar_dados(self,
                     endpoint: str,
                     data_inicio: date,
                     data_fim: date,
                     id_loja: Optional[str] = None) -> List[Dict]:
        """
        Busca dados no data lake por período e loja.

        Args:
            endpoint: Nome do endpoint
            data_inicio: Data inicial
            data_fim: Data final  
            id_loja: ID da loja (opcional)

        Returns:
            Lista de dados encontrados
        """
        logger.info(
            f"Buscando dados do endpoint {endpoint} de {data_inicio} a {data_fim}")

        resultados = []
        data_atual = data_inicio

        while data_atual <= data_fim:
            # Construir caminho da partição
            caminho_particao = (self.caminho_base /
                                self.estrutura_pastas['raw'] /
                                endpoint /
                                f"ano={data_atual.year}" /
                                f"mes={data_atual.month:02d}" /
                                f"dia={data_atual.day:02d}")

            if caminho_particao.exists():
                # Se loja específica foi informada
                if id_loja:
                    caminho_loja = caminho_particao / f"loja={id_loja}"
                    if caminho_loja.exists():
                        resultados.extend(
                            self._ler_arquivos_pasta(caminho_loja))
                else:
                    # Buscar em todas as lojas
                    for pasta_loja in caminho_particao.glob("loja=*"):
                        resultados.extend(self._ler_arquivos_pasta(pasta_loja))

            # Próximo dia
            from datetime import timedelta
            data_atual += timedelta(days=1)

        logger.info(f"Encontrados {len(resultados)} arquivos")
        return resultados

    def _ler_arquivos_pasta(self, caminho_pasta: Path) -> List[Dict]:
        """Lê todos os arquivos JSON de uma pasta."""

        arquivos = []
        for arquivo_json in caminho_pasta.glob("*.json"):
            try:
                with open(arquivo_json, 'r', encoding='utf-8') as arquivo:
                    dados = json.load(arquivo)
                    dados['_caminho_arquivo'] = str(arquivo_json)
                    arquivos.append(dados)
            except Exception as erro:
                logger.warning(f"Erro ao ler arquivo {arquivo_json}: {erro}")

        return arquivos

    def listar_esquemas_disponiveis(self) -> Dict[str, List[str]]:
        """Lista todos os esquemas disponíveis por endpoint."""

        caminho_esquemas = self.caminho_base / self.estrutura_pastas['schemas']
        esquemas = {}

        if caminho_esquemas.exists():
            for pasta_endpoint in caminho_esquemas.iterdir():
                if pasta_endpoint.is_dir():
                    versoes = []
                    for arquivo_esquema in pasta_endpoint.glob("*.json"):
                        versoes.append(arquivo_esquema.stem)
                    esquemas[pasta_endpoint.name] = sorted(versoes)

        return esquemas

    def obter_estatisticas_data_lake(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do data lake."""

        logger.info("Calculando estatísticas do data lake")

        estatisticas = {
            'timestamp_calculo': datetime.now().isoformat(),
            'estrutura_pastas': {},
            'total_arquivos': 0,
            'tamanho_total_mb': 0,
            'endpoints': {},
            'periodo_dados': {
                'data_mais_antiga': None,
                'data_mais_recente': None
            }
        }

        # Analisar cada pasta principal
        for pasta_en, pasta_pt in self.estrutura_pastas.items():
            caminho_pasta = self.caminho_base / pasta_pt
            if caminho_pasta.exists():
                info_pasta = self._analisar_pasta(caminho_pasta)
                estatisticas['estrutura_pastas'][pasta_pt] = info_pasta

                if pasta_en == 'raw':
                    # Analisar endpoints em dados brutos
                    for pasta_endpoint in caminho_pasta.iterdir():
                        if pasta_endpoint.is_dir():
                            info_endpoint = self._analisar_endpoint(
                                pasta_endpoint)
                            estatisticas['endpoints'][pasta_endpoint.name] = info_endpoint

        # Calcular totais
        for info_pasta in estatisticas['estrutura_pastas'].values():
            estatisticas['total_arquivos'] += info_pasta['total_arquivos']
            estatisticas['tamanho_total_mb'] += info_pasta['tamanho_mb']

        return estatisticas

    def _analisar_pasta(self, caminho_pasta: Path) -> Dict[str, Any]:
        """Analisa uma pasta e retorna estatísticas."""

        total_arquivos = 0
        tamanho_total = 0

        for arquivo in caminho_pasta.rglob("*"):
            if arquivo.is_file():
                total_arquivos += 1
                tamanho_total += arquivo.stat().st_size

        return {
            'total_arquivos': total_arquivos,
            'tamanho_mb': round(tamanho_total / (1024 * 1024), 2),
            'caminho': str(caminho_pasta)
        }

    def _analisar_endpoint(self, caminho_endpoint: Path) -> Dict[str, Any]:
        """Analisa um endpoint específico."""

        info = {
            'total_arquivos': 0,
            'lojas_unicas': set(),
            'datas_disponiveis': set(),
            'tamanho_mb': 0
        }

        for arquivo in caminho_endpoint.rglob("*.json"):
            if arquivo.is_file():
                info['total_arquivos'] += 1
                info['tamanho_mb'] += arquivo.stat().st_size / (1024 * 1024)

                # Extrair informações do caminho
                partes_caminho = arquivo.parts
                for parte in partes_caminho:
                    if parte.startswith('loja='):
                        info['lojas_unicas'].add(parte.split('=')[1])
                    elif parte.startswith('ano='):
                        ano = parte.split('=')[1]
                        # Buscar mês e dia nas próximas partes
                        idx = partes_caminho.index(parte)
                        if idx + 2 < len(partes_caminho):
                            mes = partes_caminho[idx + 1].split('=')[1]
                            dia = partes_caminho[idx + 2].split('=')[1]
                            info['datas_disponiveis'].add(f"{ano}-{mes}-{dia}")

        # Converter sets para listas para serialização JSON
        info['lojas_unicas'] = sorted(list(info['lojas_unicas']))
        info['datas_disponiveis'] = sorted(list(info['datas_disponiveis']))
        info['tamanho_mb'] = round(info['tamanho_mb'], 2)

        return info

    def criar_backup(self, caminho_backup: str) -> str:
        """Cria backup completo do data lake."""

        logger.info(f"Criando backup do data lake em: {caminho_backup}")

        try:
            # Criar pasta de backup
            caminho_backup_path = Path(caminho_backup)
            caminho_backup_path.mkdir(parents=True, exist_ok=True)

            # Nome do backup com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f"backup_data_lake_{timestamp}"
            caminho_backup_completo = caminho_backup_path / nome_backup

            # Copiar estrutura completa
            shutil.copytree(self.caminho_base, caminho_backup_completo)

            # Criar arquivo de metadados do backup
            metadados_backup = {
                'timestamp_backup': datetime.now().isoformat(),
                'caminho_original': str(self.caminho_base),
                'caminho_backup': str(caminho_backup_completo),
                'estatisticas': self.obter_estatisticas_data_lake()
            }

            arquivo_metadados = caminho_backup_completo / "metadados_backup.json"
            with open(arquivo_metadados, 'w', encoding='utf-8') as arquivo:
                json.dump(metadados_backup, arquivo, indent=2,
                          ensure_ascii=False, default=str)

            logger.info(
                f"Backup criado com sucesso: {caminho_backup_completo}")
            return str(caminho_backup_completo)

        except Exception as erro:
            logger.error(f"Erro ao criar backup: {erro}")
            raise

    def limpar_dados_antigos(self, dias_retencao: int = 90):
        """Remove dados mais antigos que o período de retenção."""

        logger.info(f"Limpando dados com mais de {dias_retencao} dias")

        from datetime import timedelta
        data_corte = datetime.now().date() - timedelta(days=dias_retencao)

        arquivos_removidos = 0
        tamanho_liberado = 0

        # Percorrer dados brutos
        caminho_raw = self.caminho_base / self.estrutura_pastas['raw']

        for pasta_endpoint in caminho_raw.iterdir():
            if pasta_endpoint.is_dir():
                for pasta_ano in pasta_endpoint.glob("ano=*"):
                    ano = int(pasta_ano.name.split('=')[1])

                    for pasta_mes in pasta_ano.glob("mes=*"):
                        mes = int(pasta_mes.name.split('=')[1])

                        for pasta_dia in pasta_mes.glob("dia=*"):
                            dia = int(pasta_dia.name.split('=')[1])

                            try:
                                data_pasta = date(ano, mes, dia)

                                if data_pasta < data_corte:
                                    # Calcular tamanho antes de remover
                                    for arquivo in pasta_dia.rglob("*"):
                                        if arquivo.is_file():
                                            tamanho_liberado += arquivo.stat().st_size
                                            arquivos_removidos += 1

                                    # Remover pasta completa
                                    shutil.rmtree(pasta_dia)
                                    logger.info(f"Removida pasta: {pasta_dia}")

                            except ValueError:
                                logger.warning(
                                    f"Data inválida na pasta: {pasta_dia}")

        tamanho_liberado_mb = round(tamanho_liberado / (1024 * 1024), 2)
        logger.info(
            f"Limpeza concluída: {arquivos_removidos} arquivos removidos, {tamanho_liberado_mb} MB liberados")

        return {
            'arquivos_removidos': arquivos_removidos,
            'tamanho_liberado_mb': tamanho_liberado_mb,
            'data_corte': data_corte.isoformat()
        }


def main():
    """Função principal para demonstrar o gerenciador de data lake."""

    logging.basicConfig(level=logging.INFO)

    # Criar gerenciador
    gerenciador = GerenciadorDataLake()

    # Dados de exemplo para demonstração
    dados_exemplo = {
        "guestCheckId": "12345678-1234-5678-9012-123456789012",
        "chkNum": 1001,
        "chkTtl": 50.05,
        "items": [
            {"name": "Hambúrguer", "price": 25.00},
            {"name": "Refrigerante", "price": 5.00}
        ]
    }

    try:
        # Armazenar dados de exemplo
        caminho_arquivo = gerenciador.armazenar_resposta_api(
            endpoint="getGuestChecks",
            dados=dados_exemplo,
            data_negocio=date.today(),
            id_loja="loja001",
            metadados_adicionais={
                "versao_api": "2.1", "origem": "pos_terminal_1"}
        )

        print(f"Dados armazenados em: {caminho_arquivo}")

        # Obter estatísticas
        estatisticas = gerenciador.obter_estatisticas_data_lake()

        print("\nESTATÍSTICAS DO DATA LAKE:")
        print(f"   Total de arquivos: {estatisticas['total_arquivos']}")
        print(f"   Tamanho total: {estatisticas['tamanho_total_mb']} MB")

        print("\nENDPOINTS DISPONÍVEIS:")
        for endpoint, info in estatisticas['endpoints'].items():
            print(f"   • {endpoint}: {info['total_arquivos']} arquivos")

        # Buscar dados
        dados_encontrados = gerenciador.buscar_dados(
            endpoint="getGuestChecks",
            data_inicio=date.today(),
            data_fim=date.today(),
            id_loja="loja001"
        )

        print(f"\nBUSCA DE DADOS:")
        print(f"   Encontrados: {len(dados_encontrados)} registros")

        print(f"\nDemonstração do Data Lake concluída!")
        print(f"Estrutura criada em: {gerenciador.caminho_base}")

    except Exception as erro:
        logger.error(f"Erro na demonstração: {erro}")
        raise


if __name__ == "__main__":
    main()
