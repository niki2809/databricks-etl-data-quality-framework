from behave import when, then

from framework import ge_validations


@when('I run a not-null check on "{table}" column "{column}"')
def step_not_null(context, table, column):
    context.last_check_result = ge_validations.check_not_null(table, column)


@then("the check should pass")
def step_check_passes(context):
    r = context.last_check_result
    assert r["passed"], f"{r['label']} failed: {r['result']}"
    