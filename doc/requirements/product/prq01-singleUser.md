# PRQ-01: Single-User Operation
In order to simplify application setup and usage on my local machine  
As a user running this application for my own tax purposes  
I want to run the application without needing to create an account or log in

## Description
Operate as a local, single-user application without requiring user registration or a login system. All data and configurations belong to the implicit single user of the instance.

## Details
- Application starts directly into main UI
- All data and settings stored in local files
- Data belongs implicitly to single user
- No authentication or session management needed

## Risks
- Anyone with computer access can view financial data
- Local data files risk corruption or deletion

## Concept
- Application state managed locally
- Startup loads data from default local path

## Test Scenarios
- Verify application opens without login prompt
- Verify app reload restores previous state

## Down-stream references
* [CRQ-001: Frictionless Startup](../customer/crq001-frictionlessStartup.md)
* [CRQ-002: Automatic Data Persistence](../customer/crq002-dataPersistence.md)
