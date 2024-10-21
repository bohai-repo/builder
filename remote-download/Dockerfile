FROM node:16.0.0

WORKDIR /app

COPY app /app
RUN npm install

CMD [ "/bin/sh", "/app/startup.sh" ]
HEALTHCHECK --interval=1m --timeout=10s \
  CMD curl -sf http://127.0.0.1:8080/api/files || exit 1