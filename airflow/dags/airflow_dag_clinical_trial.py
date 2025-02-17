#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
### DAG Tutorial Documentation
This DAG is demonstrating an Extract -> Transform -> Load pipeline
"""

from __future__ import annotations

# [START tutorial]
# [START import_module]
import json
import textwrap

import pendulum

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

from tdc.multi_pred import TrialOutcome

# [END import_module]

# [START instantiate_dag]
with DAG(
    "dag_clinical_trial",
    # [START default_args]
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={"retries": 2},
    # [END default_args]
    description="DAG clinical trial",
    schedule=None,
    catchup=False,
    tags=["example"],
) as dag:
    # [END instantiate_dag]
    # [START documentation]
    dag.doc_md = __doc__
    # [END documentation]

    # [START extract_function]
    def extract(**kwargs):
        ti = kwargs["ti"]
        data = TrialOutcome(name = 'phase1') # 'phase2' / 'phase3'
        split = data.get_split()
        data_train = split['train']
        ti.xcom_push("order_data", data_train)

    # [END extract_function]

    # [START transform_function]
    def transform(**kwargs):
        ti = kwargs["ti"]
        extract_data_string = ti.xcom_pull(task_ids="extract", key="order_data")
        
        print(extract_data_string)

        ti.xcom_push("total_order_value", extract_data_string)

    # [END transform_function]

    # [START load_function]
    def load(**kwargs):
        ti = kwargs["ti"]
        total_value_string = ti.xcom_pull(task_ids="transform", key="total_order_value")

        print(total_value_string)

    # [END load_function]

    # [START main_flow]
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )
    extract_task.doc_md = textwrap.dedent(
        """\
    #### Extract task
    A simple Extract task to get data ready for the rest of the data pipeline.
    In this case, getting data is simulated by reading from a hardcoded JSON string.
    This data is then put into xcom, so that it can be processed by the next task.
    """
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )
    transform_task.doc_md = textwrap.dedent(
        """\
    #### Transform task
    A simple Transform task which takes in the collection of order data from xcom
    and computes the total order value.
    This computed value is then put into xcom, so that it can be processed by the next task.
    """
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )
    load_task.doc_md = textwrap.dedent(
        """\
    #### Load task
    A simple Load task which takes in the result of the Transform task, by reading it
    from xcom and instead of saving it to end user review, just prints it out.
    """
    )

    extract_task >> transform_task >> load_task

# [END main_flow]