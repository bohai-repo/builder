FROM node:22-alpine AS builder
ADD . /kubedoor-web/
WORKDIR /kubedoor-web
# RUN npm install -g pnpm && pnpm install && npm run build
RUN npm install -g pnpm --registry=https://registry.npmmirror.com && \
    pnpm install --registry=https://registry.npmmirror.com && \
    npm run build
# FROM registry.cn-shenzhen.aliyuncs.com/starsl/nginx:1.24.0-alpine
FROM registry.cn-shenzhen.aliyuncs.com/starsl/nginx-ldap:1.27-alpine
WORKDIR /www
COPY --from=builder /kubedoor-web/dist dist/
