FROM python:3.11-slim
          
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ls -la

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

RUN python --version

CMD ["python", "server.py"]