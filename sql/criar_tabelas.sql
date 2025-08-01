-- =====================================================
-- SCRIPT DDL - SISTEMA ERP RESTAURANTE
-- Gerado em: 2025-07-31 18:53:25
-- =====================================================

-- CRIAÇÃO DE TABELAS
-- =====================================================

-- Tabela: comandas_cliente
-- Tabela principal de comandas/pedidos
CREATE TABLE comandas_cliente (
    id_comanda_cliente UUID PRIMARY KEY,
    numero_comanda INTEGER NOT NULL,
    data_abertura_negocio DATE NOT NULL,
    abertura_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    abertura_local TIMESTAMP WITH TIME ZONE NOT NULL,
    data_fechamento_negocio DATE,
    fechamento_utc TIMESTAMP WITH TIME ZONE,
    fechamento_local TIMESTAMP WITH TIME ZONE,
    ultima_transacao_utc TIMESTAMP WITH TIME ZONE,
    ultima_atualizacao_utc TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    flag_fechada BOOLEAN DEFAULT FALSE,
    contagem_clientes INTEGER CHECK (contagem_clientes >= 0),
    subtotal DECIMAL(12,2) CHECK (subtotal >= 0),
    total_vendas_nao_tributaveis DECIMAL(12,2) DEFAULT 0.00,
    total_comanda DECIMAL(12,2) CHECK (total_comanda >= 0),
    total_desconto DECIMAL(12,2) DEFAULT 0.00,
    total_pagamento DECIMAL(12,2) DEFAULT 0.00,
    total_saldo_devedor DECIMAL(12,2) DEFAULT 0.00,
    numero_centro_receita INTEGER,
    numero_tipo_pedido INTEGER,
    numero_canal_pedido INTEGER,
    numero_mesa INTEGER,
    nome_mesa VARCHAR(100),
    numero_funcionario INTEGER,
    contagem_rodadas_servico INTEGER DEFAULT 1,
    contagem_impressoes_comanda INTEGER DEFAULT 0,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: linhas_detalhe_comanda
-- Linhas de detalhe das comandas
CREATE TABLE linhas_detalhe_comanda (
    id_linha_item_comanda UUID PRIMARY KEY,
    id_comanda_cliente UUID NOT NULL REFERENCES comandas_cliente(id_comanda_cliente),
    numero_centro_receita INTEGER,
    numero_tipo_pedido_detalhe INTEGER,
    numero_canal_pedido_detalhe INTEGER,
    numero_linha INTEGER NOT NULL,
    id_detalhe INTEGER NOT NULL,
    detalhe_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    detalhe_local TIMESTAMP WITH TIME ZONE NOT NULL,
    ultima_atualizacao_utc TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_negocio DATE NOT NULL,
    numero_estacao_trabalho INTEGER,
    total_exibicao DECIMAL(12,2),
    quantidade_exibicao DECIMAL(8,3),
    total_agregado DECIMAL(12,2),
    quantidade_agregada DECIMAL(8,3),
    id_funcionario_comanda INTEGER,
    numero_funcionario_comanda INTEGER,
    numero_rodada_servico INTEGER DEFAULT 1,
    numero_assento INTEGER,
    tipo_linha VARCHAR(50) CHECK (tipo_linha IN ('menu_item', 'discount', 'service_charge', 'tender_media', 'error_code')),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: itens_menu
-- Itens do cardápio/menu
CREATE TABLE itens_menu (
    id_item_menu VARCHAR(100) PRIMARY KEY,
    id_linha_item_comanda UUID REFERENCES linhas_detalhe_comanda(id_linha_item_comanda),
    numero_item_menu INTEGER NOT NULL,
    flag_modificacao BOOLEAN DEFAULT FALSE,
    imposto_incluido DECIMAL(10,2) DEFAULT 0.00,
    impostos_ativos VARCHAR(100),
    nivel_preco INTEGER DEFAULT 1,
    nome_item VARCHAR(255) NOT NULL,
    nome_categoria VARCHAR(100),
    id_categoria VARCHAR(100),
    nome_grupo_familia VARCHAR(100),
    id_grupo_familia VARCHAR(100),
    preco_unitario DECIMAL(10,2) CHECK (preco_unitario >= 0),
    total_exibicao DECIMAL(12,2),
    quantidade_exibicao DECIMAL(8,3) CHECK (quantidade_exibicao > 0),
    total_agregado DECIMAL(12,2),
    quantidade_agregada DECIMAL(8,3) CHECK (quantidade_agregada > 0),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: impostos_comanda_cliente
-- Impostos aplicados às comandas
CREATE TABLE impostos_comanda_cliente (
    id SERIAL PRIMARY KEY,
    id_comanda_cliente UUID NOT NULL REFERENCES comandas_cliente(id_comanda_cliente),
    numero_imposto INTEGER NOT NULL,
    total_vendas_tributaveis DECIMAL(12,2) CHECK (total_vendas_tributaveis >= 0),
    total_imposto_coletado DECIMAL(12,2) CHECK (total_imposto_coletado >= 0),
    taxa_imposto DECIMAL(5,2) CHECK (taxa_imposto >= 0 AND taxa_imposto <= 100),
    tipo_imposto INTEGER,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: descontos
-- Descontos aplicados
CREATE TABLE descontos (
    id_desconto VARCHAR(100) PRIMARY KEY,
    id_linha_item_comanda UUID REFERENCES linhas_detalhe_comanda(id_linha_item_comanda),
    numero_desconto INTEGER NOT NULL,
    nome_desconto VARCHAR(255) NOT NULL,
    tipo_desconto VARCHAR(50) CHECK (tipo_desconto IN ('percentage', 'fixed_amount', 'buy_x_get_y')),
    valor_desconto DECIMAL(10,2) CHECK (valor_desconto >= 0),
    quantia_desconto DECIMAL(10,2) CHECK (quantia_desconto >= 0),
    aplicado_a VARCHAR(50),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: taxas_servico
-- Taxas de serviço aplicadas
CREATE TABLE taxas_servico (
    id_taxa_servico VARCHAR(100) PRIMARY KEY,
    id_linha_item_comanda UUID REFERENCES linhas_detalhe_comanda(id_linha_item_comanda),
    numero_taxa_servico INTEGER NOT NULL,
    nome_taxa_servico VARCHAR(255) NOT NULL,
    tipo_taxa_servico VARCHAR(50),
    quantia_taxa_servico DECIMAL(10,2) CHECK (quantia_taxa_servico >= 0),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: meios_pagamento
-- Meios de pagamento utilizados
CREATE TABLE meios_pagamento (
    id_meio_pagamento VARCHAR(100) PRIMARY KEY,
    id_linha_item_comanda UUID REFERENCES linhas_detalhe_comanda(id_linha_item_comanda),
    numero_meio_pagamento INTEGER NOT NULL,
    nome_meio_pagamento VARCHAR(255) NOT NULL,
    tipo_meio_pagamento VARCHAR(50) CHECK (tipo_meio_pagamento IN ('cash', 'credit_card', 'debit_card', 'pix', 'voucher')),
    quantia_pagamento DECIMAL(12,2) CHECK (quantia_pagamento > 0),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Tabela: codigos_erro
-- Códigos de erro registrados
CREATE TABLE codigos_erro (
    id_codigo_erro VARCHAR(100) PRIMARY KEY,
    id_linha_item_comanda UUID REFERENCES linhas_detalhe_comanda(id_linha_item_comanda),
    numero_codigo_erro INTEGER NOT NULL,
    descricao_erro TEXT,
    severidade_erro VARCHAR(20) CHECK (severidade_erro IN ('low', 'medium', 'high', 'critical')),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- CRIAÇÃO DE ÍNDICES
-- =====================================================
CREATE INDEX idx_comandas_cliente_data_negocio ON comandas_cliente (data_abertura_negocio);
CREATE INDEX idx_comandas_cliente_numero_mesa ON comandas_cliente (numero_mesa, data_abertura_negocio);
CREATE INDEX idx_linhas_detalhe_id_comanda_cliente ON linhas_detalhe_comanda (id_comanda_cliente);
CREATE INDEX idx_linhas_detalhe_data_negocio ON linhas_detalhe_comanda (data_negocio);
CREATE INDEX idx_itens_menu_categoria ON itens_menu (nome_categoria);
CREATE INDEX idx_impostos_id_comanda_cliente ON impostos_comanda_cliente (id_comanda_cliente);

-- COMENTÁRIOS NAS TABELAS E COLUNAS
-- =====================================================
COMMENT ON TABLE comandas_cliente IS 'Tabela principal de comandas/pedidos';
COMMENT ON COLUMN comandas_cliente.id_comanda_cliente IS 'Identificador único da comanda';
COMMENT ON COLUMN comandas_cliente.numero_comanda IS 'Número sequencial da comanda';
COMMENT ON COLUMN comandas_cliente.data_abertura_negocio IS 'Data de abertura da comanda';
COMMENT ON COLUMN comandas_cliente.abertura_utc IS 'Timestamp de abertura em UTC';
COMMENT ON COLUMN comandas_cliente.abertura_local IS 'Timestamp de abertura local';
COMMENT ON COLUMN comandas_cliente.data_fechamento_negocio IS 'Data de fechamento da comanda';
COMMENT ON COLUMN comandas_cliente.fechamento_utc IS 'Timestamp de fechamento em UTC';
COMMENT ON COLUMN comandas_cliente.fechamento_local IS 'Timestamp de fechamento local';
COMMENT ON COLUMN comandas_cliente.ultima_transacao_utc IS 'Última transação em UTC';
COMMENT ON COLUMN comandas_cliente.ultima_atualizacao_utc IS 'Última atualização do registro';
COMMENT ON COLUMN comandas_cliente.flag_fechada IS 'Indica se a comanda está fechada';
COMMENT ON COLUMN comandas_cliente.contagem_clientes IS 'Número de clientes na mesa';
COMMENT ON COLUMN comandas_cliente.subtotal IS 'Subtotal antes de impostos e descontos';
COMMENT ON COLUMN comandas_cliente.total_vendas_nao_tributaveis IS 'Total de vendas não tributáveis';
COMMENT ON COLUMN comandas_cliente.total_comanda IS 'Total final da comanda';
COMMENT ON COLUMN comandas_cliente.total_desconto IS 'Total de descontos aplicados';
COMMENT ON COLUMN comandas_cliente.total_pagamento IS 'Total pago';
COMMENT ON COLUMN comandas_cliente.total_saldo_devedor IS 'Saldo devedor';
COMMENT ON COLUMN comandas_cliente.numero_centro_receita IS 'Número do centro de receita';
COMMENT ON COLUMN comandas_cliente.numero_tipo_pedido IS 'Tipo de pedido';
COMMENT ON COLUMN comandas_cliente.numero_canal_pedido IS 'Canal do pedido';
COMMENT ON COLUMN comandas_cliente.numero_mesa IS 'Número da mesa';
COMMENT ON COLUMN comandas_cliente.nome_mesa IS 'Nome/identificação da mesa';
COMMENT ON COLUMN comandas_cliente.numero_funcionario IS 'Número do funcionário responsável';
COMMENT ON COLUMN comandas_cliente.contagem_rodadas_servico IS 'Número de rodadas de serviço';
COMMENT ON COLUMN comandas_cliente.contagem_impressoes_comanda IS 'Número de vezes que a comanda foi impressa';
COMMENT ON COLUMN comandas_cliente.criado_em IS 'Data de criação do registro';
COMMENT ON COLUMN comandas_cliente.atualizado_em IS 'Data de última atualização';
COMMENT ON TABLE linhas_detalhe_comanda IS 'Linhas de detalhe das comandas';
COMMENT ON COLUMN linhas_detalhe_comanda.id_linha_item_comanda IS 'Identificador único da linha';
COMMENT ON COLUMN linhas_detalhe_comanda.id_comanda_cliente IS 'Referência à comanda principal';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_centro_receita IS 'Centro de receita';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_tipo_pedido_detalhe IS 'Tipo de pedido do detalhe';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_canal_pedido_detalhe IS 'Canal do pedido do detalhe';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_linha IS 'Número sequencial da linha';
COMMENT ON COLUMN linhas_detalhe_comanda.id_detalhe IS 'ID do detalhe';
COMMENT ON COLUMN linhas_detalhe_comanda.detalhe_utc IS 'Timestamp do detalhe em UTC';
COMMENT ON COLUMN linhas_detalhe_comanda.detalhe_local IS 'Timestamp do detalhe local';
COMMENT ON COLUMN linhas_detalhe_comanda.ultima_atualizacao_utc IS 'Última atualização em UTC';
COMMENT ON COLUMN linhas_detalhe_comanda.data_negocio IS 'Data do negócio';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_estacao_trabalho IS 'Número da estação de trabalho';
COMMENT ON COLUMN linhas_detalhe_comanda.total_exibicao IS 'Total exibido';
COMMENT ON COLUMN linhas_detalhe_comanda.quantidade_exibicao IS 'Quantidade exibida';
COMMENT ON COLUMN linhas_detalhe_comanda.total_agregado IS 'Total agregado';
COMMENT ON COLUMN linhas_detalhe_comanda.quantidade_agregada IS 'Quantidade agregada';
COMMENT ON COLUMN linhas_detalhe_comanda.id_funcionario_comanda IS 'ID do funcionário da comanda';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_funcionario_comanda IS 'Número do funcionário da comanda';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_rodada_servico IS 'Número da rodada de serviço';
COMMENT ON COLUMN linhas_detalhe_comanda.numero_assento IS 'Número do assento/posição';
COMMENT ON COLUMN linhas_detalhe_comanda.tipo_linha IS 'Tipo da linha de detalhe';
COMMENT ON COLUMN linhas_detalhe_comanda.criado_em IS 'Data de criação do registro';
COMMENT ON COLUMN linhas_detalhe_comanda.atualizado_em IS 'Data de última atualização';
COMMENT ON TABLE itens_menu IS 'Itens do cardápio/menu';
COMMENT ON COLUMN itens_menu.id_item_menu IS 'Identificador único do item';
COMMENT ON COLUMN itens_menu.id_linha_item_comanda IS 'Referência à linha de detalhe';
COMMENT ON COLUMN itens_menu.numero_item_menu IS 'Número do item no sistema';
COMMENT ON COLUMN itens_menu.flag_modificacao IS 'Indica se o item foi modificado';
COMMENT ON COLUMN itens_menu.imposto_incluido IS 'Imposto incluído no preço';
COMMENT ON COLUMN itens_menu.impostos_ativos IS 'Impostos ativos para o item';
COMMENT ON COLUMN itens_menu.nivel_preco IS 'Nível de preço aplicado';
COMMENT ON COLUMN itens_menu.nome_item IS 'Nome do item';
COMMENT ON COLUMN itens_menu.nome_categoria IS 'Nome da categoria';
COMMENT ON COLUMN itens_menu.id_categoria IS 'ID da categoria';
COMMENT ON COLUMN itens_menu.nome_grupo_familia IS 'Nome do grupo familiar';
COMMENT ON COLUMN itens_menu.id_grupo_familia IS 'ID do grupo familiar';
COMMENT ON COLUMN itens_menu.preco_unitario IS 'Preço unitário';
COMMENT ON COLUMN itens_menu.total_exibicao IS 'Total exibido';
COMMENT ON COLUMN itens_menu.quantidade_exibicao IS 'Quantidade exibida';
COMMENT ON COLUMN itens_menu.total_agregado IS 'Total agregado';
COMMENT ON COLUMN itens_menu.quantidade_agregada IS 'Quantidade agregada';
COMMENT ON COLUMN itens_menu.criado_em IS 'Data de criação do registro';
COMMENT ON COLUMN itens_menu.atualizado_em IS 'Data de última atualização';
COMMENT ON TABLE impostos_comanda_cliente IS 'Impostos aplicados às comandas';
COMMENT ON COLUMN impostos_comanda_cliente.id IS 'Chave primária sequencial';
COMMENT ON COLUMN impostos_comanda_cliente.id_comanda_cliente IS 'Referência à comanda';
COMMENT ON COLUMN impostos_comanda_cliente.numero_imposto IS 'Número do imposto';
COMMENT ON COLUMN impostos_comanda_cliente.total_vendas_tributaveis IS 'Total de vendas tributáveis';
COMMENT ON COLUMN impostos_comanda_cliente.total_imposto_coletado IS 'Total de imposto coletado';
COMMENT ON COLUMN impostos_comanda_cliente.taxa_imposto IS 'Taxa de imposto em percentual';
COMMENT ON COLUMN impostos_comanda_cliente.tipo_imposto IS 'Tipo de imposto';
COMMENT ON COLUMN impostos_comanda_cliente.criado_em IS 'Data de criação do registro';
COMMENT ON TABLE descontos IS 'Descontos aplicados';
COMMENT ON COLUMN descontos.id_desconto IS 'Identificador único do desconto';
COMMENT ON COLUMN descontos.id_linha_item_comanda IS 'Referência à linha de detalhe';
COMMENT ON COLUMN descontos.numero_desconto IS 'Número do desconto';
COMMENT ON COLUMN descontos.nome_desconto IS 'Nome do desconto';
COMMENT ON COLUMN descontos.tipo_desconto IS 'Tipo de desconto';
COMMENT ON COLUMN descontos.valor_desconto IS 'Valor do desconto';
COMMENT ON COLUMN descontos.quantia_desconto IS 'Valor monetário do desconto';
COMMENT ON COLUMN descontos.aplicado_a IS 'A que o desconto foi aplicado';
COMMENT ON COLUMN descontos.criado_em IS 'Data de criação do registro';
COMMENT ON TABLE taxas_servico IS 'Taxas de serviço aplicadas';
COMMENT ON COLUMN taxas_servico.id_taxa_servico IS 'Identificador único da taxa';
COMMENT ON COLUMN taxas_servico.id_linha_item_comanda IS 'Referência à linha de detalhe';
COMMENT ON COLUMN taxas_servico.numero_taxa_servico IS 'Número da taxa de serviço';
COMMENT ON COLUMN taxas_servico.nome_taxa_servico IS 'Nome da taxa de serviço';
COMMENT ON COLUMN taxas_servico.tipo_taxa_servico IS 'Tipo da taxa de serviço';
COMMENT ON COLUMN taxas_servico.quantia_taxa_servico IS 'Valor da taxa de serviço';
COMMENT ON COLUMN taxas_servico.criado_em IS 'Data de criação do registro';
COMMENT ON TABLE meios_pagamento IS 'Meios de pagamento utilizados';
COMMENT ON COLUMN meios_pagamento.id_meio_pagamento IS 'Identificador único do meio de pagamento';
COMMENT ON COLUMN meios_pagamento.id_linha_item_comanda IS 'Referência à linha de detalhe';
COMMENT ON COLUMN meios_pagamento.numero_meio_pagamento IS 'Número do meio de pagamento';
COMMENT ON COLUMN meios_pagamento.nome_meio_pagamento IS 'Nome do meio de pagamento';
COMMENT ON COLUMN meios_pagamento.tipo_meio_pagamento IS 'Tipo do meio de pagamento';
COMMENT ON COLUMN meios_pagamento.quantia_pagamento IS 'Valor pago';
COMMENT ON COLUMN meios_pagamento.criado_em IS 'Data de criação do registro';
COMMENT ON TABLE codigos_erro IS 'Códigos de erro registrados';
COMMENT ON COLUMN codigos_erro.id_codigo_erro IS 'Identificador único do erro';
COMMENT ON COLUMN codigos_erro.id_linha_item_comanda IS 'Referência à linha de detalhe';
COMMENT ON COLUMN codigos_erro.numero_codigo_erro IS 'Número do código de erro';
COMMENT ON COLUMN codigos_erro.descricao_erro IS 'Descrição do erro';
COMMENT ON COLUMN codigos_erro.severidade_erro IS 'Severidade do erro';
COMMENT ON COLUMN codigos_erro.criado_em IS 'Data de criação do registro';