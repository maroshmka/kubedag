import json
import logging

from kubedag.kube import init_kube, k8s_from_yaml, jobname

import docker
from pathlib import Path


init_kube()
DUMMY_FIRST_TASK = "DUMMY_FIRST_TASK"  # todo - cfg with these setup things
logging.basicConfig(level=logging.INFO)
here = Path(__file__).parent.absolute()
root = here.parent.absolute()
templates_path = root / "templates"
docker_client = docker.from_env()
airflow_docker_image = "apache/airflow:2.0.0"


logging.info("generating graph from workflow manager")
graph: bytes = docker_client.containers.run(
    airflow_docker_image,
    entrypoint="",
    command="python3 get_graph.py",
    environment={"AIRFLOW__CORE__LOGGING_LEVEL": "ERROR"},
    volumes={
        root
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

logging.info("creating config map")
k8s_from_yaml(templates_path / "template.graphcfg.yml", {"data": graph_map})

logging.info("create SA with perms to read cfgs")
k8s_from_yaml(templates_path / "template.serviceaccount.yml")

logging.info("Processing graph of workflows and creating dummy first task as cronjob.")
for dag_id, tasks in graph_dict["graph"].items():
    logging.info(f"creating cronjob - {dag_id}")
    k8s_from_yaml(
        templates_path / "template.cronjob.yml",
        template_context={
            "dag_id": dag_id,
            "task_id": DUMMY_FIRST_TASK,
            "cronjob_name": jobname(dag_id, DUMMY_FIRST_TASK),
        },
    )

    # supports only 1 dag :D
    break
