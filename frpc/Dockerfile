FROM alpine:3.8
LABEL maintainer="https://github.com/yaobohai/builder/tree/develop/frpc"

ENV TZ=Asia/Shanghai
WORKDIR /
ADD entrypoint.sh entrypoint.sh
RUN apk add --no-cache tzdata \
	&& apk add -U curl grep \
    && ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && chmod +x entrypoint.sh

RUN tar xzf frp_${VERSION}.tar.gz \
	&& cd frp_${VERSION} \
	&& mkdir -p /app/frpc \
	&& mv frpc /app/frpc \
	&& cd .. \
	&& rm -rf *.tar.gz

CMD /entrypoint.sh