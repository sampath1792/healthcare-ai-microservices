# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# Final stage
FROM python:3.13-slim
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

# Add non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Start app
CMD ["uvicorn", "worker:app", "--host", "0.0.0.0", "--port", "8080"]



