# frontend/Dockerfile

# Schimbăm la versiunea 20-alpine (LTS) cum cere react-router-dom
FROM node:20-alpine

WORKDIR /app

# Copiem fișierele de configurare yarn
COPY package.json yarn.lock ./

# Instalăm folosind yarn
RUN yarn install

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]