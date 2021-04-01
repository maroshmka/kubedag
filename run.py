import datetime
import logging
import subprocess
import sys
import json

import kubernetes

DUMMY_FIRST_TASK = "DUMMY_FIRST_TASK"
logging.basicConfig(level=logging.INFO)
logging.info("==" * 100)

with open("/app/graph/graph.json", "r") as f:
    logging.info(json.load(f))


def run_subprocess(d_id, t_id):
    # todo use docker in docker? or another k8s job
    # todo - sort out time.
    execution_date = datetime.datetime.now()
    airflow_cmd = (
        f"airflow tasks test {d_id} {t_id} {execution_date.isoformat()}".split(" ")
    )

    process = subprocess.Popen(
        airflow_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    print(stdout)
    print(stderr)
    return process


dag_id, task_id = sys.argv[1], sys.argv[2]
if task_id == DUMMY_FIRST_TASK:
    # skipping dummy, rather a bit more explicit here
    pass
else:
    process = run_subprocess(d_id=dag_id, t_id=task_id)
    # fail fast
    if process.returncode != 0:
        sys.exit(process.returncode)

logging.info("process finished, running deps")

try:
    logging.info("k8s local")
    kubernetes.config.load_kube_config()
except:
    logging.info("k8s in cluster")
    kubernetes.config.load_incluster_config()

with kubernetes.client.ApiClient() as api_client:
    api = kubernetes.client.CoreV1Api(api_client)

    resp = api.list_namespaced_config_map(
        namespace="default", field_selector="metadata.name=kubedag-graph"
    )

    if len(resp.items) == 0:
        logging.error("no cfg map for kubedag graph")
        raise Exception("no cfg map for kubedag graph")
    elif len(resp.items) > 1:
        logging.error("too many cfg maps for kubedag graph")
        raise Exception("too many cfg maps for kubedag graph")

    graphobj = json.loads(resp.items[0].data["graph.json"])

graph = graphobj["graph"]
dag = graph[dag_id]
logging.info(dag)


def completed(d_id, t_id):
    if d_id == dag_id and t_id == task_id:
        logging.info("skipping self")

    # todo - implement

    return True


def trigger(t_id):
    # todo - implement
    logging.info(f"Creating k8s job for task: {t_id}")


if task_id == DUMMY_FIRST_TASK:
    # trigger all the roots
    for root in dag["roots"]:
        print("triggering root")
else:
    # for all of downstream of current check if all upstream fine, if yes trigger
    curr_task = dag["tasks"][task_id]

    # todo - run this in parallel
    for down_id in curr_task["downstream"]:
        downtask = dag["tasks"][down_id]

        # todo - block this until every downstream is in completed state
        if all(completed(dag_id, t) for t in downtask["upstream"]):
            trigger(downtask)

    logging.info(dag["roots"])
