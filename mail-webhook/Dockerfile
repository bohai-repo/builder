FROM python:3.9-slim

EXPOSE 5600
WORKDIR /app
ADD main.py /app
RUN pip3 install --no-cache-dir Flask requests
CMD ["python3", "main.py"]