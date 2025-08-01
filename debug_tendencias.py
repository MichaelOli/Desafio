from src.extrair import ExtratorDados
from src.transformar import TransformadorDados
import pandas as pd

extrator = ExtratorDados()
transformador = TransformadorDados()

dados_brutos = extrator.extrair_dados_combinados_restaurante()
dados_limpos = transformador.limpar_dados_restaurante(dados_brutos)

print('=== DADOS PARA ANÁLISE DE TENDÊNCIAS ===')
print('Total de registros:', len(dados_limpos))
print('Colunas disponíveis:', list(dados_limpos.columns))

if 'data_abertura' in dados_limpos.columns:
    print('\n=== ANÁLISE DE DATAS ===')
    datas_unicas = dados_limpos['data_abertura'].dt.date.unique()
    print('Datas únicas:', datas_unicas)

    print('\n=== VENDAS POR MÊS ===')
    vendas_mensais = dados_limpos.groupby(
        dados_limpos['data_abertura'].dt.to_period('M'))['valor_item'].sum()
    print('Períodos encontrados:', len(vendas_mensais))
    for periodo, valor in vendas_mensais.items():
        print(f'  {periodo}: R$ {valor:.2f}')

    print('\n=== PROBLEMA IDENTIFICADO ===')
    if len(vendas_mensais) == 1:
        print('Apenas 1 período encontrado - por isso melhor e pior são iguais!')
        print(
            'Solução: Precisamos de dados de múltiplos meses para análise de tendências')
    else:
        print('Múltiplos períodos encontrados - análise válida')

else:
    print('Coluna data_abertura não encontrada')
