# oscar-econvention-sync

Tool for data synchronization between Oscar and E-convention

## Installation ans startup

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Export your AIRFLOW_HOME environment variable in the current shell:

```bash
export AIRFLOW_HOME=/path/to/your/airflow/home
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

Also, you may encounter an error with psycopg2.
In that case, you can install the required package with:

```bash
sudo apt install libpq-dev python3.x-dev
```
Note: Don't forget to replace x with your current Python version (e.g., python3.11-dev for Python 3.11).


Run Airflow in standalone mode:

```bash
airflow standalone
```

Access the Airflow UI at `http://localhost:8080` and log in with credentials which were provided during the Airflow
setup.

---

## Connecting to Apache Airflow Public API with JWT

[Official documentation](https://airflow.apache.org/docs/apache-airflow/stable/security/api.html)

This section explains how to authenticate and interact with Apache Airflow's public REST API (v2) using curl and JWT authentication, assuming the SimpleAuthManager is configured.

Ensure the following settings are present in the [api] section of your airflow.cfg to allow POST, GET, and other HTTP methods:
```bash
[api]
access_control_allow_headers = content-type
access_control_allow_methods = POST,GET
```

To authenticate, send a POST request to the /auth/token endpoint with your username and password:
```bash
curl -X POST http://localhost:8080/auth/token   -H "Content-Type: application/json"   -d '{
    "username": <admin>,
    "password": <password>
  }'
```
Expected response and save this token to use in next API requests :
```bash
{"access_token":"<JWT access_token>"}
```

You can now use the retrieved token to interact with Airflow's public API.
```bash
curl -X GET http://localhost:8080/api/v2/dags \
  -H "Authorization: Bearer <JWT access_token>"
```

---

## Triggering the ETL pipeline via the Airflow Web UI

An `.env.example` file is provided as a template. It contains the required configuration variables (e.g., paths) for the DAG to function properly.

To use it:

```bash
cp .env.example .env
```
Then edit .env to match your local environment paths.

Access the Airflow UI at http://localhost:8080 and log in with credentials which were provided during the Airflow setup.

Once logged in : 
1. Enable the DAG named econvention_to_oscar.

2. Click on the Trigger DAG button.

3. In the configuration modal, pass a JSON payload in the following format:
```bash
{
  "items": [
    {
      "Reference": "123",
      "Title": "Sample title",
      "Porteur": "Porteur",
      "StructurePorteur": "Struct",
      "DateDemarrage":"29/08/2025 00:00"
    }
  ]
}
```

You can also trigger oscar_to_econvention without a JSON payload

This process automatically extracts data from your OSCAR database. To set it up, follow these steps:

1. Navigate to Admin > Connections in your Airflow interface.
2. Click "Add Connection" to open the connection form.
3. Fill in the form with your PostgreSQL database credentials.

Note: The Connection ID must exactly match the value of POSTGRES_CONN_ID defined in your project's .env file.


---

## Triggering the ETL pipeline via curl

Make sure the requirements from the previous two sections are met before proceeding with this step.

You can copy and paste the following POST request by replacing the logical date:

```bash
curl -X POST http://localhost:8080/api/v2/dags/econvention_to_oscar/dagRuns   
  -H "Content-Type: application/json"   
  -H "Authorization: Bearer <JWT access_token>
  -d '{
    "logical_date": "2025-08-01T00:00:00Z",
    "conf": {
      "items":[
      {
        "Reference": "123",
        "Title": "Sample title",
        "Porteur": "Porteur",
        "StructurePorteur": "Struct",
        "DateDemarrage":"29/08/2025 00:00"
      }
    ]}
  }'
```

If your POST request to trigger the ETL pipeline is queued, it may be because the DAG is currently paused.

You can either enable the DAG via the Airflow Web UI or run this command in your terminal:
```bash
airflow dags unpause econvention_to_oscar
```
To avoid conflicts and ensure that each test is treated as a distinct execution, it's essential to use a unique logical_date for every attempt.

Be sure to change this value for each new try.

---

## Running Tests

To run the full test suite (unit and DAG integration tests), use:

```bash
APP_ENV=TEST pytest
```

Make sure the following test data files are present in the tests/data directory:

1. convention_raw_data.json
2. activity_expected_data.json

These files are used to simulate E-convention input and expected OSCAR output.
