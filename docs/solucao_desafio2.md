# Solução do Desafio 2: Data Lake e Pipeline de APIs

## Visão Geral

Este documento apresenta a solução completa para o **Desafio 2**, que aborda o armazenamento e gerenciamento de dados de APIs de restaurante em um data lake, incluindo estratégias para evolução de schema e operações em escala.

## 1. Por que Armazenar as Respostas das APIs?

### Justificativas Técnicas:

#### 1.1 **Auditoria e Compliance**
- **Rastreabilidade Completa**: Histórico de todas as transações
- **Conformidade Fiscal**: Atendimento às exigências da Receita Federal
- **Auditoria Interna**: Verificação de processos e controles

#### 1.2 **Análise e Business Intelligence**
- **Dados Históricos**: Tendências e padrões de longo prazo
- **Análise Preditiva**: Machine learning sobre dados históricos
- **Relatórios Regulatórios**: Compliance com órgãos fiscalizadores

#### 1.3 **Recuperação e Continuidade**
- **Disaster Recovery**: Reconstrução de dados em caso de falhas
- **Backup Operacional**: Redundância para sistemas críticos
- **Reconciliação**: Verificação de consistência entre sistemas

#### 1.4 **Integração e ETL**
- **Fonte de Verdade**: Dados originais para processamento
- **Reprocessamento**: Capacidade de reexecutar pipelines
- **Integração Futura**: Novos sistemas podem acessar dados históricos

### Benefícios de Negócio:

- **Insights Avançados**: Análises que não são possíveis em tempo real
- **Otimização Operacional**: Identificação de gargalos e oportunidades
- **Conformidade Legal**: Atendimento a regulamentações
- **Redução de Riscos**: Backup e auditoria completos

## 2. Estrutura de Armazenamento do Data Lake

### 2.1 Arquitetura Geral

```
dados/data_lake/
├── dados_brutos/           # Raw data from APIs
│   ├── bilgetFiscalInvoice/
│   ├── getGuestChecks/
│   ├── getChargeBack/
│   ├── getTransactions/
│   └── getCashManagementDetails/
├── dados_processados/      # Processed/transformed data
├── esquemas/              # Schema definitions and versions
├── metadados/            # Metadata for quick queries
├── arquivo/              # Archived old data
└── temporario/           # Temporary processing files
```

### 2.2 Estratégia de Particionamento

#### Particionamento Hierárquico por Data e Loja:
```
dados_brutos/getGuestChecks/
├── ano=2024/
│   ├── mes=01/
│   │   ├── dia=15/
│   │   │   ├── loja=loja001/
│   │   │   │   ├── getGuestChecks_loja001_20240115_143022.json
│   │   │   │   └── getGuestChecks_loja001_20240115_143055.json
│   │   │   └── loja=loja002/
│   │   └── dia=16/
│   └── mes=02/
└── ano=2025/
```

#### Vantagens do Particionamento:

1. **Performance de Consulta**:
   - Eliminação de partições irrelevantes (partition pruning)
   - Paralelização de consultas por partição
   - Índices menores e mais eficientes

2. **Gerenciamento de Dados**:
   - Arquivamento seletivo por período
   - Backup incremental por partição
   - Limpeza automática de dados antigos

3. **Escalabilidade**:
   - Distribuição de carga por partições
   - Processamento paralelo
   - Crescimento linear de performance

### 2.3 Formato de Armazenamento

#### Estrutura do Arquivo JSON:
```json
{
  "metadados": {
    "endpoint": "getGuestChecks",
    "data_negocio": "2024-01-15",
    "id_loja": "loja001",
    "timestamp_ingestao": "2024-01-15T14:30:22.123Z",
    "versao_esquema": "1.0",
    "hash_dados": "a1b2c3d4e5f6...",
    "tamanho_bytes": 2048,
    "origem": "sistema_pos",
    "usuario": "operador001"
  },
  "dados": {
    // Dados originais da API
  }
}
```

#### Benefícios do Formato:

1. **Metadados Ricos**: Contexto completo para cada arquivo
2. **Versionamento**: Controle de evolução de schema
3. **Auditoria**: Rastreabilidade completa
4. **Integridade**: Hash para verificação de dados

## 3. Tratamento de Evolução de Schema

### 3.1 Cenário: Mudança de `guestChecks.taxes` para `guestChecks.taxation`

#### Impactos Identificados:

1. **Quebra de Compatibilidade**:
   - Pipelines existentes falharão
   - Consultas SQL precisarão ser atualizadas
   - Dashboards podem parar de funcionar

2. **Dados Históricos**:
   - Arquivos antigos mantêm estrutura original
   - Necessidade de mapeamento entre versões
   - Consultas unificadas se tornam complexas

3. **Sistemas Downstream**:
   - ETL processes precisam ser atualizados
   - Data warehouses requerem alterações
   - APIs de consumo podem quebrar

### 3.2 Estratégia de Mitigação

#### 3.2.1 Versionamento de Schema

```python
class GerenciadorEvolucaoEsquema:
    def __init__(self):
        self.versoes_esquema = {
            'getGuestChecks': {
                '1.0': {'campo_imposto': 'taxes'},
                '1.1': {'campo_imposto': 'taxation'}
            }
        }
    
    def normalizar_dados(self, endpoint, dados, versao_origem):
        """Converte dados para versão mais recente"""
        if versao_origem == '1.0' and 'taxes' in dados:
            dados['taxation'] = dados.pop('taxes')
        return dados
```

#### 3.2.2 Camada de Abstração

```python
class AdaptadorEsquema:
    def obter_campo_imposto(self, dados, versao_esquema):
        """Abstrai diferenças entre versões"""
        mapeamento = {
            '1.0': 'taxes',
            '1.1': 'taxation'
        }
        campo = mapeamento.get(versao_esquema, 'taxation')
        return dados.get(campo, [])
```

#### 3.2.3 Pipeline de Migração

```python
def migrar_dados_historicos():
    """Migra dados antigos para nova estrutura"""
    for arquivo in buscar_arquivos_versao_antiga():
        dados = carregar_dados(arquivo)
        dados_migrados = aplicar_migracao(dados)
        salvar_dados_migrados(dados_migrados)
        marcar_como_migrado(arquivo)
```

### 3.3 Implementação da Solução

#### 3.3.1 Detecção Automática de Mudanças

```python
class DetectorMudancasEsquema:
    def detectar_mudancas(self, dados_novos, esquema_atual):
        """Detecta mudanças no schema automaticamente"""
        mudancas = []
        
        # Campos removidos
        for campo in esquema_atual:
            if campo not in dados_novos:
                mudancas.append(f"Campo removido: {campo}")
        
        # Campos adicionados
        for campo in dados_novos:
            if campo not in esquema_atual:
                mudancas.append(f"Campo adicionado: {campo}")
        
        return mudancas
```

#### 3.3.2 Notificação de Mudanças

```python
class NotificadorMudancas:
    def notificar_mudanca_esquema(self, endpoint, mudancas):
        """Notifica equipes sobre mudanças de schema"""
        mensagem = f"""
        🚨 MUDANÇA DE SCHEMA DETECTADA
        
        Endpoint: {endpoint}
        Mudanças: {mudancas}
        Ação Requerida: Atualizar pipelines downstream
        """
        self.enviar_alerta(mensagem)
```

#### 3.3.3 Versionamento Automático

```python
class GerenciadorVersaoEsquema:
    def criar_nova_versao(self, endpoint, esquema_novo):
        """Cria nova versão do schema automaticamente"""
        versao_atual = self.obter_versao_atual(endpoint)
        nova_versao = self.incrementar_versao(versao_atual)
        
        self.salvar_esquema(endpoint, nova_versao, esquema_novo)
        self.atualizar_mapeamentos(endpoint, nova_versao)
        
        return nova_versao
```

## 4. Operações e Manutenção

### 4.1 Monitoramento

#### Métricas Principais:
- **Volume de Dados**: GB ingeridos por dia/endpoint
- **Latência**: Tempo entre API call e armazenamento
- **Qualidade**: Percentual de arquivos com schema válido
- **Disponibilidade**: Uptime do sistema de ingestão

#### Alertas Configurados:
- Falha na ingestão de dados
- Mudança de schema detectada
- Espaço em disco baixo
- Performance degradada

### 4.2 Backup e Arquivamento

#### Estratégia de Backup:
```python
class GerenciadorBackup:
    def criar_backup_incremental(self):
        """Backup diário de dados novos"""
        data_ultimo_backup = self.obter_data_ultimo_backup()
        arquivos_novos = self.buscar_arquivos_desde(data_ultimo_backup)
        self.copiar_para_backup(arquivos_novos)
    
    def criar_backup_completo(self):
        """Backup semanal completo"""
        self.copiar_data_lake_completo()
```

#### Política de Retenção:
- **Dados Ativos**: 90 dias no storage principal
- **Dados Arquivados**: 7 anos em storage frio
- **Backups**: 30 dias backup incremental, 1 ano backup completo

### 4.3 Limpeza Automática

```python
class LimpadorDados:
    def limpar_dados_antigos(self, dias_retencao=90):
        """Remove dados mais antigos que período de retenção"""
        data_corte = datetime.now() - timedelta(days=dias_retencao)
        
        for pasta_data in self.listar_pastas_por_data():
            if pasta_data.data < data_corte:
                self.arquivar_pasta(pasta_data)
                self.remover_pasta_local(pasta_data)
```

## 5. Consultas e Análises

### 5.1 Interface de Consulta

```python
class ConsultorDataLake:
    def consultar_vendas_periodo(self, data_inicio, data_fim, loja=None):
        """Consulta vendas por período"""
        return self.gerenciador.buscar_dados(
            endpoint="getGuestChecks",
            data_inicio=data_inicio,
            data_fim=data_fim,
            id_loja=loja
        )
    
    def obter_metricas_loja(self, id_loja, periodo):
        """Métricas consolidadas de uma loja"""
        dados = self.consultar_todos_endpoints(id_loja, periodo)
        return self.calcular_metricas(dados)
```

### 5.2 Integração com Ferramentas de BI

```python
class ConectorBI:
    def exportar_para_parquet(self, consulta):
        """Converte dados JSON para Parquet para BI tools"""
        dados = self.executar_consulta(consulta)
        df = pd.DataFrame(dados)
        return df.to_parquet()
    
    def criar_view_sql(self, nome_view, consulta):
        """Cria view SQL para acesso via BI tools"""
        self.executar_ddl(f"CREATE VIEW {nome_view} AS {consulta}")
```

## 6. Benefícios da Solução Implementada

### 6.1 Técnicos:
✅ **Escalabilidade**: Particionamento permite crescimento linear

✅ **Performance**: Consultas otimizadas por eliminação de partições

✅ **Flexibilidade**: Suporte a evolução de schema sem perda de dados

✅ **Confiabilidade**: Backup, monitoramento e recuperação automáticos

### 6.2 Operacionais:
✅ **Auditoria Completa**: Rastreabilidade de todas as operações

✅ **Compliance**: Atendimento a regulamentações fiscais

✅ **Análise Avançada**: Dados históricos para BI e ML

✅ **Recuperação Rápida**: Restore de dados em caso de falhas

### 6.3 Estratégicos:
✅ **Fonte de Verdade**: Dados originais preservados

✅ **Inovação**: Base para novos produtos e análises

✅ **Competitividade**: Insights únicos sobre operações

✅ **Crescimento**: Infraestrutura preparada para expansão

## 7. Conclusão

A solução de data lake implementada oferece uma base sólida e escalável para o armazenamento e análise de dados de APIs de restaurante. A estratégia de particionamento, versionamento de schema e operações automatizadas garante que o sistema seja robusto, eficiente e preparado para o crescimento futuro do negócio.

A abordagem adotada equilibra as necessidades de performance, flexibilidade e governança, resultando em uma plataforma de dados moderna e adequada para operações empresariais em escala.