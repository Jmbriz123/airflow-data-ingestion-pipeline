# Airflow Data Ingestion Pipeline

A reproducible, containerized ETL pipeline for customer-care email data. Apache Airflow orchestrates the work and PostgreSQL stores the final dataset.

The repository includes the source CSV, the expected schema, and the SQL definition for the target table. No local Python installation is required to run the pipeline.

## What the pipeline does

The DAG is named `customer_care_emails_pipeline` and runs these tasks in order:

1. **Extract** reads `data/dataset.csv` and writes a temporary Parquet file.
2. **Validate** checks column names, nullability, and pandas data types against `config/customer-care-emails/expected_schema.yaml`.
3. **Transform** trims text, parses UTC timestamps, converts customer satisfaction to a number, and converts list-valued fields to JSON.
4. **Load** creates the target table from `config/customer-care-emails/ddl.sql` and loads the transformed rows into `public.customer_care_emails`.

The source data is mounted into Airflow at `/opt/airflow/data`; configuration, pipeline code, DAGs, logs, and plugins are mounted in the same way. The current checked-in CSV contains 20,488 data rows, excluding its header.

## Prerequisites

Install Docker on the host machine. Git is optional if you already have the repository files, and a web browser is needed for the Airflow UI.

- Docker Desktop, or Docker Engine with the Compose plugin
- A web browser

Verify Docker Compose is available:

```bash
docker --version
docker compose version
```

The commands below are written for Linux and macOS. On Windows, run them from WSL or adapt `id -u` to the user-ID mechanism provided by your Docker environment.

## Get the project

Clone the repository and enter its root directory:

```bash
git clone <repository-url>
cd airflow-data-ingestion-pipeline
```

If the project is already open in VS Code, run the remaining commands from the directory containing `docker-compose.yaml`.

## Configure the environment

Create the local `.env` file from the committed template:

```bash
cp .env.example .env
id -u
```

Open `.env`, set `AIRFLOW_UID` to the number printed by `id -u`, and replace `your_username` and `your_password` with local values. For example:

```dotenv
POSTGRES_USER=airflow_user
POSTGRES_PASSWORD=airflow_password
POSTGRES_DB=airflow_data
DB_HOST=postgres
DB_PORT=5432
DB_NAME=airflow_data
AIRFLOW_UID=1000
```

The values in `DB_HOST` and `DB_PORT` are container-to-container settings. Keep `DB_HOST=postgres`: that is the Compose service name, not `localhost`. `.env` is ignored by Git and should not be committed.

## Start Airflow and PostgreSQL

Build the Airflow image and start both services in the background:

```bash
docker compose up --build -d
```

Check that the containers exist:

```bash
docker compose ps
```

Airflow may take a minute to initialize its metadata database. Follow its startup logs until it reports that the standalone server is running:

```bash
docker compose logs -f airflow
```

Press `Ctrl+C` to stop following logs; the containers continue running. Open the Airflow web UI at [http://localhost:8080](http://localhost:8080).

### Airflow login

Airflow standalone creates a local `admin` user. The generated password is printed in the Airflow logs during first startup. Retrieve it with:

```bash
docker compose logs airflow | grep -i -E "password|username"
```

Use username `admin` and the password shown in the logs. If the logs have rotated or the password is unavailable, inspect the mounted Airflow home inside the container:

```bash
docker compose exec airflow sh -c 'cat /opt/airflow/simple_auth_manager_passwords.json.generated'
```

## Trigger the DAG

### Using the web UI

1. Open [http://localhost:8080](http://localhost:8080) and sign in.
2. Find `customer_care_emails_pipeline` in the DAG list.
3. Turn the DAG on if it is paused.
4. Open the DAG, choose **Trigger DAG**, and confirm.
5. Open the new DAG run and wait for `extract`, `validate`, `transform`, and `load` to show success.

### Using the command line

The same operation can be performed without the browser:

```bash
docker compose exec airflow airflow dags trigger customer_care_emails_pipeline
```

Inspect recent runs and task states:

```bash
docker compose exec airflow airflow dags list-runs -d customer_care_emails_pipeline
docker compose exec airflow airflow tasks states-for-dag-run \
	customer_care_emails_pipeline <run_id>
```

Replace `<run_id>` with the run ID printed by the first command. The `@daily` schedule is enabled in the DAG, but `catchup=False` prevents historical runs from being created automatically.

## Verify the loaded rows

Run the following query inside the PostgreSQL container. Reading the variables inside the container means the command works with the credentials in `.env` without requiring you to export them in the host shell:

```bash
docker compose exec postgres sh -c \
	'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) AS row_count FROM public.customer_care_emails;"'
```

The result should be `20488` for the version of `data/dataset.csv` currently in this repository. A different count is expected if the CSV has been changed.

Useful inspection queries:

```bash
docker compose exec postgres sh -c \
	'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM public.customer_care_emails LIMIT 5;"'

docker compose exec postgres sh -c \
	'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT MIN(timestamp), MAX(timestamp) FROM public.customer_care_emails;"'
```

The load task is intentionally repeatable: each successful run replaces the target table contents with the current transformed CSV, so rerunning it does not append duplicate rows.

## Repository layout

```text
config/
	config.py                         Environment variables and project paths
	customer-care-emails/ddl.sql     PostgreSQL table definition
	customer-care-emails/expected_schema.yaml
																		DataFrame validation contract
data/dataset.csv                   Source dataset mounted into Airflow
dags/customer_care_emails_dag.py   Airflow DAG and task dependencies
pipeline/                           Extract, validate, transform, and load code
docker-compose.yaml                Airflow and PostgreSQL services
Dockerfile                          Airflow image and Python dependencies
logs/                               Persisted Airflow task logs
```

## Common troubleshooting

### `docker compose` cannot find `.env`

Run `cp .env.example .env` from the project root. Confirm the file contains values for `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `AIRFLOW_UID`.

### Airflow is still starting or the web page is unavailable

Check service status and logs:

```bash
docker compose ps
docker compose logs --tail=100 airflow
docker compose logs --tail=100 postgres
```

Wait for initialization to finish, then refresh `http://localhost:8080`. If port `8080` is already in use, stop the other service or change the left side of the port mapping in `docker-compose.yaml`, for example `8081:8080`, and use `http://localhost:8081`.

### The DAG is not visible

Confirm the DAG file is mounted and inspect Airflow’s import errors:

```bash
docker compose exec airflow airflow dags list | grep customer_care_emails_pipeline
docker compose exec airflow airflow dags list-import-errors
```

The project must be started from its root directory so the relative volume mounts point at `dags/`, `pipeline/`, `config/`, and `data/`.

### A task fails because PostgreSQL is unavailable

Compose starts PostgreSQL before Airflow, but the database may still be initializing. Check PostgreSQL logs, wait a few seconds, and trigger the DAG again:

```bash
docker compose logs --tail=100 postgres
docker compose exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

If the host shell does not have those variables, use the container form:

```bash
docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

### Validation fails

Inspect the failed task log in the Airflow UI or with:

```bash
docker compose logs airflow
```

Compare the CSV columns and null values with `config/customer-care-emails/expected_schema.yaml`. If you changed the CSV, rerun the DAG after correcting the data.

### Start over with a clean database

This removes the named PostgreSQL volume, including all loaded data and Airflow metadata. Use it only when a full reset is intended:

```bash
docker compose down -v
docker compose up --build -d
```

## Stop and clean up

Stop the services while keeping the PostgreSQL volume:

```bash
docker compose down
```

Stop services and delete the persisted database volume:

```bash
docker compose down -v
```

View all service logs:

```bash
docker compose logs -f
```

## Reproduction checklist

- Docker and Docker Compose are installed.
- `.env` was created from `.env.example` and `AIRFLOW_UID` matches `id -u`.
- `docker compose up --build -d` completed successfully.
- The DAG was triggered manually.
- All four tasks succeeded.
- PostgreSQL returned a row count for `public.customer_care_emails`.
