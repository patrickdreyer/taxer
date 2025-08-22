# CRQ-012: Understandable Wealth Schedule
In order to fill out my tax forms easily and accurately  
As a user  
I want the wealth report to be presented as a clear schedule, matching the format of my official tax forms.

## Description
The user needs the "Wealth" section of the report to be a trustworthy and well-structured table. The frontend must render the wealth data provided by the backend in a clear, tabular format with specific, well-defined columns that directly correspond to the information required by the official tax schedule.

## Details
* Wealth section is a table with clear headers: "Asset", "Quantity", "Value per Unit", "Total Value"
* A grand total of all wealth is displayed prominently at the bottom of the table
* Each row represents a single cryptocurrency held at the end of the year

## Risks
* I might not be sure if the "Total Value" for an asset is calculated correctly
* A coin I hold might be missing from the list if its balance was calculated incorrectly

## Concept
* This part of the report is a direct digital copy of the *Wertschriftenverzeichnis* my tax software asks for
* It's a simple list of what I owned and what it was worth on the last day of the year

## Test Scenarios
* Verify the table contains a row for each crypto asset held on December 31st
* Verify the "Total Value" for a row is correctly calculated by multiplying "Quantity" and "Value per Unit"
* Verify a "Grand Total" row at the bottom correctly sums up the "Total Value" column

## Up-stream references
* [PRQ-06: Wealth Report Content](../product/prq06-wealthReport.md)
* [PRQ-10: Swiss Tax Rules & Valuation](../product/prq10-swissTax.md)