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


@when('I compare the row count of "{table}" with "{other_table}"')
def step_row_count(context, table, other_table):
    context.last_check_result = ge_validations.check_row_count_matches(table, other_table)


@when('I reconcile the totals of "{mart}" against "{orders}"')
def step_reconcile(context, mart, orders):
    context.last_check_result = ge_validations.check_aggregate_reconciliation(mart, orders)


@when('I inspect the schema of table "{table}"')
def step_inspect_schema(context, table):
    failures = []
    for column in ge_validations.EXPECTED_TYPES[table]:
        exists = ge_validations.check_column_exists(table, column)
        if not exists["passed"]:
            failures.append({"column": column, "issue": "missing"})
            continue
        typed = ge_validations.check_column_type(table, column)
        if not typed["passed"]:
            failures.append({"column": column, "issue": "wrong type", "gx_result": typed["result"]})
    context.last_check_result = {
        "passed": not failures,
        "label": f"{table} schema",
        "result": failures,
    }
    
        
@then("the check should pass")
def step_check_passes(context):
    r = context.last_check_result
    assert r["passed"], f"{r['label']} failed: {r['result']}"


