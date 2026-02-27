FROM node:22-alpine AS builder
WORKDIR /app

# Install dependencies
COPY Software/Servidor/Frontend/Demeter-React/package*.json ./
RUN npm install

# Copy sources
COPY Software/Servidor/Frontend/Demeter-React ./

# Build the app using Vite
RUN npm run build

# ── Stage 2: Serve with Nginx ──────────────────────────────────────────────
FROM nginx:alpine

# Static files from React build
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config
COPY Software/Servidor/Backend/Nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
