FROM python:3.7-alpine
WORKDIR /
RUN pip3 install -i requests
ADD consul_deregister.py /
CMD ["python3", "consul_deregister.py"]