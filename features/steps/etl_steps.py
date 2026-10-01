import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from behave import given, when, then  # noqa: E402

from framework import dbt_runner  # noqa: E402
from framework.config import load_config, resolve  # noqa: E402


@given('the raw source data for "customers" and "orders" is available')
def step_raw_source_available(context):
    cfg = load_config()
    for key in ("customers_csv", "orders_csv"):
        path = resolve(cfg["raw_data"][key])
        assert os.path.exists(path), f"Missing raw source file: {path}"


@when("the ETL pipeline is executed via dbt seed, run and test")
def step_run_pipeline(context):
    context.pipeline_result = dbt_runner.run_full_pipeline()


@then("the pipeline should complete with no errors")
def step_pipeline_no_errors(context):
    for phase, result in context.pipeline_result.items():
        assert result.returncode == 0, (
            f"dbt {phase} failed (exit {result.returncode}).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

_PIPELINE_RESULT = None


@given("the ETL pipeline has been executed")
def step_given_pipeline_executed(context):
    global _PIPELINE_RESULT
    if _PIPELINE_RESULT is None:
        _PIPELINE_RESULT = dbt_runner.run_full_pipeline()
    context.pipeline_result = _PIPELINE_RESULT
    for phase, result in context.pipeline_result.items():
        assert result.returncode == 0, (
            f"dbt {phase} failed (exit {result.returncode}).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )