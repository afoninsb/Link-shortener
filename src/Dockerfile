FROM python:3.10-slim

ENV HOME /app
ENV PYTHONPATH ${HOME}

WORKDIR ${HOME}/

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
