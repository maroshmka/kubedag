FROM apache/airflow:2.0.0

RUN mkdir ./app

COPY run.py ./app/run.py
