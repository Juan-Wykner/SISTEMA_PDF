@echo off
echo 🚀 Criando container Docker do SISTEMA_PDF...

# Parar containers anteriores se existirem
docker-compose down 2>nul
docker stop sistema_pdf 2>nul
docker rm sistema_pdf 2>nul

# Build do container Docker
echo 📦 Buildando imagem Docker...
docker build -t sistema_pdf:latest .

# Criar container a partir da imagem
echo 🐳 Criando container...
docker create --name sistema_pdf sistema_pdf:latest

# Exportar container completo
echo 💾 Exportando container...
docker export sistema_pdf > sistema_pdf_container.tar

# Comprimir com gzip
echo 🗜️  Comprimindo arquivo...
gzip -9 sistema_pdf_container.tar

# Limpar container temporário
docker rm sistema_pdf

# Criar arquivo com instruções
echo 📝 Criando instruções...
(
echo 🐳 SISTEMA_PDF - Container Docker Completo
echo.
echo ARQUIVOS CRIADOS:
echo - sistema_pdf_container.tar.gz ^(Container completo comprimido^)
echo.
echo COMO IMPORTAR E EXECUTAR:
echo.
echo 1. Importar o container:
echo    docker import sistema_pdf_container.tar.gz sistema_pdf:imported
echo.
echo 2. Executar o container:
echo    docker run -d -p 8000:8000 --name sistema_pdf sistema_pdf:imported
echo.
echo 3. Acessar a aplicação:
echo    http://localhost:8000
echo.
echo INFORMAÇÕES:
echo - Usuário admin: admin/admin123
echo - Banco de dados: SQLite ^(já incluso^)
echo - Todos os arquivos estão dentro do container
echo.
) > INSTRUCOES_DOCKER.txt

echo ✅ Container Docker criado com sucesso!
echo 📁 Arquivos gerados:
dir sistema_pdf_container.tar.gz INSTRUCOES_DOCKER.txt 2>nul

echo.
echo 🎯 Para executar:
echo    docker import sistema_pdf_container.tar.gz sistema_pdf:imported
echo    docker run -d -p 8000:8000 --name sistema_pdf sistema_pdf:imported
pause