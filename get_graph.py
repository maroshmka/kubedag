import logging
import json
from airflow.models.dagbag import DagBag

logging.basicConfig(level=logging.ERROR)

dagbag = DagBag("/opt/airflow/dags")

# todo - use graphviz dot thing ?
out = {
    "graph": {
        d.dag_id: {
            "tasks": {
                # todo - should we also add the dummy first task?
                # todo - probably not needed, but could be use-full for testing
                t.task_id: {
                    "downstream": [tt.task_id for tt in t.downstream_list],
                    "upstream": [tt.task_id for tt in t.upstream_list],
                }
                for t in d.tasks
            },
            "roots": [tt.task_id for tt in d.roots],
        },
    }
    for dag_id, d in dagbag.dags.items()
}

print(json.dumps(out))
