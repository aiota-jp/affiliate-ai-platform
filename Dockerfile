FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py mcp_app.py db.py rakuten.py wordpress.py ./
COPY models/ ./models/
COPY providers/ ./providers/
COPY services/ ./services/
COPY tools/ ./tools/
COPY harness/ ./harness/
COPY sql/ ./sql/

CMD ["python", "server.py"]
