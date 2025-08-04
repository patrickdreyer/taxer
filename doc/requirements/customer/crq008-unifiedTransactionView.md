# CRQ-008: Unified Transaction View
In order to get a complete overview of my activity
As a user
I want to see all my transactions from every source in a single, chronological list.

## Description
The user needs a central dashboard to view and verify all their transactions. The data must be presented in a clean, readable table that consolidates information from different exchanges and wallets into a consistent format. The frontend presents this table, populated by normalized data from the backend.

## Details
* A table view showing date, type, assets, amount, and source for each transaction
* Transactions are sorted by date by default, from newest to oldest
* Data from different exchanges and wallets appears seamlessly in the same list

## Risks
* I might have thousands of transactions, and the page could become slow or crash
* The transaction types from different exchanges might be confusingly named or inconsistent

## Concept
* The main page of the app is a big table of all my crypto activity
* The backend standardizes all different transaction types into simple categories like "Trade" or "Deposit"
* The frontend uses a "virtualized" list to display thousands of rows without slowing down

## Test Scenarios
* Verify transactions from my Binance and Kraken accounts appear in the same list
* Verify the list is initially sorted with the most recent transaction at the top

## Up-stream references
* [PRQ-04: Transaction Dashboard](../product/prq04-transactionHistory.md)