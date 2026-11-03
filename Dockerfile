FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx

COPY server.py /app/server.py
COPY home_redirect.py /app/home_redirect.py

EXPOSE 3040

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3040"]
