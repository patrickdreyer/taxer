# CRQ-018: Compliant Swiss Valuation
In order to file a fully compliant tax return  
As a Swiss taxpayer  
I want the application to automatically use the official ESTV end-of-year prices for my crypto assets.

## Description
The user needs absolute confidence that the application's calculations adhere to local tax law. This requirement ensures the backend's valuation engine prioritizes official data from the Swiss Federal Tax Administration (ESTV) over standard market data. The frontend must then clearly label the source of each price in the final report, providing transparency and building user trust.

## Details
* The final tax report explicitly states the source of the price for each asset (e.g., "ESTV Rate", "Market Rate")
* The currency used throughout the report is clearly labeled as CHF
* Values for major cryptocurrencies match the published ESTV numbers for the selected tax year

## Risks
* I might not know if the app's list of official ESTV rates is up-to-date
* For a coin not on the official list, I might not trust the "Market Rate" the app has chosen

## Concept
* The app has a built-in "official price list" from the government for my tax year
* It always checks that list first before looking up a price on a public market data site
* It's like having a tax expert built-in who knows which prices are the correct ones to use

## Test Scenarios
* Generate a report and verify the value for BTC exactly matches the official ESTV rate for that year
* Verify that an asset not on the ESTV list still gets a value and is explicitly labeled as "Market Rate"
* Verify all currency symbols shown in the final report are "CHF"

## Up-stream references
* [PRQ-10: Swiss Tax Rules & Valuation](../product/prq10-swissTax.md)
* [PRQ-06: Wealth Report Content](../product/prq06-wealthReport.md)
* [PRQ-07: Income Report Content](../product/prq07-incomeReport.md)