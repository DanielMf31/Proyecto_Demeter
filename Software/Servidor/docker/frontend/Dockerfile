FROM nginx:alpine

# Copy static web files
COPY Software/Servidor/Frontend/Web/ /usr/share/nginx/html/

# Copy custom nginx configuration
COPY Software/Servidor/Backend/Nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
