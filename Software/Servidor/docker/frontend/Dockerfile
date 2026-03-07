FROM node:22-alpine AS builder
WORKDIR /app

# Enable injection of API URLs at build time
ARG VITE_API_URL
ARG VITE_WS_URL
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}

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
