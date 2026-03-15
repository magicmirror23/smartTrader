# ---- Stage 1: Build Angular frontend ----
    FROM node:22-alpine AS frontend-build
    WORKDIR /app/frontend
    COPY frontend/package.json frontend/package-lock.json* ./
    RUN npm ci --no-audit --no-fund 2>/dev/null || npm install --no-audit --no-fund
    COPY frontend/ ./
    RUN npx ng build --configuration production
    
    # ---- Stage 2: Python backend + serve frontend ----
    FROM python:3.13-slim
    
    WORKDIR /app
    
    # Install system deps needed for lightgbm/xgboost compilation
    RUN apt-get update && apt-get install -y --no-install-recommends \
        curl libgomp1 && rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY backend/ ./backend/
    COPY models/registry.json ./models/registry.json
    COPY scripts/ ./scripts/

    COPY storage/raw/ ./storage/raw/
    
    # Copy built Angular files into backend static directory
    COPY --from=frontend-build /app/frontend/dist/stocktrader-frontend/browser ./static
    
    EXPOSE 8000
    
    CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]