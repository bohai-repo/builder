FROM python:3.11-alpine
ADD . /
WORKDIR /
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --no-cache-dir
EXPOSE 8000
CMD ["python3", "/kubedoor-mcp.py"]
