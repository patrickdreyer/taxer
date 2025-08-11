# CRQ-003: Add a New Data Source
In order to connect the application to my accounts
As a user
I want to fill out a simple form to add a new exchange API key or a public wallet address.

## Description
The user needs a clear and unambiguous way to add new data sources one by one. The process should be self-explanatory, guiding the user to provide the correct information for each source type. The frontend provides the form, and the backend validates and securely stores the submitted credentials.

## Details
* Form includes `Source Type` dropdown (e.g., Binance, Kraken, ETH Wallet)
* Form fields adapt based on selected `Source Type`
* Fields for a friendly `Display Name` for easy identification
* "Save" button to confirm and add the new source

## Risks
* I might not know where to find my API keys on the exchange
* I might enter the wrong key and not realize it until the sync fails

## Concept
* An "Add New Source" button opens a form
* The form is like a settings panel where I configure a new connection
* The form checks my input for obvious errors before saving

## Test Scenarios
* Verify I can select "Binance" and see fields for API Key and Secret
* Verify I can select "Ethereum Wallet" and see a field for a public address
* Verify saving a new source adds it to my list of configured sources

## Up-stream references
* [PRQ-02: Data Source Management](../product/prq02-dataSources.md)