FROM php:latest

WORKDIR /var/www/html

RUN export ORDER_API_URL=http://localhost:3002

COPY . .

EXPOSE 3000

CMD ["php", "-S", "0.0.0.0:3000"]
