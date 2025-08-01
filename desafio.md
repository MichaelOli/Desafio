# DESAFIO 1

## Contexto
A resposta de um determinado endpoint de API de ERP para uma loja de um restaurante está no arquivo `ERP.json`. Este exemplo corresponde a um determinado pedido (`guestCheckId`) com um único item (`guestCheckLineItemId`), referente a um único item de menu (`menuItem`).  
**Link:** `ERP.json`

## Tarefas

### 1. Descreva o esquema JSON correspondente ao exemplo acima
- Descrição do esquema e análise das entidades presentes.

### 2. Contexto
No exemplo fornecido, o objeto `detailLines` contém um `menuItem`. Ele também pode conter instâncias de:
- `discount`
- `serviceCharge`
- `tenderMedia`
- `errorCode`
Transcreva o JSON para tabelas SQL. A implementação deve fazer sentido para operações de restaurante.

### 3. Descreva a abordagem escolhida em detalhes. Justifique a escolha
- Detalhamento do processo de pensamento, incluindo preocupações e consequências.

## Recomendações
- Faça um esboço antes de começar.
- Considere que esta tarefa abrange toda a cadeia de restaurantes.
- Descreva seu processo de pensamento, preocupações e as consequências detalhadamente.
- Certifique-se de incluir pelo menos uma linha por ativo (asset).
- Esperamos ver um código que você estaria confortável em colocar em produção.
- Não hesite em pedir esclarecimentos ou, se preferir, faça uma suposição e siga com ela.

---

# DESAFIO 2

## Contexto
Nossa equipe de inteligência de negócios precisa analisar a receita de todas as lojas de uma rede de restaurantes. Essas informações podem ser obtidas por meio de 5 endpoints de API.

| Method | API Endpoint          | Payload                          |
|--------|-----------------------|----------------------------------|
| POST   | /bilgetFiscalInvoice  | - `busDt: string(date)`<br>- `storeId: string` |
| POST   | /res/getGuestChecks   | - `busDt: string(date)`<br>- `storeId: string` |
| POST   | /org/getChargeBack    | - `busDt: string(date)`<br>- `storeId: string` |
| POST   | /trans/getTransactions | - `busDt: string(date)`<br>- `storeId: string` |
| POST   | /inv/getCashManagementDetails | - `busDt: string(date)`<br>- `storeId: string` |

## Tarefa
Esta é uma continuação do primeiro desafio. Você deve armazenar os dados das respostas das APIs (JSON) no nosso data lake.

### 1. Por que armazenar as respostas das APIs?
- Justificativas para o armazenamento dos dados.

### 2. Como você armazenaria os dados? Crie uma estrutura de pastas capaz de armazenar as respostas da API. Ela deve permitir manipulação, verificações, buscas e pesquisas rápidas
- Proposta de estrutura e implementação.

### 3. Considere que a resposta do endpoint `getGuestChecks` foi alterada, por exemplo, `guestChecks.taxes` foi renomeado para `guestChecks.taxation`. O que isso implicaria?
- Análise dos impactos e soluções.

## Recomendações
- Faça um esboço antes de começar.
- Considere que esta tarefa abrange toda a cadeia de restaurantes.
- Descreva seu processo de pensamento, preocupações e as consequências detalhadamente.
- Certifique-se de incluir pelo menos uma linha por ativo (asset).
- Esperamos ver um código que você estaria confortável em colocar em produção.
- Não hesite em pedir esclarecimentos ou, se preferir, faça uma suposição e siga com ela.