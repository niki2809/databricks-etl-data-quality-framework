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


