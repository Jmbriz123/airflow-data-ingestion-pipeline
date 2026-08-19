FROM apache/airflow:2.9.3-python3.11

COPY requirements.txt /requirements.txt

USER airflow

RUN pip install \
    --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    -r /requirements.txt