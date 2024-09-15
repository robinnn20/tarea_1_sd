FROM python:3.9-slim
WORKDIR /app

COPY . /app
RUN apt-get update && apt-get install -y dnsutils
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
