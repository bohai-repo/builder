FROM alpine:3.8
LABEL maintainer="itan90.cn"

ENV VERSION version_key
ENV TZ=Asia/Shanghai
WORKDIR /
ADD entrypoint.sh entrypoint.sh
RUN apk add --no-cache tzdata \
	&& apk add -U curl grep \
    && ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && chmod +x entrypoint.sh

RUN if [ "$(uname -m)" = "x86_64" ]; then export PLATFORM=amd64 ; else if [ "$(uname -m)" = "aarch64" ]; then export PLATFORM=arm64 ; fi fi \
	&& wget --no-check-certificate https://github.com/fatedier/frp/releases/download/v${VERSION}/frp_${VERSION}_linux_${PLATFORM}.tar.gz \
	&& tar xzf frp_${VERSION}_linux_${PLATFORM}.tar.gz \
	&& cd frp_${VERSION}_linux_${PLATFORM} \
	&& mkdir -p /app/frpc \
	&& mv frpc /app/frpc \
	&& cd .. \
	&& rm -rf *.tar.gz frp_${VERSION}_linux_${PLATFORM}

CMD /entrypoint.sh
