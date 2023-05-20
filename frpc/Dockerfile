FROM alpine:3.8
LABEL maintainer="https://github.com/yaobohai/builder/tree/develop/frpc"

ENV VERSION version_key
ENV TZ=Asia/Shanghai

WORKDIR /

ADD frp_version_key.tar.gz /
ADD entrypoint.sh entrypoint.sh

RUN apk add --no-cache tzdata \
    && apk add -U curl grep \
    && ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && chmod +x entrypoint.sh

RUN cd frp_${VERSION} \
    && mkdir -p /app/frpc \
    && mv frpc /app/frpc \
    && cd .. \
    && rm -rf /frp_${VERSION}

CMD /entrypoint.sh
