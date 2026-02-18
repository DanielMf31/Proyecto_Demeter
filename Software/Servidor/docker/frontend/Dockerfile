FROM nginx:alpine

# Copy static web files
COPY Software/Servidor/Frontend/Web/ /usr/share/nginx/html/

# Copy custom nginx configuration (if exists, otherwise default is fine for simple static)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
