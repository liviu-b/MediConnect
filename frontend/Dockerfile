# frontend/Dockerfile

FROM node:20-alpine

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

# Ensure CRA dev server binds to all interfaces inside container
ENV HOST=0.0.0.0 PORT=3000

EXPOSE 3000

CMD ["yarn", "start"]