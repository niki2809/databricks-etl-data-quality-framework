# Databricks ETL Data Quality Framework

A BDD data-testing framework for a small ETL flow on Databricks, validating each layer using Great Expectations (GX).

- **BDD:** scenarios are written in Gherkin (`features/data_quality.feature`) and run with behave.
- **ETL:** dbt seeds two source tables (customers, orders), builds staging views and a mart table.
- **Data quality:** GX checks run directly against the Databricks SQL warehouse.
- **Reports:** behave HTML report, plus the terminal output and screenshots in `docs/screenshots/`.

## Architecture

```
CSV seeds (customers, orders)
        |  dbt seed
        v
raw_customers, raw_orders
        |  dbt run
        v
stg_customers, stg_orders  ->  customer_order_summary (mart)
        |
        |  Great Expectations (SQL connection to Databricks)
        v
behave scenarios  ->  console output + HTML report
```

dbt tests (`unique`, `not_null`, `relationships`, `accepted_values` and one custom SQL test) act as a quick gate inside the pipeline. GX is the independent validation layer that checks the finished tables and reports results through the behave scenarios.

## Project structure

```
.
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
```

## Test scenarios (18)

| Area | Tag | Scenarios | What is checked | GX approach |
|---|---|---|---|---|
| Pipeline | `@smoke` | 1 | dbt seed, run and test complete without errors | dbt |
| Completeness | `@completeness` | 4 | Key columns contain no nulls | `ExpectColumnValuesToNotBeNull` |
| Uniqueness | `@uniqueness` | 2 | No duplicate primary keys | SQL via `UnexpectedRowsExpectation` |
| Referential integrity | `@integrity` | 1 | Every order references an existing customer | SQL via `UnexpectedRowsExpectation` |
| Business rules | `@business` | 2 | Amounts are not negative, status is an accepted value | `ExpectColumnValuesToBeBetween`, `ExpectColumnValuesToBeInSet` |
| Freshness | `@freshness` | 2 | No future-dated records | SQL via `UnexpectedRowsExpectation` |
| Reconciliation | `@reconciliation` | 3 | Row counts match between layers, mart totals match staging | `ExpectTableRowCountToEqualOtherTable`, SQL |
| Schema | `@schema` | 2 | Expected columns exist with the expected types | `ExpectColumnToExist`, `ExpectColumnValuesToBeInTypeList` |
| Negative | `@negative` | 1 | Checks detect duplicates, orphans, bad values, invalid status and future dates in a deliberately invalid fixture | all of the above |

The negative scenario loads `data/raw/orders_invalid.csv` into a scratch table (`raw_orders_override`) and asserts that the checks fail on it. This proves the checks catch bad data instead of passing by default.

## Prerequisites

- Python 3.10 or newer
- A Databricks workspace with a running SQL warehouse
- A catalog and schema where you can create tables (defaults: `workspace` and `dq_framework`)
- A Databricks personal access token (User Settings, Developer, Access tokens)

## Setup

```bash
git clone https://github.com/niki2809/databricks-etl-data-quality-framework.git
cd databricks-etl-data-quality-framework

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the schema once in the Databricks SQL editor:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.dq_framework;
```

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Example |
|---|---|
| `DATABRICKS_HOST` | `dbc-xxxxxxxx-xxxx.cloud.databricks.com` (no `https://`) |
| `DATABRICKS_HTTP_PATH` | `/sql/1.0/warehouses/xxxxxxxxxxxxxxxx` |
| `DATABRICKS_TOKEN` | `dapi...` |
| `DATABRICKS_CATALOG` | `workspace` |
| `DATABRICKS_SCHEMA` | `dq_framework` |

Load the variables into your terminal. Environment variables last only for the terminal session, so repeat this in every new terminal:

```bash
set -a; source .env; set +a
```

Check the connection before running the tests:

```bash
dbt debug --project-dir dbt_project --profiles-dir dbt_project
```

## Running the tests

```bash
behave                                   # all 18 scenarios
behave --tags=@smoke                     # pipeline only
behave --tags=@negative                  # negative scenario only
behave --tags=@completeness,@uniqueness  # several groups
behave --dry-run                         # check all steps are defined, run nothing
```

Generate the HTML report:

```bash
behave -f html -o reports/behave/report.html -f pretty
open reports/behave/report.html
```
