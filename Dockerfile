# Étape 1 : Construction (Build)
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
# Installation de toutes les dépendances pour le build
RUN npm install
COPY . .

# Étape 2 : Exécution (Runtime)
FROM node:20-alpine
WORKDIR /app

# On ne récupère que le nécessaire du build précédent
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/src ./src

# --- SÉCURITÉ ---
# 1. On utilise un utilisateur non-privilégié (node) au lieu de root
USER node

# 2. On expose le port
EXPOSE 3000

# 3. Utilisation de node directement au lieu de npm (plus léger et gère mieux les signaux OS)
CMD ["node", "src/app.js"]