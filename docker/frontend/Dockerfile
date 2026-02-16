FROM nginx:alpine

# Copy static files
COPY ./web /usr/share/nginx/html

# Custom nginx config to proxy /api to the backend
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
