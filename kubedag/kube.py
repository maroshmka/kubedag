import json
import logging
import time
from string import Template

import kubernetes
from kubernetes import utils
from kubernetes.client import V1JobStatus
from kubernetes.utils import FailToCreateError

k8s_client = None


def init_kube():
    global k8s_client

    if k8s_client:
        return k8s_client

    try:
        logging.info("k8s local")
        kubernetes.config.load_kube_config()
    except:
        logging.info("k8s in cluster")
        kubernetes.config.load_incluster_config()

    k8s_client = kubernetes.client.ApiClient()


def k8s_from_yaml(template_path, template_context=None, fail_if_exists=False):
    with open(template_path, "r") as f:
        template = Template(f.read())

    template_context = template_context or {}
    rendered = template.substitute(**template_context)

    name = f"/tmp/{str(time.time())}__rendered.yml"
    with open(name, "w") as f:
        f.write(rendered)

    try:
        utils.create_from_yaml(k8s_client, name)
    except FailToCreateError as e:
        exists = all(ee.status == 409 for ee in e.api_exceptions)
        if exists and not fail_if_exists:
            logging.info("Already exists, skipping creation.")
        else:
            raise e


def get_graph_from_cfgmap():
    api = kubernetes.client.CoreV1Api(k8s_client)

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

    return graphobj["graph"]


async def job_completed(dag_id, task_id) -> bool:
    watch = kubernetes.watch.Watch()
    job_v1 = kubernetes.client.BatchV1Api()
    job_name = jobname(dag_id, task_id)

    for event in watch.stream(
        func=job_v1.list_namespaced_job,
        namespace="default",
        field_selector=f"metadata.name={job_name}",
        timeout_seconds=60 * 5,
    ):  # 5min timeout
        obj: V1JobStatus = event["object"]
        if obj.active:
            logging.info(f"Still waiting for job {job_name}")

        elif obj.active is None and obj.completion_time and obj.succeeded > 1:
            logging.info(f"Job '{job_name}' finished successfully.")
            watch.stop()
            return True

    return False


def jobname(*args):
    return "-".join(a.lower().replace("_", "-") for a in args)
