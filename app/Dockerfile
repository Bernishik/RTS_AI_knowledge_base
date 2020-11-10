FROM python:3.8-buster
COPY requirements.txt .
RUN pip3 install -r requirements.txt
ADD . /app
WORKDIR /app
EXPOSE 5000
#ENTRYPOINT ["python3"]
#CMD ["app.py"]
