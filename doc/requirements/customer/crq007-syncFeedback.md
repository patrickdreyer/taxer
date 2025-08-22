# CRQ-007: Synchronization Feedback
In order to know the application is working correctly  
As a user  
I want to see visible feedback about the sync process as it happens.

## Description
While the backend is busy fetching data from external APIs, the user needs clear, real-time feedback in the UI. This reassures the user that the application has not frozen and provides transparency into what is happening.

## Details
* A visual indicator shows that a sync is globally in progress
* The UI can show status messages for each source (e.g., "Kraken: Syncing...", "Binance: Success", "Coinbase: Error")
* The process should not block me from using other parts of the UI

## Risks
* The sync might take a long time, and I might think the application has crashed
* An error might occur with one source, and I won't know which one failed

## Concept
* The frontend regularly asks the backend for the status of the ongoing sync job
* The UI updates in real-time with the status messages it receives from the backend
* It's like watching a download manager; I can see the progress for each item

## Test Scenarios
* Verify a loading spinner or progress bar appears when a sync starts
* Verify I can see a status update next to each data source in the settings list
* Verify I can still navigate to other pages in the app while a sync is running

## Up-stream references
* [PRQ-03: Automated Data Ingestion](../product/prq03-dataIngestion.md)