FROM python:3.10-slim

ENV HOME /app
ENV PYTHONPATH ${HOME}

RUN apt-get update && apt-get upgrade -y && apt-get install postgresql-client -y

WORKDIR ${HOME}/

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
