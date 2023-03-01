FROM python:3.9-slim-buster

WORKDIR /app 

copy metrics.py requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

RUN python3 -m pip install psutil --find-links=https://ddelange.github.io/psutil/
