FROM apache/airflow:2.9.3

#build time variables 
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG CONSTRAINT_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt

COPY requirements.txt /requirements.txt

USER airflow
RUN pip install --no-cache-dir --constraint "${CONSTRAINT_URL}" -r /requirements.txt