# CRQ-006: Initiate Data Synchronization
In order to keep my financial data up-to-date  
As a user  
I want to press a single button to fetch all the latest transactions from my connected sources.

## Description
The user requires a simple, one-step action to trigger a full data refresh from all configured exchanges and wallets. This action, initiated from the frontend, tells the backend to start its data gathering process.

## Details
* A prominent "Sync" or "Refresh" button is always accessible in the UI
* Clicking the button starts the data fetching process immediately
* The button should be disabled while a sync is already in progress

## Risks
* I might accidentally click the button multiple times and start multiple syncs
* I might not know if the button click actually worked

## Concept
* The button is the main trigger for the backend's data collection work
* The frontend sends a single command to the backend to start syncing all sources

## Test Scenarios
* Verify clicking the "Sync" button sends a request to the backend to start ingestion
* Verify the button becomes greyed out or disabled after being clicked, until the sync is finished

## Up-stream references
* [PRQ-03: Automated Data Ingestion](../product/prq03-dataIngestion.md)