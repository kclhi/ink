FROM node:16-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY proxy/nginx.conf /etc/nginx/nginx.conf
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/nginx.conf
COPY proxy/certs/ink.crt /etc/nginx/ssl/ink.crt
COPY proxy/certs/ink.key /etc/nginx/ssl/ink.key
RUN chmod 644 /etc/nginx/ssl/ink.crt /etc/nginx/ssl/ink.key
COPY --from=build /app/build /usr/share/nginx/html/ink
RUN chown -R nginx:nginx /usr/share/nginx/html 
RUN chmod -R 755 /usr/share/nginx/html
RUN touch /var/run/nginx.pid
RUN chown -R nginx:nginx /var/run/nginx.pid
EXPOSE 80
EXPOSE 443
USER nginx
CMD ["nginx", "-g", "daemon off;"]