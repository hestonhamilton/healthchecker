FROM python:3.9-slim

WORKDIR /app

COPY status_checker.py /app/status_checker.py

RUN apt-get update && \
    apt-get install -y libffi-dev libssl-dev && \
    pip install requests prometheus_client python-kasa

CMD ["python", "status_checker.py"]

