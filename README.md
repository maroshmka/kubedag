# kubedag

Write DAGs in Airflow (or other workflow manager - argo, kubeflow etc.)
Read them, generate k8s Cronjobs from firsts tasks.
k8s will do the scheduling, kubedag will trigger next tasks or wait if needed.

# warning

very wip, ugly code, PoC-ing

# local setup

- minikube start
- k run --image postgres --env="POSTGRES_USER=airflow" --env="POSTGRES_PASSWORD=airflow" --env="POSTGRES_DB=airflow" --port 5432 airflow-db

# todo - get rid of db? or at least write full manifest 
- k apply -f postgres-service.yaml 

# todo - rm after finish
- k run --image apache/airflow:2.0.0 --env="AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@airflow-db/airflow" airflow-ctl airflow db init
- sh run.sh

# todo

- meet dependencies (A->C, B->C)
- sensors?
- UI (logs?)
- make CLI
- separate example from the kubedag

# problems

- dind? needed?
- execution date ? how to setup?
- k8s resoureces already exists when redeployed ?
- airflow db?
