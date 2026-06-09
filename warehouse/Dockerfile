FROM python:3.11-slim

WORKDIR /app

COPY requirements-warehouse.txt .
RUN pip install --no-cache-dir -r requirements-warehouse.txt

COPY warehouse/ ./warehouse/
COPY warehouse/dagster/workspace.yaml ./workspace.yaml

ENV PYTHONPATH=/app/warehouse

CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000", "-w", "workspace.yaml"]
