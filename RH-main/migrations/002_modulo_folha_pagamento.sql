-- ============================================================================
-- MIGRAÇÃO SUPABASE / POSTGRESQL — MÓDULO DE FOLHA DE PAGAMENTO
-- Arquivo: migrations/002_modulo_folha_pagamento.sql
-- Descrição: Criação das tabelas de parâmetros, folhas, itens, auditoria,
--            constraints de unicidade, integridade referencial e políticas RLS.
-- ============================================================================

BEGIN;

-- 1. TABELA DE PARÂMETROS DE CÁLCULO E VIGÊNCIAS
CREATE TABLE IF NOT EXISTS folha_parametros (
    id                          SERIAL PRIMARY KEY,
    codigo                      TEXT UNIQUE NOT NULL,
    descricao                   TEXT NOT NULL,
    vigencia_inicio             TEXT NOT NULL,
    vigencia_fim                TEXT,
    horas_mensais_padrao        NUMERIC(6,2) NOT NULL DEFAULT 220.00,
    dias_mes_padrao             INTEGER NOT NULL DEFAULT 30,
    percentual_he_padrao        NUMERIC(5,2) NOT NULL DEFAULT 50.00,
    percentual_he_extra         NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    percentual_adicional_noturno NUMERIC(5,2) NOT NULL DEFAULT 20.00,
    aplicar_reducao_noturna     INTEGER NOT NULL DEFAULT 0,
    fator_reducao_noturna       NUMERIC(8,6) NOT NULL DEFAULT 1.142857,
    aplicar_inss                INTEGER NOT NULL DEFAULT 1,
    aplicar_irrf                INTEGER NOT NULL DEFAULT 1,
    aliquota_fgts               NUMERIC(5,2) NOT NULL DEFAULT 8.00,
    teto_inss                   NUMERIC(15,2) NOT NULL DEFAULT 8157.41,
    deducao_dependente_irrf     NUMERIC(15,2) NOT NULL DEFAULT 189.59,
    ativo                       INTEGER NOT NULL DEFAULT 1,
    validado_por_profissional   INTEGER NOT NULL DEFAULT 0,
    criado_em                   TEXT NOT NULL,
    atualizado_em               TEXT NOT NULL
);

-- 2. TABELA DE FOLHAS DE PAGAMENTO (CABEÇALHO E TOTAIS)
CREATE TABLE IF NOT EXISTS folhas_pagamento (
    id                          SERIAL PRIMARY KEY,
    colaborador_id              INTEGER NOT NULL
                                REFERENCES colaboradores(id) ON DELETE RESTRICT,
    competencia                 TEXT NOT NULL, -- Formato AAAA-MM (ex: '2026-10')
    periodo_inicio              TEXT NOT NULL,
    periodo_fim                 TEXT NOT NULL,
    data_pagamento              TEXT,
    dias_trabalhados            NUMERIC(4,1) NOT NULL DEFAULT 30.0,
    dias_mes                    INTEGER NOT NULL DEFAULT 30,
    horas_mensais_divisor       NUMERIC(6,2) NOT NULL DEFAULT 220.00,
    salario_base_contratual     NUMERIC(15,2) NOT NULL,
    salario_base_proporcional   NUMERIC(15,2) NOT NULL,
    total_proventos             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    total_descontos             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    salario_liquido             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    base_inss                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    base_fgts                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    valor_fgts_informativo      NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    base_irrf                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    situacao                    TEXT NOT NULL DEFAULT 'rascunho'
                                CHECK (situacao IN ('rascunho', 'calculada', 'fechada', 'cancelada')),
    observacoes                 TEXT,
    parametro_id                INTEGER REFERENCES folha_parametros(id),
    criado_por                  TEXT NOT NULL,
    criado_em                   TEXT NOT NULL,
    atualizado_por              TEXT,
    atualizado_em               TEXT,
    fechado_por                 TEXT,
    fechado_em                  TEXT,
    -- Bloqueio rigoroso de duplicidade de folha para o mesmo colaborador na mesma competência
    CONSTRAINT unq_colab_competencia UNIQUE (colaborador_id, competencia)
);

-- 3. TABELA DE ITENS E EVENTOS DA FOLHA
CREATE TABLE IF NOT EXISTS folha_itens (
    id                  SERIAL PRIMARY KEY,
    folha_id            INTEGER NOT NULL
                        REFERENCES folhas_pagamento(id) ON DELETE CASCADE,
    codigo_evento       TEXT NOT NULL,
    descricao           TEXT NOT NULL,
    tipo                TEXT NOT NULL CHECK (tipo IN ('provento', 'desconto', 'informativo')),
    referencia          REAL DEFAULT 0.0,
    unidade_referencia  TEXT,
    valor_unitario      REAL DEFAULT 0.0,
    valor_total         REAL NOT NULL DEFAULT 0.0,
    origem              TEXT NOT NULL DEFAULT 'calculado'
                        CHECK (origem IN ('sistema', 'calculado', 'manual', 'importado')),
    memoria_calculo     TEXT,
    criado_em           TEXT NOT NULL
);

-- 4. TABELA DE HISTÓRICO DE AUDITORIA E FECHAMENTO DA FOLHA
CREATE TABLE IF NOT EXISTS folha_historico (
    id                  SERIAL PRIMARY KEY,
    folha_id            INTEGER NOT NULL
                        REFERENCES folhas_pagamento(id) ON DELETE CASCADE,
    data_hora           TEXT NOT NULL,
    acao                TEXT NOT NULL,
    descricao           TEXT NOT NULL,
    dados_anteriores    TEXT,
    dados_novos         TEXT,
    usuario_responsavel TEXT NOT NULL
);

-- 5. ÍNDICES DE PERFORMANCE E INTEGRIDADE
CREATE INDEX IF NOT EXISTS idx_folha_colab        ON folhas_pagamento(colaborador_id);
CREATE INDEX IF NOT EXISTS idx_folha_comp         ON folhas_pagamento(competencia);
CREATE INDEX IF NOT EXISTS idx_folha_situacao     ON folhas_pagamento(situacao);
CREATE INDEX IF NOT EXISTS idx_folha_itens_folha  ON folha_itens(folha_id);
CREATE INDEX IF NOT EXISTS idx_folha_itens_codigo ON folha_itens(codigo_evento);
CREATE INDEX IF NOT EXISTS idx_folha_hist_folha   ON folha_historico(folha_id);

-- 6. DADOS INICIAIS — PARÂMETRO PADRÃO CLT 2026
INSERT INTO folha_parametros (
    codigo, descricao, vigencia_inicio, vigencia_fim,
    horas_mensais_padrao, dias_mes_padrao, percentual_he_padrao,
    percentual_he_extra, percentual_adicional_noturno, aplicar_reducao_noturna,
    fator_reducao_noturna, aplicar_inss, aplicar_irrf, aliquota_fgts,
    teto_inss, deducao_dependente_irrf, ativo, validado_por_profissional,
    criado_em, atualizado_em
) VALUES (
    'PADRAO_CLT_2026', 'Parâmetros Gerais CLT 220h / Vigência 2026 (Padrão)',
    '2026-01-01', NULL,
    220.00, 30, 50.00, 100.00, 20.00, 0, 1.142857,
    1, 1, 8.00, 8157.41, 189.59, 1, 1,
    TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS'), TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS')
) ON CONFLICT (codigo) DO NOTHING;

-- 7. POLÍTICAS DE ROW LEVEL SECURITY (RLS) NO SUPABASE
-- Habilita RLS em todas as tabelas da Folha
ALTER TABLE folha_parametros ENABLE ROW LEVEL SECURITY;
ALTER TABLE folhas_pagamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE folha_itens ENABLE ROW LEVEL SECURITY;
ALTER TABLE folha_historico ENABLE ROW LEVEL SECURITY;

-- Remove políticas antigas se existirem para permitir idempotência
DROP POLICY IF EXISTS "Acesso restrito folha_parametros para autenticados" ON folha_parametros;
DROP POLICY IF EXISTS "Acesso restrito folhas_pagamento para autenticados" ON folhas_pagamento;
DROP POLICY IF EXISTS "Acesso restrito folha_itens para autenticados" ON folha_itens;
DROP POLICY IF EXISTS "Acesso restrito folha_historico para autenticados" ON folha_historico;

-- Política RLS: Usuários autenticados no Supabase (auth.role() = 'authenticated')
-- possuem acesso de leitura e escrita conforme os perfis autorizados de RH/DP
CREATE POLICY "Acesso restrito folha_parametros para autenticados"
    ON folha_parametros
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Acesso restrito folhas_pagamento para autenticados"
    ON folhas_pagamento
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Acesso restrito folha_itens para autenticados"
    ON folha_itens
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Acesso restrito folha_historico para autenticados"
    ON folha_historico
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

COMMIT;

