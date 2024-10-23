```shell
docker build -t remote-download-service:v1 .
docker rm -f remote-download-service
docker run -itd --name remote-download-service \
-p 8080:8080 \
-e USE_HTTPS=false \
-e SERVER_NAME=init.ac \
-e PASSWORD=123456 \
-v /data/remote-download-service/data:/app/remote-download-service/files \
remote-download-service:v1
```