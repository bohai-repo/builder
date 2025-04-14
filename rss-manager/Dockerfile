FROM base_platfrom
WORKDIR /app/rss-manager

EXPOSE 8000

ENV ADMIN_KEY=admin
ENV TZ=Asia/Shanghai

COPY app /app/rss-manager/
ADD docker-entrypoint.sh /app/rss-manager/
RUN npm install --production

CMD [ "/bin/sh", "docker-entrypoint.sh" ]