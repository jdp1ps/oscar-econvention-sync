# oscar-econvention-sync

Tool for data synchronization between Oscar and E-convention

## Installation ans startup

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Export your AIFLOW_HOME environment variable in the current shell:

```bash
export AIFLOW_HOME=/path/to/your/aiflow/home
```

To check your database settings, run :

```bash
airflow config get-value database sql_alchemy_conn
```

On some Ubuntu systems, you may encounter an error with asyncpg.
In that case, you can install the required package with:

```bash
python3 -m pip install asyncpg
```

Run Airflow in standalone mode:

```bash
airflow standalone
```

Access the Airflow UI at `http://localhost:8080` and log in with credentials which were provided during the Airflow
setup.
