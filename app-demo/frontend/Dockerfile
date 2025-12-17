FROM node:20-alpine

WORKDIR /app

# Copiamo solo i file dei pacchetti per sfruttare la cache
COPY package*.json ./

# Installiamo le dipendenze
RUN npm install

# Copiamo il resto (utile per build standalone, anche se il volume lo coprirà)
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Esponiamo la porta di Vite/SvelteKit
EXPOSE 5173

# COMANDO DI AVVIO (Dev Mode)
# "npm run dev" avvia il server di sviluppo.
# "--" serve a passare argomenti allo script sottostante (Vite).
# "--host" dice a Vite di accettare connessioni dall'esterno del container.
CMD ["npm", "run", "dev", "--", "--host"]