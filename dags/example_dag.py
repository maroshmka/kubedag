from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2020, 7, 25),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("tutorial", default_args=default_args, schedule_interval=timedelta(minutes=5))

# example of getting Airflow variable
# var = Variable.get("def", "test")

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(task_id="print_date", bash_command="date", dag=dag)

t2 = BashOperator(task_id="sleep", bash_command="sleep 120", retries=3, dag=dag)

templated_command = """
    echo "{{ macros.between_interval(ti, 'created_at') }}"
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
        echo "{{ params.my_param }}"
    {% endfor %}
    echo "{{ macros.between_interval(ti, 'created_at') }}"
"""

t3 = BashOperator(
    task_id="templated",
    bash_command=templated_command,
    params={"my_param": "Parameter I passed in"},
    executor_config={
        "KubernetesExecutor": {
            "image": "eu.gcr.io/kw-registry/bi/skyflow-data-lake/airflow-gdc:latest"
        }
    },
    dag=dag,
)

t4 = BashOperator(
    task_id="t4",
    bash_command=templated_command,
    params={"my_param": "Parameter I passed in"},
    dag=dag,
)

t1 >> t2 >> t3
t1 >> t4
