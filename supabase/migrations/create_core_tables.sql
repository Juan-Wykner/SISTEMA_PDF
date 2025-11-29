-- Core tables for SISTEMA_PDF (PostgreSQL / Supabase)
-- Safe-guards: create tables if not exists, align with Django models

create table if not exists pessoas (
  id bigserial primary key,
  tipo varchar(20) not null,
  razao_social varchar(200) not null,
  nome_fantasia varchar(200),
  cnpj_cpf varchar(20) unique,
  telefone varchar(20),
  email varchar(254),
  endereco text,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint pessoas_tipo_chk check (tipo in ('CLIENTE','FORNECEDOR','FATURADO'))
);

create table if not exists classificacao (
  id bigserial primary key,
  tipo varchar(20) not null,
  descricao varchar(100) not null,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  constraint classificacao_tipo_chk check (tipo in ('RECEITA','DESPESA'))
);

create table if not exists movimentocontas (
  id bigserial primary key,
  tipo varchar(10) not null,
  pessoa_id bigint not null references pessoas(id) on delete restrict,
  descricao text not null,
  valor_total numeric(10,2) not null check (valor_total >= 0),
  quantidade_parcelas integer not null default 1,
  data_emissao date not null,
  status varchar(20) not null default 'ABERTO',
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  constraint movimentocontas_tipo_chk check (tipo in ('PAGAR','RECEBER')),
  constraint movimentocontas_status_chk check (status in ('ABERTO','PAGO','CANCELADO'))
);

create table if not exists parcelacontas (
  id bigserial primary key,
  movimento_id bigint not null references movimentocontas(id) on delete cascade,
  numero_parcela integer not null,
  valor_parcela numeric(10,2) not null,
  data_vencimento date not null,
  data_pagamento date,
  status varchar(20) not null default 'ABERTO',
  identificacao_unica varchar(50) not null unique,
  created_at timestamptz not null default now(),
  constraint parcelacontas_status_chk check (status in ('ABERTO','PAGO'))
);

create table if not exists movimento_classificacao (
  id bigserial primary key,
  movimento_id bigint not null references movimentocontas(id) on delete cascade,
  classificacao_id bigint not null references classificacao(id) on delete restrict,
  valor_classificado numeric(10,2) not null
);

-- helpful indexes
create index if not exists pessoas_cnpj_tipo_idx on pessoas (cnpj_cpf, tipo);
create index if not exists classificacao_desc_tipo_idx on classificacao (lower(descricao), tipo);
create index if not exists movcontas_pessoa_idx on movimentocontas (pessoa_id);
create index if not exists parcelas_mov_idx on parcelacontas (movimento_id, numero_parcela);
create index if not exists movclass_mov_idx on movimento_classificacao (movimento_id);

