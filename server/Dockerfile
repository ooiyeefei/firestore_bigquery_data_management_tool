# 1 
FROM python:3.13.0a3

# 2
COPY src/ /app
WORKDIR /app
RUN pip install -r requirements.txt

# 3
ENV PORT 8080

# 4
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app