Feature: ETL data quality automation
  As a data engineering team
  We want an automated data-testing suite covering the full ETL flow
  So that broken pipelines and bad data are caught before they reach downstream application.

  @smoke @pipeline
  Scenario: The ETL pipeline runs end-to-end without errors
    Given the raw source data for "customers" and "orders" is available
    When the ETL pipeline is executed via dbt seed, run and test
    Then the pipeline should complete with no errors