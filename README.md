Databricks ETL Data Quality Framework

A BDD data-testing framework for a small ETL flow on Databricks validating each layer using Great Expectations (GX).

BDD: scenarios are written in Gherkin (features/data_quality.feature).
ETL: dbt seeds two source tables (customers, orders), builds staging views and a mart table.
Data quality: GX checks run directly against the Databricks SQL warehouse.
Reports: behave HTML report, plus the terminal output and screenshots in docs/screenshots/.

Project Structure

├── behave.ini                  # behave settings and HTML formatter
├── requirements.txt            # pinned dependencies
├── .env.example                # names of the required environment variables
├── config/
│   └── config.yaml             # file paths, env var names, dbt settings
├── data/raw/
│   └── orders_invalid.csv      # deliberately bad data for the negative scenario
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml            # reads credentials from environment variables
│   ├── seeds/                  # raw_customers.csv, raw_orders.csv
│   ├── models/staging/         # stg_customers, stg_orders, sources and tests
│   ├── models/marts/           # customer_order_summary
│   └── tests/                  # custom SQL test
├── features/
│   ├── data_quality.feature    # the BDD scenarios
│   ├── environment.py          # behave hooks
│   └── steps/                  # step definitions
├── framework/
│   ├── config.py               # config loader
│   ├── db.py                   # Databricks connection and fixture loader
│   ├── dbt_runner.py           # runs dbt seed, run and test
│   └── ge_validations.py       # all Great Expectations checks
├── reports/behave/             # generated HTML report
└── docs/screenshots/           # screenshots of test execution


Prerequisites

Python 3.10 or newer
A Databricks workspace with a running SQL warehouse
A catalog and schema where you can create tables (defaults: workspace and dq_framework)
A Databricks personal access token (User Settings, Developer, Access tokens)

Setup

git clone https://github.com/niki2809/databricks-etl-data-quality-framework.git
cd databricks-etl-data-quality-framework

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Create the schema once in the Databricks SQL editor:
sql
CREATE SCHEMA IF NOT EXISTS workspace.dq_framework;


Copy .env.example to .env and fill in your values:
cp .env.example .env


Variable	Example
DATABRICKS_HOST	dbc-xxxxxxxx-xxxx.cloud.databricks.com (no https://)
DATABRICKS_HTTP_PATH	/sql/1.0/warehouses/xxxxxxxxxxxxxxxx
DATABRICKS_TOKEN	dapi...
DATABRICKS_CATALOG	workspace
DATABRICKS_SCHEMA	dq_framework


Load the variables into your terminal. Environment variables last only for the terminal session, so repeat this in every new terminal:

set -a; source .env; set +a

Check the connection before running the tests:


dbt debug --project-dir dbt_project --profiles-dir dbt_project

Running the tests

behave                                   # all 18 scenarios
behave --tags=@smoke                     # pipeline only
behave --tags=@negative                  # negative scenario only
behave --tags=@completeness,@uniqueness  # several groups
behave --dry-run                         # check all steps are defined, run nothing


Generate the HTML report:

behave -f html -o reports/behave/report.html -f pretty
open reports/behave/report.html