FROM python:3.12-slim
WORKDIR /workspace
COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt
COPY backend/app /workspace/backend/app
COPY cases /workspace/cases
ENV PYTHONPATH=/workspace/backend
ENV DD_DB_PATH=/workspace/data/detective.db
RUN mkdir -p /workspace/data
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
