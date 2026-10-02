Feature: Data Quality Automation
  As a data engineering team
  We want an automated data-testing suite covering the full ETL flow
  So that broken pipelines and bad data are caught before they reach downstream application.

  @smoke @pipeline
  Scenario: The ETL pipeline runs end-to-end without errors
    Given the raw source data for "customers" and "orders" is available
    When the ETL pipeline is executed via dbt seed, run and test
    Then the pipeline should complete with no errors


@regression @completeness
  Scenario Outline: Key columns must not contain nulls
    Given the ETL pipeline has been executed
    When I run a not-null check on "<table>" column "<column>"
    Then the check should pass

    Examples:
      | table         | column      |
      | stg_customers | customer_id |
      | stg_customers | email       |
      | stg_orders    | order_id    |
      | stg_orders    | customer_id |


@regression @uniqueness
  Scenario Outline: Primary keys must be unique
    Given the ETL pipeline has been executed
    When I run a duplicate check on "<table>" using key "<key>"
    Then the check should pass

    Examples:
      | table         | key         |
      | stg_customers | customer_id |
      | stg_orders    | order_id    |


@regression @integrity
  Scenario Outline: Every order must reference an existing customer
    Given the ETL pipeline has been executed
    When I run a referential integrity check between "<child>" and "<parent>"
    Then the check should pass

    Examples:
      | child                 | parent                 |
      | stg_orders.customer_id | stg_customers.customer_id |


@regression @business
  Scenario Outline: Order amounts must never be negative
    Given the ETL pipeline has been executed
    When I run a value range check on "<table>" column "<column>" with minimum <minimum>
    Then the check should pass

    Examples:
      | table      | column       | minimum |
      | stg_orders | order_amount | 0       |


@regression @business
  Scenario Outline: Order status must only contain accepted values
    Given the ETL pipeline has been executed
    When I run an accepted values check on "<table>" column "<column>" allowing "<values>"
    Then the check should pass


    Examples:
      | table      | column       | values                       |
      | stg_orders | order_status | COMPLETED, CANCELLED, PENDING |


@regression @freshness
  Scenario Outline: Dates must not be in the future
    Given the ETL pipeline has been executed
    When I run a freshness check on "<table>" column "<column>"
    Then the check should pass

    Examples:
      | table         | column      |
      | stg_orders    | order_date  |
      | stg_customers | signup_date |


@regression @reconciliation
  Scenario Outline: Row counts must match between layers
    Given the ETL pipeline has been executed
    When I compare the row count of "<table>" with "<other_table>"
    Then the check should pass

    Examples:
      | table         | other_table   |
      | stg_customers | raw_customers |
      | stg_orders    | raw_orders    |


@regression @reconciliation
  Scenario: Mart totals must reconcile with the staging layer
    Given the ETL pipeline has been executed
    When I reconcile the totals of "customer_order_summary" against "stg_orders"
    Then the check should pass


@regression @schema
  Scenario Outline: Staging tables must have the expected schema
    Given the ETL pipeline has been executed
    When I inspect the schema of table "<table>"
    Then the check should pass

    Examples:
      | table         |
      | stg_customers |
      | stg_orders    |


      