import json
import logging

from kubernetes import client, config, utils
config.load_kube_config()
from string import Template

import docker
from pathlib import Path


logging.basicConfig(level=logging.INFO)

here = Path(__file__).parent.absolute()

docker_client = docker.from_env()
airflow_docker_image = "apache/airflow:2.0.0"

logging.info("generating graph from workflow manager")
graph: bytes = docker_client.containers.run(
	airflow_docker_image,
	entrypoint="",
	command="python3 get_graph.py",
	environment={
		"AIRFLOW__CORE__LOGGING_LEVEL": "ERROR"
	},
	volumes={
		here / "dags": {
			'bind': '/opt/airflow/dags',
			'mode': 'ro',
		},
		here / "get_graph.py": {
			'bind': '/opt/airflow/get_graph.py',
			'mode': 'ro',
		}
	},
	remove=True
)

graph_dict = json.loads(graph)
graph_map = json.dumps({"graph.json": graph_dict})

with open("template.graphcfg.yml", "r") as f:
	t = Template(f.read())
	res = t.substitute(data=graph_map)

with open("graphcfg.yml", "w") as f:
	f.write(res)

logging.info("creating config map")

k8s_client = client.ApiClient()
utils.create_from_yaml(k8s_client, "graphcfg.yml")


def create_cronjob(dag_id, task_id):
	with open("template.cronjob.yml", "r") as f:
		cronjob_template = Template(f.read())

	res = cronjob_template.substitute({"dag_id": dag_id, "task_id": task_id})

	with open("cronjob.yml", "w") as f:
		f.write(res)


create_cronjob(graph_dict[0]["dag_id"], graph_dict[0]["downstream"][0]["task_id"])
logging.info("creating cronjob for first task")
utils.create_from_yaml(k8s_client, "cronjob.yml")
