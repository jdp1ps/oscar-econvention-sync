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
---
# Connecting to Apache Airflow Public API with JWT

Official documentation : https://airflow.apache.org/docs/apache-airflow/stable/security/api.html

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

