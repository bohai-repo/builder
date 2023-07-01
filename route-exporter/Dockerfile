FROM python:3.8-slim-buster
WORKDIR /app/

# 设备IP
ENV route_ip '192.168.60.1'
# 设备密码 (通过登录接口获取)
ENV password 'rVm/+oNskbZ7lwkTpMITzA=='

RUN pip3 install --no-cache-dir requests prometheus_client 
ADD main.py /app/

CMD ["python3", "/app/main.py"]