# PRQ-07: Income Report Content
In order to declare my asset-related income accurately  
As a user  
I want the income portion of the report to detail every taxable event and its value.

## Description
The generated tax report must contain an Income section listing all taxable events, such as staking or airdrops. For each event, it must specify the date, the asset, the quantity received, and the market value in the reporting currency at the time of receipt.

## Details
- "Income" section is table of taxable events
- Columns: Date, Type, Asset, Quantity Received, Value at Receipt (Reporting Currency)

## Risks
- Transaction misclassified as income
- Incorrect value at receipt due to failed price lookup

## Concept
- System filters transactions for "income" types
- Calls valuation engine with transaction date for value

## Test Scenarios
- Verify known staking reward appears in income report
- Verify reporting currency value matches `quantity * historical price`
- Verify non-income transactions are excluded

## Down-stream references
* [CRQ-011: Clear and Actionable Report View](../customer/crq011-viewTaxReport.md)
* [CRQ-013: Understandable Income Schedule](../customer/crq013-incomeSchedule.md)
* [CRQ-018: Compliant Swiss Valuation](../customer/crq018-swissValuation.md)
