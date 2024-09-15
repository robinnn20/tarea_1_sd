FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install numpy
RUN pip install matplotlib
RUN pip install flask
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
