FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt
COPY hello ./hello
RUN useradd --system --uid 10001 hello
USER hello
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "hello.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
