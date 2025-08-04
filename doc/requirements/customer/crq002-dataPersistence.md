# CRQ-002: Automatic Data Persistence
In order to continue my work between sessions without losing progress
As a user
I want the application to automatically save all my settings and transaction data so that everything is there when I reopen it.

## Description
The user expects that any configuration changes or synchronized data will be persistent by default. The application should not require a manual "Save" action. The backend is responsible for storing all data on the local disk and serving it to the frontend whenever the application is launched.

## Details
* API keys and data sources are remembered after app restart
* Synced transactions are available immediately on next launch
* No manual "Save Configuration" button is needed in the UI

## Risks
* I might not know where the data file is located if I want to back it up
* If the backend crashes while saving, my data file could get corrupted

## Concept
* The application automatically saves any changes I make
* The frontend asks the backend for my data, and the backend reads it from a local file

## Test Scenarios
* Verify syncing 100 transactions, closing the app, and reopening it shows the 100 transactions are still present
* Verify changing a setting, closing the app, and reopening it shows the setting has been saved

## Up-stream references
* [PRQ-01: Single-User Operation](../product/prq01-singleUser.md)