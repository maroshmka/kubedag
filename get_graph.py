import logging
import json
from airflow.models.dagbag import DagBag

logging.basicConfig(level=logging.ERROR)

dagbag = DagBag("/opt/airflow/dags")

# todo - use graphviz ?
# todo - always needs 1 dummy root? probably yes, so we can parallelize first level of tasks

print(
    json.dumps([
        {
            "dag_id": d.dag_id,
            "downstream": [{
                 "task_id": t.task_id,
                 "downstream": [tt.task_id for tt in t.downstream_list]
            } for t in d.tasks],
            "upstream": {
                t.task_id: [tt.task_id for tt in t.upstream_list]
                for t in d.tasks
            }
        }
        for dag_id, d in dagbag.dags.items()
    ])
)
