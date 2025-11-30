-- Tabelas para o sistema de gerenciamento BD
-- Baseado na documentação técnica

-- Habilitar RLS nas tabelas existentes
ALTER TABLE contas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pessoas ENABLE ROW LEVEL SECURITY;
ALTER TABLE classificacao ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança
-- Políticas para contas
CREATE POLICY "Usuários autenticados podem ver contas ativas" ON contas
    FOR SELECT USING (status = 'ativo');

CREATE POLICY "Admin pode gerenciar todas as contas" ON contas
    FOR ALL USING (auth.role() = 'authenticated');

-- Políticas para pessoas
CREATE POLICY "Usuários autenticados podem ver pessoas ativas" ON pessoas
    FOR SELECT USING (status = 'ativo');

CREATE POLICY "Admin pode gerenciar todas as pessoas" ON pessoas
    FOR ALL USING (auth.role() = 'authenticated');

-- Políticas para classificação
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