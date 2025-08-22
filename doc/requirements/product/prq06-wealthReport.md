# PRQ-06: Wealth Report Content
In order to fill out my official tax forms correctly  
As a user  
I want the wealth portion of the report to contain all the specific details required for my annual securities schedule.

## Description
The generated tax report must contain a Wealth section listing all asset holdings as of December 31st. For each asset, it must specify the quantity, the value per unit in the reporting currency, and the total value in the reporting currency.

## Details
- "Wealth" section is table of assets held on Dec 31st
- Columns: Asset Name, Quantity, Value per Unit (Reporting Currency), Total Value (Reporting Currency)

## Risks
- Asset missed in year-end calculation
- Quantity calculated incorrectly

## Concept
- Function calculates final balances at year-end
- Multiplies balances by price from valuation engine

## Test Scenarios
- Manually calculate balance of one asset, verify it matches report
- Verify total value is `Quantity * Value per Unit`

## Down-stream references
* [CRQ-011: Clear and Actionable Report View](../customer/crq011-viewTaxReport.md)
* [CRQ-012: Understandable Wealth Schedule](../customer/crq012-wealthSchedule.md)
* [CRQ-018: Compliant Swiss Valuation](../customer/crq018-swissValuation.md)
