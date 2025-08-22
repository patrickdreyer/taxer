# CRQ-010: Simple Tax Report Generation
In order to get the final figures for my tax declaration  
As a user  
I want to select a tax year and click a single button to generate my complete tax report.

## Description
The user needs a straightforward way to get their final tax numbers. This process should be as simple as selecting the relevant year and initiating the calculation. The frontend provides these simple controls, which trigger the complex calculation and report compilation process on the backend.

## Details
* A dedicated "Tax Report" page in the application
* A dropdown menu to select the tax year
* A single "Generate Report" button
* A loading indicator is shown while the backend performs calculations

## Risks
* I might generate a report for the wrong year by mistake
* The report generation might be slow, and I might not know if the app has frozen

## Concept
* It's a specific function in the app, separate from the raw transaction list
* The "Generate" button tells the backend to do all the heavy lifting and calculations
* A loading overlay prevents me from clicking anything else until the report is ready

## Test Scenarios
* Verify the tax year dropdown shows previous years correctly
* Verify clicking "Generate" shows a loading indicator and then the report view
* Verify the generated report title clearly states the selected year (e.g., "Tax Report 2024")

## Up-stream references
* [PRQ-05: Tax Report Generation](../product/prq05-taxReport.md)