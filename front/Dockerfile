# Dockerfile pour Nuxt 3 (Frontend)

# ========== Stage 1: Build ==========
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production --ignore-scripts

# Copier le code source
COPY . .

# Build de production
RUN npm run build

# ========== Stage 2: Production ==========
FROM node:20-alpine

WORKDIR /app

# Copier les fichiers buildés
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/package*.json /app/

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
