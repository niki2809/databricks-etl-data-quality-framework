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
