# CRQ-001: Frictionless Startup
In order to get started quickly without any hassle    
As the sole user of this application on my computer    
I want to open the app and immediately see the main screen without needing to log in.

## Description
The user expects the application to feel like a local tool, not a cloud service. This experience is defined by immediate access upon launch. The frontend application should launch and display the main interface, and the backend should be ready to serve it without requiring an authentication step.

## Details
* Launching the application opens the main dashboard directly
* No login, registration, or password prompt is presented at startup
* Backend starts without an authentication gate for the local frontend

## Risks
* Anyone with access to my computer can open the app and view my financial data

## Concept
* The application feels like a standard desktop tool, not a web service
* The frontend and backend are a matched pair running locally that trust each other

## Test Scenarios
* Verify that running the application executable opens the UI to the main dashboard
* Verify there is no login screen presented by the frontend

## Up-stream references
* [PRQ-01: Single-User Operation](../product/prq01-singleUser.md)