

# Étape 1 : Construction (Build)
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Étape 2 : Exécution (Runtime)
FROM node:20-alpine
WORKDIR /app

# On récupère le nécessaire du build précédent
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/src ./src
# 🟢 CORRECTIF : Copier le dossier public contenant l'interface utilisateur (UI)
COPY --from=build /app/public ./public

# --- SÉCURITÉ ---
USER node
EXPOSE 3000

CMD ["node", "src/app.js"]

