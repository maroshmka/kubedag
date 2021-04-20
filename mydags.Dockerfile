FROM kubedag-runner:latest

# todo - mount as volume
COPY dags /opt/airflow/dags
