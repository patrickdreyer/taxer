# CRQ-011: Clear and Actionable Report View
In order to confidently use the data in my tax return
As a user
I want the generated report to be easy to read and understand, clearly separating wealth and income.

## Description
The user needs the final report to be presented in a way that is unambiguous and directly usable. The backend sends a fully calculated and structured report to the frontend, which must then render it with clear headings, tables, and totals to give the user confidence in the data before they transcribe it into their official tax forms.

## Details
* Report has clear top-level headings for "Wealth" and "Income"
* Each section has a summary total (e.g., "Total Wealth on Dec 31")
* Numbers are formatted for readability (e.g., with thousand separators)
* The source of valuation (e.g., ESTV or Market) is shown for each asset

## Risks
* The report layout could be confusing, and I might mix up the numbers
* I might not trust a number if I don't know where it came from

## Concept
* The report is like a final, printable summary page
* It's designed for maximum clarity, not for data manipulation
* Key figures and totals are highlighted visually (e.g., bold text)

## Test Scenarios
* Verify the report view contains both "Wealth" and "Income" sections
* Verify the "Total Wealth" figure is clearly visible and correct
* Verify each asset in the wealth report has a "Price Source" column

## Up-stream references
* [PRQ-05: Tax Report Generation](../product/prq05-taxReport.md)
* [PRQ-06: Wealth Report Content](../product/prq06-wealthReport.md)
* [PRQ-07: Income Report Content](../product/prq07-incomeReport.md)
* [PRQ-10: Swiss Tax Rules & Valuation](../product/prq10-swissTax.md)