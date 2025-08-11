# CRQ-004: Manage Existing Data Sources
In order to keep my configuration clean and correct
As a user
I want to see a list of all my connected sources and be able to edit or delete them.

## Description
The user needs a central place to see all their configured data sources at a glance. From this view, they should be able to perform management actions like renaming a source for clarity, updating credentials, or removing a source they no longer use.

## Details
* A list or table view of all currently configured sources
* Each item in the list displays its friendly name and type
* Each item has an "Edit" and a "Delete" button

## Risks
* I might delete the wrong data source by accident and lose my configuration

## Concept
* It's a settings page that shows all my connections
* The "Delete" button has a confirmation step to prevent mistakes
* The "Edit" button reuses the same form as adding a source, but with the data filled in

## Test Scenarios
* Verify I can see my added Kraken account in a list
* Verify clicking "Delete" and then "Confirm" removes the source from the list
* Verify I can click "Edit" on a source and successfully change its display name

## Up-stream references
* [PRQ-02: Data Source Management](../product/prq02-dataSources.md)