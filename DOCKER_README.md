# SISTEMA_PDF - Configuração Docker Completa

Esta pasta contém todos os arquivos necessários para criar um container Docker completo do sistema SISTEMA_PDF.

## 📋 Arquivos Inclusos

- `Dockerfile` - Configuração do container Docker
- `docker-entrypoint.sh` - Script de inicialização
- `requirements.txt` - Dependências Python
- `build_docker_complete.bat` - Script Windows para build
- `build_docker_complete.sh` - Script Linux/Mac para build
- Todos os arquivos do projeto Django

## 🚀 Como Criar o Container

### Opção 1: Usar o Script (Recomendado)

**Windows:**
```cmd
build_docker_complete.bat
```

**Linux/Mac:**
```bash
chmod +x build_docker_complete.sh
./build_docker_complete.sh
```

### Opção 2: Manual

1. **Build da imagem Docker:**
   ```bash
   docker build -t sistema_pdf:latest .
   ```

2. **Criar container:**
   ```bash
   docker create --name sistema_pdf sistema_pdf:latest
   ```

3. **Exportar container:**
   ```bash
   docker export sistema_pdf > sistema_pdf_container.tar
   ```

4. **Comprimir:**
   ```bash
   gzip -9 sistema_pdf_container.tar
   ```

## 📦 Arquivo Final

O script criará o arquivo: `sistema_pdf_container.tar.gz`

Este arquivo contém TODO o sistema pronto para ser importado em qualquer máquina com Docker.

## 🔧 Como Importar e Executar

1. **Importar o container:**
   ```bash
   docker import sistema_pdf_container.tar.gz sistema_pdf:imported
   ```

2. **Executar o container:**
   ```bash
   docker run -d -p 8000:8000 --name sistema_pdf sistema_pdf:imported
   ```

3. **Acessar o sistema:**
   Abrir navegador em: http://localhost:8000

## 🔑 Credenciais Padrão

- **Usuário:** admin
- **Senha:** admin123

## 📁 Estrutura do Container

O container inclui:
- ✅ Django 4.2.7
- ✅ Python 3.11
- ✅ Todas as dependências
- ✅ Banco de dados SQLite
- ✅ Arquivos estáticos
- ✅ Templates e views
- ✅ Agentes de IA
- ✅ Todos os arquivos do projeto

## 🐳 Comandos Úteis

**Ver containers em execução:**
```bash
docker ps
```

**Parar container:**
```bash
docker stop sistema_pdf
```

**Remover container:**
```bash
docker rm sistema_pdf
```

**Ver logs:**
```bash
docker logs sistema_pdf
```

## 📞 Suporte

O container está completo e pronto para uso. Todos os arquivos do projeto SISTEMA_PDF estão incluídos.