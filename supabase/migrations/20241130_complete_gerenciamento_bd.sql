-- Tabelas para o sistema de gerenciamento BD - Versão completa
-- Baseado na documentação técnica

-- Criar tabela Contas
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

-- Criar tabela Pessoas
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

-- Criar tabela Classificacao
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

-- Habilitar RLS
ALTER TABLE contas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pessoas ENABLE ROW LEVEL SECURITY;
ALTER TABLE classificacao ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança
CREATE POLICY "Usuários autenticados podem ver contas ativas" ON contas
    FOR SELECT USING (status = 'ativo');

CREATE POLICY "Admin pode gerenciar todas as contas" ON contas
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Usuários autenticados podem ver pessoas ativas" ON pessoas
    FOR SELECT USING (status = 'ativo');

CREATE POLICY "Admin pode gerenciar todas as pessoas" ON pessoas
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Usuários autenticados podem ver classificações ativas" ON classificacao
    FOR SELECT USING (status = 'ativo');

CREATE POLICY "Admin pode gerenciar todas as classificações" ON classificacao
    FOR ALL USING (auth.role() = 'authenticated');

-- Inserir dados de teste
INSERT INTO contas (codigo, nome, tipo, saldo_inicial, status) VALUES
('C001', 'Banco do Brasil', 'banco', 15000.00, 'ativo'),
('C002', 'Caixa Interna', 'caixa', 5000.00, 'ativo'),
('C003', 'Santander', 'banco', 25000.00, 'ativo');

INSERT INTO pessoas (codigo, nome, cpf_cnpj, email, telefone, tipo, status) VALUES
('P001', 'João Silva', '12345678901', 'joao@email.com', '11999999999', 'cliente', 'ativo'),
('P002', 'Maria Santos', '98765432100', 'maria@email.com', '11888888888', 'fornecedor', 'ativo'),
('P003', 'Empresa ABC Ltda', '11222333000144', 'contato@abc.com', '1133333333', 'faturado', 'ativo');

INSERT INTO classificacao (codigo, nome, tipo, status) VALUES
('CL001', 'Vendas de Produtos', 'receita', 'ativo'),
('CL002', 'Serviços Prestados', 'receita', 'ativo'),
('CL003', 'Compra de Materiais', 'despesa', 'ativo');