FROM node:20

WORKDIR /app

COPY . .
RUN npm ci

EXPOSE 3001

CMD ["npm", "run", "start"]
