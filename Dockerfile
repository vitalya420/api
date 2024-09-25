FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["sanic", "app:app", "--host", "0.0.0.0", "--port", "8080"]