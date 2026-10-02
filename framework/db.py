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


ORDER_COLUMN_TYPES = {
    "order_id": "INT",
    "customer_id": "INT",
    "order_date": "DATE",
    "order_amount": "DOUBLE",
    "order_status": "STRING",
}


def _sql_literal(value, sql_type: str) -> str:
    if pd.isna(value):
        return "NULL"
    if sql_type == "INT":
        return str(int(value))
    if sql_type == "DOUBLE":
        return repr(float(value))
    text = str(value).replace("'", "''")
    if sql_type == "DATE":
        return f"DATE'{text}'"
    return f"'{text}'"


def load_raw_orders(csv_path: str, table_name: str = "raw_orders_override") -> None:
    df = pd.read_csv(csv_path, dtype={"order_id": "Int64", "customer_id": "Int64"})
    col_types = {c: ORDER_COLUMN_TYPES.get(c, "STRING") for c in df.columns}
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        columns_ddl = ", ".join(f"`{c}` {t}" for c, t in col_types.items())
        cur.execute(f"CREATE TABLE {table_name} ({columns_ddl}) USING DELTA")
        rows = [
            "(" + ", ".join(_sql_literal(row[c], col_types[c]) for c in df.columns) + ")"
            for _, row in df.iterrows()
        ]
        cur.execute(f"INSERT INTO {table_name} VALUES {', '.join(rows)}")
    finally:
        con.close()


   