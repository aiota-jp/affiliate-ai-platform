FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py mcp_app.py db.py rakuten.py wordpress.py ./
COPY test_harness.py ./
COPY dify_client.py ./
COPY test_dify_harness.py ./
COPY models/ ./models/
COPY providers/ ./providers/
COPY services/ ./services/
COPY tools/ ./tools/
COPY harness/ ./harness/
COPY sql/ ./sql/

EXPOSE 8000
CMD ["python", "server.py"]
