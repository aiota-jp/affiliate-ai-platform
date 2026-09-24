FROM python:3.12-slim

ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py mcp_app.py db.py rakuten.py wordpress.py ./
COPY models/ ./models/
COPY providers/ ./providers/
COPY services/ ./services/
COPY tools/ ./tools/

EXPOSE 8000

CMD ["python", "server.py"]
