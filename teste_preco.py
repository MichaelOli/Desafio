from src.extrair import ExtratorDados
from src.transformar import TransformadorDados

extrator = ExtratorDados()
transformador = TransformadorDados()

print('=== TESTE DE ALTERAÇÃO DE PREÇO ===')
dados_brutos = extrator.extrair_dados_combinados_restaurante()
dados_limpos = transformador.limpar_dados_restaurante(dados_brutos)

# Filtrar apenas o Hambúrguer Artesanal
hamburger = dados_limpos[dados_limpos['nome_item'] == 'Hambúrguer Artesanal']

if not hamburger.empty:
    print('Hambúrguer Artesanal encontrado:')
    print(f'  Nome: {hamburger.iloc[0]["nome_item"]}')
    print(f'  Preço Unitário: R$ {hamburger.iloc[0]["preco_unitario"]:.2f}')
    print(f'  Valor Item: R$ {hamburger.iloc[0]["valor_item"]:.2f}')
    print(f'  Quantidade: {hamburger.iloc[0]["quantidade"]}')

    print('\n=== VERIFICAÇÃO NO ERP.json ===')
    dados_erp = extrator.extrair_json("dados/ERP.json")
    for item in dados_erp['detailLines']:
        if 'menuItem' in item and item['menuItem']['itemName'] == 'Hambúrguer Artesanal':
            print(
                f'  unitPrice no JSON: R$ {item["menuItem"]["unitPrice"]:.2f}')
            print(f'  dspTtl no JSON: R$ {item["menuItem"]["dspTtl"]:.2f}')
            break
else:
    print('Hambúrguer Artesanal não encontrado')
