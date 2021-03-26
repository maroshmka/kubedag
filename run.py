# todo use docker in docker? or another k8s job
import datetime
import logging
import subprocess
import sys
import json

logging.basicConfig(level=logging.INFO)

logging.info("=="*100)
with open("/app/graph/graph.json", "r") as f:
    logging.info(json.load(f))


dag_id = sys.argv[1]
task_id = sys.argv[2]

# todo - sort out time.
execution_date = datetime.datetime.now()
airflow_cmd = f"airflow tasks test {dag_id} {task_id} {execution_date.isoformat()}".split(" ")

process = subprocess.Popen(airflow_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

print(stdout)
print(stderr)

if process.returncode != 0:
    sys.exit(process.returncode)
else:
    print("running deps")
    # do stuff
    pass

    # todo - run jobs that can be run and wait for deps

    # todo - for each downstream tasks, determine if they can run todo - do that by checking they
    #  upstream. if only this task, then run, else check if other tasks finished. if yes,then do run
    #  them wait for all tasks to be met and then run those as well. if all running finish process
