# mcp/Dockerfile
FROM python:3.12-slim

# 文字化け対策: 標準入出力・ログをUTF-8に固定する
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py mcp_app.py db.py rakuten.py wordpress.py ./
COPY tools/ ./tools/

# Streamable HTTP の待ち受けポート
EXPOSE 8000

CMD ["python", "server.py"]