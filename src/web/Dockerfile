FROM nginx:alpine

# Copiar arquivos estáticos para o diretório do Nginx
COPY ./pages/ /usr/share/nginx/html/
COPY ./css/ /usr/share/nginx/html/css/
COPY ./js/ /usr/share/nginx/html/js/
COPY ./assets/ /usr/share/nginx/html/assets/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
