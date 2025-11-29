#!/bin/bash

# Script para criar container Docker completo do SISTEMA_PDF
# e compactar em um arquivo único

echo "🚀 Criando container Docker do SISTEMA_PDF..."

# Parar containers anteriores se existirem
docker-compose down 2>/dev/null || true
docker stop sistema_pdf 2>/dev/null || true
docker rm sistema_pdf 2>/dev/null || true

# Build do container Docker
echo "📦 Buildando imagem Docker..."
docker build -t sistema_pdf:latest .

# Criar container a partir da imagem
echo "🐳 Criando container..."
docker create --name sistema_pdf sistema_pdf:latest

# Exportar container completo
echo "💾 Exportando container..."
docker export sistema_pdf > sistema_pdf_container.tar

# Comprimir com gzip
echo "🗜️  Comprimindo arquivo..."
gzip -9 sistema_pdf_container.tar

# Limpar container temporário
docker rm sistema_pdf

# Criar arquivo com instruções
cat > INSTRUCOES_DOCKER.txt << 'EOF'
🐳 SISTEMA_PDF - Container Docker Completo

ARQUIVOS CRIADOS:
- sistema_pdf_container.tar.gz (Container completo comprimido)

COMO IMPORTAR E EXECUTAR:

1. Importar o container:
   docker import sistema_pdf_container.tar.gz sistema_pdf:imported

2. Executar o container:
   docker run -d -p 8000:8000 --name sistema_pdf sistema_pdf:imported

3. Acessar a aplicação:
   http://localhost:8000

INFORMAÇÕES:
- Usuário admin: admin/admin123
- Banco de dados: SQLite (já incluso)
- Todos os arquivos estão dentro do container

EOF

echo "✅ Container Docker criado com sucesso!"
echo "📁 Arquivos gerados:"
ls -lh sistema_pdf_container.tar.gz INSTRUCOES_DOCKER.txt 2>/dev/null || dir sistema_pdf_container.tar.gz INSTRUCOES_DOCKER.txt

echo ""
echo "🎯 Para executar:"
echo "   docker import sistema_pdf_container.tar.gz sistema_pdf:imported"
echo "   docker run -d -p 8000:8000 --name sistema_pdf sistema_pdf:imported"