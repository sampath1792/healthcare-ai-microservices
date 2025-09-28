# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

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

EXPOSE 8080

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

