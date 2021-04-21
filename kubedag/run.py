import asyncio
import datetime
import logging
import subprocess
import sys

from kube import (
    get_graph_from_cfgmap,
    k8s_from_yaml,
    job_completed,
    jobname,
    init_kube,
)

DUMMY_FIRST_TASK = "DUMMY_FIRST_TASK"
logging.basicConfig(level=logging.INFO)
logging.info("==" * 100)
init_kube()


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

logging.info("process finished, running downstream")
graph = get_graph_from_cfgmap()
dag = graph[dag_id]
logging.info(f"Im a task: dag_id='{dag_id}' task_id='{task_id}'")


def completed(d_id, t_id):
    if d_id == dag_id and t_id == task_id:
        logging.info("skipping self")
        return True
    return job_completed(d_id, t_id)


if task_id == DUMMY_FIRST_TASK:
    logging.info("trigger all the roots")
    for root_task_id in dag["roots"]:
        k8s_from_yaml(
            "./templates/template.job.yml",
            template_context={
                "dag_id": dag_id,
                "task_id": root_task_id,
                "job_name": jobname(dag_id, root_task_id),
            },
        )
else:
    logging.info("trigger all possible downstream")
    # for all of downstream of current check if all upstream fine, if yes trigger
    curr_task = dag["tasks"][task_id]

    # todo - run this in parallel
    for down_id in curr_task["downstream"]:
        downtask = dag["tasks"][down_id]

        # todo - this is done in airflow?

        # todo - timeout hardcoded 5min each
        ok = [completed(dag_id, t) for t in downtask["upstream"]]
        if all(ok):
            k8s_from_yaml(
                "./templates/template.job.yml",
                template_context={
                    "dag_id": dag_id,
                    "task_id": down_id,
                    "job_name": jobname(dag_id, down_id),
                },
            )
