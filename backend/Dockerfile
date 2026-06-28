FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/collected_static

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_project.wsgi"]
