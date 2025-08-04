# PRQ-10: Swiss Tax Rules & Valuation
In order to get an accurate and compliant report for Switzerland
As a Swiss user
I want the application to automatically apply Swiss-specific tax rules and valuations to my report.

## Description
Apply Swiss-specific tax logic to the generic reports. This includes valuing all assets in Swiss Francs (CHF) and ensuring the report format is compatible with the *Wertschriftenverzeichnis*. The valuation engine must prioritize the official end-of-year rates (*Kurswerte*) from the Swiss Federal Tax Administration (ESTV). For assets not on the official list, it must use a reliable market data API as a fallback. This engine provides all values for the "Reporting Currency" fields in other PRQs.

## Details
- All report values calculated in CHF
- Backend valuation module uses two-step ESTV-first process
- Report to indicate if value is from ESTV or market rate
- Structure and naming conventions follow *Wertschriftenverzeichnis*

## Risks
- Internal ESTV rate list is outdated
- Fallback API unavailable or provides inaccurate data

Concept
- A "Swiss Strategy" module that can be swapped for other countries
- Core function `getValue(asset, date)` encapsulates logic
- Function returns price and source used (ESTV/Market)

## Test Scenarios
- Verify BTC valuation on Dec 31st matches ESTV rate
- Verify niche coin gets price from fallback API
- Verify Wealth report displays price source for each asset

## Down-stream references
* [CRQ-011: Clear and Actionable Report View](../customer/crq011-viewTaxReport.md)
* [CRQ-012: Understandable Wealth Schedule](../customer/crq012-wealthSchedule.md)
* [CRQ-013: Understandable Income Schedule](../customer/crq013-incomeSchedule.md)
* [CRQ-018: Compliant Swiss Valuation](../customer/crq018-swissValuation.md)
