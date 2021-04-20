FROM apache/airflow:2.0.0

RUN mkdir ./kubedag
WORKDIR ./kubedag

COPY ./kubedag/* ./
COPY ./templates/* ./templates/
