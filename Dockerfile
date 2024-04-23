FROM python:3.12-slim

LABEL maintainer="Abhiram B.S.N."

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install-deps && playwright install chromium
COPY ./src .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]