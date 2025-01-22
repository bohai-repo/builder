FROM python:3.9-slim

WORKDIR /app

ADD main.py /app


EXPOSE 8872
ENV wrest_url=http://127.0.0.1:7600

RUN pip install --no-cache-dir Flask requests openai sqlite3 \
    && mkdir -p /app/data/
CMD ["python3", "main.py"]