import os

import great_expectations as gx

from framework.config import load_config

_CONTEXT = None
_DATASOURCE = None


def _context():
    global _CONTEXT
    if _CONTEXT is None:
        _CONTEXT = gx.get_context(mode="ephemeral")
    return _CONTEXT


def _connection_string() -> str:
    cfg = load_config()["database"]
    host = os.environ[cfg["host_env_var"]]
    http_path = os.environ[cfg["http_path_env_var"]]
    token = os.environ[cfg["token_env_var"]]
    catalog = os.environ.get(cfg["catalog_env_var"], "workspace")
    schema = os.environ.get(cfg["schema_env_var"], "dq_framework")
    return (
        f"databricks://token:{token}@{host}"
        f"?http_path={http_path}&catalog={catalog}&schema={schema}"
    )


def _datasource():
    global _DATASOURCE
    context = _context()
    existing = context.data_sources.all()
    if "databricks" in existing:
        _DATASOURCE = existing["databricks"]
    elif _DATASOURCE is None:
        _DATASOURCE = context.data_sources.add_sql(
            name="databricks", connection_string=_connection_string()
        )
    return _DATASOURCE


def _table_batch(table_name: str):
    ds = _datasource()
    asset_name = f"{table_name}_asset"
    existing_assets = {a.name: a for a in ds.assets}
    asset = existing_assets.get(asset_name) or ds.add_table_asset(
        name=asset_name, table_name=table_name
    )
    batch_def_name = f"{table_name}_batch_def"
    try:
        batch_def = asset.get_batch_definition(batch_def_name)
    except Exception:
        batch_def = asset.add_batch_definition_whole_table(batch_def_name)
    return batch_def.get_batch()


def _summarize(result, label: str) -> dict:
    return {
        "passed": bool(result.success),
        "success": bool(result.success),
        "label": label,
        "expectation": result.expectation_config.type,
        "result": result.result,
    }


def check_not_null(table: str, column: str) -> dict:
    batch = _table_batch(table)
    result = batch.validate(gx.expectations.ExpectColumnValuesToNotBeNull(column=column))
    return _summarize(result, f"{table}.{column} not null")


def check_value_range(table: str, column: str, min_value=None, max_value=None) -> dict:
    batch = _table_batch(table)
    result = batch.validate(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column=column, min_value=min_value, max_value=max_value
        )
    )
    return _summarize(result, f"{table}.{column} between {min_value} and {max_value}")


def check_accepted_values(table: str, column: str, allowed: list) -> dict:
    batch = _table_batch(table)
    result = batch.validate(
        gx.expectations.ExpectColumnValuesToBeInSet(column=column, value_set=allowed)
    )
    return _summarize(result, f"{table}.{column} in {allowed}")


def _exception_messages(exc) -> list:
    if not exc:
        return []
    if "raised_exception" in exc:
        return [exc.get("exception_message")] if exc.get("raised_exception") else []
    return [
        v.get("exception_message")
        for v in exc.values()
        if isinstance(v, dict) and v.get("raised_exception")
    ]


def check_query(table_for_batch: str, description: str, sql: str) -> dict:
    batch = _table_batch(table_for_batch)
    expectation = gx.expectations.UnexpectedRowsExpectation(
        description=description, unexpected_rows_query=sql
    )
    result = batch.validate(expectation)

    errors = _exception_messages(getattr(result, "exception_info", None))
    if errors:
        raise AssertionError(f"GX query error for '{description}': {'; '.join(errors)}")

    summary = _summarize(result, description)
    observed = result.result.get("observed_value")
    unexpected = result.result.get("unexpected_rows", []) or []
    summary["violation_count"] = int(observed) if observed is not None else len(unexpected)
    summary["violations"] = unexpected[:10]
    return summary


def check_duplicates(table: str, key_column: str) -> dict:
    sql = f"""
        SELECT {key_column}, COUNT(*) AS occurrences
        FROM {{batch}}
        GROUP BY {key_column}
        HAVING COUNT(*) > 1
    """
    return check_query(table, f"No duplicate {key_column} values in {table}", sql)


def check_referential_integrity(child_table, child_col, parent_table, parent_col) -> dict:
    sql = f"""
        SELECT c.{child_col}
        FROM {{batch}} c
        LEFT JOIN {parent_table} p ON c.{child_col} = p.{parent_col}
        WHERE p.{parent_col} IS NULL AND c.{child_col} IS NOT NULL
    """
    return check_query(
        child_table,
        f"Every {child_table}.{child_col} exists in {parent_table}.{parent_col}",
        sql,
    )


def check_freshness(table: str, date_column: str, max_future_days: int = 0) -> dict:
    sql = f"""
        SELECT *
        FROM {{batch}}
        WHERE {date_column} > date_add(current_date(), {max_future_days})
    """
    return check_query(table, f"No future-dated {date_column} in {table}", sql)
