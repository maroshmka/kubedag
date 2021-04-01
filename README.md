# kubedag

Schedule your DAGs (Directed Acyclic Graphs) solely on kubernetes cluster. Using kubernetes 
scheduler, its flexible yet powerful api, to schedule your workflows.

Write DAGs in Airflow (or other workflow manager - argo, kubeflow etc.)

Kubedag will read them, generate k8s Cronjobs as root tasks.

k8s will do the scheduling, kubedag will trigger dependant tasks or wait if needed.

# warning

very wip, ugly code, PoC-ing

# local setup

- minikube start

# todo - run airflowdb for now
# todo - maybe at least manifest would be nice
- k run --image postgres --env="POSTGRES_USER=airflow" --env="POSTGRES_PASSWORD=airflow" --env="POSTGRES_DB=airflow" --port 5432 airflow-db
- k apply -f postgres-service.yaml
- k run --image apache/airflow:2.0.0 --env="AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@airflow-db/airflow" airflow-ctl airflow db init
 

# then run
- sh run.sh

# todo

- meet dependencies (A->C, B->C)
    - almost done? check complete + trigger
- sensors?
    - should work as normal tasks.. ?
- UI (logs?)
  - from k8s stdout logs (write structlog)
- make CLI
- separate example from the lib, now its merged
- cleanup

# problems

- dind? needed?
- execution date ? how to setup?
- k8s resoureces already exists when redeployed ? cleanup things
- airflow db? 
