# PRQ-05: Tax Report Generation
In order to understand my tax obligations for a specific year
As a user
I want to generate a tax report that is displayed within the application

## Description
Generate a comprehensive tax report for a user-selected tax year, which is presented within the application's user interface.

## Details
- UI has "Tax Report" section
- User selects tax year and clicks "Generate Report"
- App processes data and displays clean summary view

## Risks
- Calculation logic bugs lead to incorrect tax figures
- Slow generation for users with many transactions

## Concept
- Backend endpoint takes year, calculates, returns JSON to frontend

## Test Scenarios
- Verify report for "2024" uses only 2024 data
- Verify report view is well-formatted and readable

## Down-stream references
* [CRQ-010: Simple Tax Report Generation](../customer/crq010-generateTaxReport.md)
* [CRQ-011: Clear and Actionable Report View](../customer/crq011-viewTaxReport.md)
