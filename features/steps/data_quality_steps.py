from behave import when, then

from framework import ge_validations


@when('I run a not-null check on "{table}" column "{column}"')
def step_not_null(context, table, column):
    context.last_check_result = ge_validations.check_not_null(table, column)


@when('I run a duplicate check on "{table}" using key "{key}"')
def step_duplicates(context, table, key):
    context.last_check_result = ge_validations.check_duplicates(table, key)


@when('I run a referential integrity check between "{child}" and "{parent}"')
def step_referential_integrity(context, child, parent):
    child_table, child_col = child.split(".")
    parent_table, parent_col = parent.split(".")
    context.last_check_result = ge_validations.check_referential_integrity(
        child_table, child_col, parent_table, parent_col
    )


@when('I run a value range check on "{table}" column "{column}" with minimum {minimum}')
def step_value_range(context, table, column, minimum):
    context.last_check_result = ge_validations.check_value_range(
        table, column, min_value=float(minimum)
    )


@when('I run an accepted values check on "{table}" column "{column}" allowing "{values}"')
def step_accepted_values(context, table, column, values):
    allowed = [v.strip() for v in values.split(",")]
    context.last_check_result = ge_validations.check_accepted_values(table, column, allowed)


@when('I run a freshness check on "{table}" column "{column}"')
def step_freshness(context, table, column):
    context.last_check_result = ge_validations.check_freshness(table, column)


@then("the check should pass")
def step_check_passes(context):
    r = context.last_check_result
    assert r["passed"], f"{r['label']} failed: {r['result']}"


