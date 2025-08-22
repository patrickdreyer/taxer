# CRQ-013: Understandable Income Schedule
In order to declare my crypto income correctly  
As a user  
I want the income report to show a simple list of all my taxable events with their respective values at the time I received them.

## Description
The user needs the "Income" section of the report to be a clear and trustworthy list of all taxable events, such as staking rewards or airdrops. The frontend must render the income data provided by the backend in a clean, tabular format that specifies the date, type, asset, and its value in the reporting currency when it was received.

## Details
* Income section is a table with clear headers: "Date", "Type", "Asset", "Quantity Received", "Value at Receipt"
* A grand total of all taxable income is displayed prominently at the bottom
* Each row represents a single taxable event

## Risks
* I might not understand why a certain transaction is considered "income"
* The value at the time of receipt might seem wrong to me if the market was volatile

## Concept
* This part of the report is a simple log of all the times I earned new crypto during the year
* It provides a clear total income figure that I need to declare on my tax forms

## Test Scenarios
* Verify the table contains a row for each known staking reward transaction
* Verify the "Value at Receipt" for a row is correctly calculated by multiplying the quantity by the historical price on that specific day
* Verify a "Grand Total" row at the bottom correctly sums up the "Value at Receipt" column

## Up-stream references
* [PRQ-07: Income Report Content](../product/prq07-incomeReport.md)
* [PRQ-10: Swiss Tax Rules & Valuation](../product/prq10-swissTax.md)