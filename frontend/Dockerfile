FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npx vite build

FROM alpine:3.19

COPY --from=build /app/dist /dist

CMD ["sh", "-c", "cp -r /dist/* /app/dist/ && tail -f /dev/null"]
