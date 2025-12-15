FROM python:3.10-slim

WORKDIR /app

# Installa dipendenze di sistema (necessarie per psycopg2 o altre lib)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# In sviluppo, il Volume del docker-compose "nasconderà" questi file 
# sostituendoli con quelli locali in tempo reale
COPY . .

# Dev server con hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]