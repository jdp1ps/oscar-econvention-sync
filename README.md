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
      "Partenaire": "Partenaire",
      "DateDemarrage": "29/08/2025 00:00",
      "MontantConvention": "1 000,1",
      "TypeConvention": "Recherche",
      "SousType": "Appels à projets internes"
    }
  ]
}
```

You can also trigger oscar_to_econvention DAG without a JSON payload

This process automatically extracts data from your OSCAR database. To set it up, follow these steps:

1. Navigate to Admin > Connections in your Airflow interface.
2. Click "Add Connection" to open the connection form.
3. Fill in the form with your PostgreSQL database credentials.

Or, you can run this following command:
```bash
airflow connections add <connection_id_name> \
    --conn-uri postgresql://<user>:<password>@<host>:5432/<db_name>
```

Note: The Connection ID must exactly match the value of POSTGRES_CONN_ID defined in your project's .env file.

Note: The same steps apply when configuring a Redis database connection.

---

## Triggering the ETL pipeline via curl

Make sure the requirements from the previous section are met before proceeding with this step.

To authenticate, send a POST request to the /auth/token endpoint with your username and password:
```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "<username>",
    "password": "<password>"
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

You can copy and paste the following POST request by replacing the logical date:

```bash
curl -X POST http://localhost:8080/api/v2/dags/econvention_to_oscar/dagRuns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT access_token>" \
  -d '{
    "logical_date": "2025-08-01T00:00:00Z",
    "conf": {
      "items":[
      {
        "Reference": "123",
        "Title": "Sample title",
        "Porteur": "Porteur",
        "Partenaire": "Partenaire",
        "DateDemarrage":"29/08/2025 00:00",
        "MontantConvention": "1 000,1",
        "TypeConvention": "Recherche",
        "SousType": "Appels à projets internes"
      }
    ]}
  }'
```

**Note:** If your POST request to trigger the ETL pipeline is queued, it may be because the DAG is currently paused.

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

## Quickstart in VirtualBox

### 1. Prepare Ubuntu 24.04 in Oracle VirtualBox

Download ISO image of Ubuntu 24.04.3 LTS:  
https://ubuntu.com/download/desktop

Open Oracle VirtualBox:

1. Click **New**
2. Fill VM Name and add the downloaded ISO image
3. Fill User Name and Password
4. Set Base Memory to 8192 MB, Number of CPUs to 4, Disk to 100 GB

**Default configurations:**
- Network: NAT
- USB: USB 2.0 Controller

**Note:** Change Graphics Controller to **VBoxVGA** (VMSVGA is not supported).

**Note:** If keyboard and mouse inputs do not work in the VM, switch to **USB 1.1 (OHCI)**.  
This ensures proper capture of input devices in Ubuntu 24.04 Desktop under VirtualBox.  

---

### 2. Setup fresh Ubuntu 24.04 VM

#### Start the VM and log in with the user name and password you created.
**Note:** The keyboard layout may switch to QWERTY automatically, so adapt your input if necessary.

 **Tip:** Wait until the Ubuntu installation completes and the VM finishes its first boot to log.

#### System update
```bash
sudo apt update && sudo apt upgrade -y
```
#### Install required system packages
```bash
sudo apt install -y libpq-dev python3-dev build-essential python3-venv python3-pip git curl
```

#### Clone project repository
```bash
git clone https://github.com/jdp1ps/oscar-econvention-sync.git
cd oscar-econvention-sync
```

#### Create and activate Python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
```

#### Install Python dependencies
```bash
pip install -r requirements.txt
```

#### Configure environment variables
Main configuration file for Airflow
```bash
cp .env.example .env
nano .env
```
*(adjust database credentials, API keys, etc.)*

Configuration file specific for pytest
```bash
cp .env.example .env.test
nano .env.test
```
*(adjust settings for the test environment)*

#### Set Airflow home (temporary)
```bash
export AIRFLOW_HOME=~/airflow
```


#### Initialize Airflow database (if Airflow is part of the project)
```bash
airflow db migrate
```

#### Configure Airflow configuration
```bash
nano ~/airflow/airflow.cfg
```

```ini
[core]
dag_folder = ~/oscar-econvention-sync/dags
load_examples = False
[api]
access_control_allow_headers = content-type
access_control_allow_methods = POST,GET
```

#### Run Airflow in standalone mode:
```bash
airflow standalone
```
#### Login to Airflow Webserver

Once Airflow standalone is running, open your browser and go to: http://localhost:8080/

Use the credentials generated by Airflow:

```bash
cat ~/airflow/simple_auth_manager_passwords.json.generated
```

#### Run tests

Before running tests, make sure Airflow is pointing to the project DAGs by creating a symbolic link:
```bash
ln -s ~/oscar-econvention-sync/dags ~/airflow/dags
```
You can verify that the link is correctly created with:
```bash
ls -l ~/airflow
```

It should display something like: ```ini dags -> /home/user/oscar-econvention-sync/dags```

Now you can run the tests:

```bash
APP_ENV=TEST pytest
```

#### Others

Install Redis server in the VM for preproduction testing. See official guide: [Install Redis on Linux](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-linux/)
