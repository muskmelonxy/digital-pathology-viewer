FROM node:18-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY public ./public
COPY src ./src

RUN npm run build
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "tcp://0.0.0.0:3000"]
