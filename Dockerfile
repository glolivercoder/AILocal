FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements_langchain.txt .
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_langchain.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p rag_data config logs

# Expor porta
EXPOSE 8080

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando de inicialização
CMD ["python", "ai_agent_gui.py"] 