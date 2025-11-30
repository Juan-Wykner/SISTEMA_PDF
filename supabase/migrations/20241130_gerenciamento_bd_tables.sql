-- Tabelas para o sistema de gerenciamento BD
-- Baseado na documentação técnica

-- Tabela Contas
CREATE TABLE IF NOT EXISTS contas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('banco', 'caixa')),
    saldo_inicial DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(10) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela Pessoas
CREATE TABLE IF NOT EXISTS pessoas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    cpf_cnpj VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    tipo VARCHAR(20) CHECK (tipo IN ('fornecedor', 'cliente', 'faturado')),
    status VARCHAR(10) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
    conta_id UUID REFERENCES contas(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela Classificacao
CREATE TABLE IF NOT EXISTS classificacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('receita', 'despesa')),
    status VARCHAR(10) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_contas_status ON contas(status);
CREATE INDEX IF NOT EXISTS idx_contas_codigo ON contas(codigo);
CREATE INDEX IF NOT EXISTS idx_contas_tipo ON contas(tipo);

CREATE INDEX IF NOT EXISTS idx_pessoas_status ON pessoas(status);
CREATE INDEX IF NOT EXISTS idx_pessoas_tipo ON pessoas(tipo);
CREATE INDEX IF NOT EXISTS idx_pessoas_codigo ON pessoas(codigo);
CREATE INDEX IF NOT EXISTS idx_pessoas_cpf_cnpj ON pessoas(cpf_cnpj);

CREATE INDEX IF NOT EXISTS idx_classificacao_status ON classificacao(status);
CREATE INDEX IF NOT EXISTS idx_classificacao_tipo ON classificacao(tipo);
CREATE INDEX IF NOT EXISTS idx_classificacao_codigo ON classificacao(codigo);

-- Permissões básicas
GRANT SELECT ON contas TO anon;
GRANT ALL PRIVILEGES ON contas TO authenticated;

GRANT SELECT ON pessoas TO anon;
GRANT ALL PRIVILEGES ON pessoas TO authenticated;

GRANT SELECT ON classificacao TO anon;
GRANT ALL PRIVILEGES ON classificacao TO authenticated;