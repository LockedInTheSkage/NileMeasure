FROM python:3.10-slim

WORKDIR /app
COPY main.py ./
COPY config/ ./config/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir nats-py

CMD ["python", "main.py"]
