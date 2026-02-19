FROM node:22-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package.json .
RUN npm install

# Copy sources
COPY tsconfig.json .
COPY Software/Servidor/Frontend/Web/src ./Software/Servidor/Frontend/Web/src

# Build
RUN npm run build

# ── Stage 2: Serve with Nginx ──────────────────────────────────────────────
FROM nginx:alpine

# Static files
COPY --from=builder /app/Software/Servidor/Frontend/Web/dist/ /usr/share/nginx/html/dist/
COPY Software/Servidor/Frontend/Web/index.html /usr/share/nginx/html/
COPY Software/Servidor/Frontend/Web/css /usr/share/nginx/html/css
# Optional: Copy assets if they exist
# COPY Software/Servidor/Frontend/Web/assets /usr/share/nginx/html/assets

# Nginx config
COPY Software/Servidor/Backend/Nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
