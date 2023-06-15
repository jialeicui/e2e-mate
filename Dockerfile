# python3.11 env
FROM python:3.11.4-alpine3.18

WORKDIR /app
COPY main.py app.py
COPY requirements.txt requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# run the application
CMD ["python", "app.py"]
