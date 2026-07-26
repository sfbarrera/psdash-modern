# Build multi-stage: primero compila la SPA de React, luego la sirve con Nginx.

# --- Etapa 1: build ---
FROM node:20-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# --- Etapa 2: runtime ---
FROM nginx:1.27-alpine
# Configuracion que sirve la SPA y hace de reverse proxy hacia el backend.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
