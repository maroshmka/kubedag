import json
import logging

from kubernetes import client, config, utils
from kubernetes.client import ApiException
from kubernetes.utils import FailToCreateError

config.load_kube_config()
from string import Template

import docker
from pathlib import Path

# todo - cfg with these setup things
DUMMY_FIRST_TASK = "DUMMY_FIRST_TASK"

logging.basicConfig(level=logging.INFO)

here = Path(__file__).parent.absolute()

docker_client = docker.from_env()
airflow_docker_image = "apache/airflow:2.0.0"

logging.info("generating graph from workflow manager")
graph: bytes = docker_client.containers.run(
    airflow_docker_image,
    entrypoint="",
    command="python3 get_graph.py",
    environment={"AIRFLOW__CORE__LOGGING_LEVEL": "ERROR"},
    volumes={
        here
        / "dags": {
            "bind": "/opt/airflow/dags",
            "mode": "ro",
        },
        here
        / "get_graph.py": {
            "bind": "/opt/airflow/get_graph.py",
            "mode": "ro",
        },
    },
    remove=True,
)

graph_dict = json.loads(graph)
graph_map = json.dumps(graph_dict)

with open("template.graphcfg.yml", "r") as f:
    t = Template(f.read())
    res = t.substitute(data=graph_map)

with open("graphcfg.yml", "w") as f:
    f.write(res)


k8s_client = client.ApiClient()

logging.info("creating config map")
utils.create_from_yaml(k8s_client, "graphcfg.yml")

logging.info("create SA with perms to read cfgs")
try:
    utils.create_from_yaml(
        k8s_client,
        f"template.serviceaccount.yml",
    )
except FailToCreateError as e:
    exists = all(ee.status == 409 for ee in e.api_exceptions)
    if exists:
        logging.info("SA exists. skipping creation.")
    else:
        raise e


def create_cronjob(dag_id):
    with open("template.cronjob.yml", "r") as f:
        cronjob_template = Template(f.read())

    # first task is always dummy cronjob
    rendered = cronjob_template.substitute(
        {"dag_id": dag_id, "task_id": DUMMY_FIRST_TASK}
    )

    with open(f"{dag_id}__cronjob.yml", "w") as f:
        f.write(rendered)


for dag_id, tasks in graph_dict["graph"].items():
    create_cronjob(dag_id)
    logging.info(f"creating cronjob - {dag_id}")
    utils.create_from_yaml(k8s_client, f"{dag_id}__cronjob.yml")

    # supports only 1 dag :D
    break
