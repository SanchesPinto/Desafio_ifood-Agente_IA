# Usa uma imagem leve do Python 3.11
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
# (Adicionei o curl para healthchecks, opcional mas útil)
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y curl

# Copia todo o resto do código para dentro do container
COPY . .

# Comando padrão (será sobrescrito no docker-compose, mas deixamos um default)
CMD ["python", "middleware.py"]