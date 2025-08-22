FROM python:3.9-slim

WORKDIR /app

ADD main.py /app
ADD static /app/static/

EXPOSE 8872
ENV wrest_url=http://127.0.0.1:7600

RUN pip3 install --no-cache-dir Flask requests openai dashscope \
    && mkdir -p /app/data/
CMD ["python3", "main.py"]