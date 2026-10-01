import os
import pandas as pd
from databricks import sql as databricks_sql

from framework.config import load_config


def _connection_kwargs() -> dict:
    cfg = load_config()["database"]
    return {
        "server_hostname": os.environ[cfg["host_env_var"]],
        "http_path": os.environ[cfg["http_path_env_var"]],
        "access_token": os.environ[cfg["token_env_var"]],
        "catalog": os.environ.get(cfg["catalog_env_var"], "workspace"),
        "schema": os.environ.get(cfg["schema_env_var"], "dq_framework"),
    }


def get_connection():
    return databricks_sql.connect(**_connection_kwargs())


def run_query(sql: str) -> pd.DataFrame:
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall_arrow().to_pandas()
    finally:
        con.close()