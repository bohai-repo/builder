FROM base_platfrom
WORKDIR /app/remote-download-service

EXPOSE 80
EXPOSE 8080

ENV PASSWORD=123456
ENV USE_HTTPS=false
ENV SHOW_PASSWD=true
ENV SERVER_NAME=localhost

COPY web /app/web/
COPY app /app/remote-download-service/
COPY ./nginx.conf /etc/nginx/nginx.conf

RUN npm install --production && rm -rf /app/nginx/html \
    && mkdir /app/remote-download-service/logs/

CMD [ "/bin/sh", "startup.sh" ]