FROM registry.cn-hangzhou.aliyuncs.com/bohai_repo/remote_download:v1.0
RUN yum -y install epel-release \
    &&  yum -y install s3fs-fuse \
    &&  yum remove epel-release -y \
    &&  rm -rf /var/cache/ \
    &&  rm -rf /var/lib/rpm
ADD  startup.sh /app/remote_download/startup.sh
ADD index.html /app/www/index.html
HEALTHCHECK --interval=30s --timeout=15s \
  CMD curl -sf http://127.0.0.1/api/files || exit 1