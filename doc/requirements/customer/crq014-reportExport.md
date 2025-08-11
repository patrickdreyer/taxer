# CRQ-014: Report Export for Record-Keeping
In order to keep my tax data for my records or share it
As a user
I want to download my complete tax report as a CSV file.

## Description
The user needs the ability to export the generated data into a common, non-proprietary format. This allows for long-term archival, personal analysis in spreadsheet software, or sharing with a tax professional. The frontend provides a simple button that requests the file from the backend, which serves the generated CSV to the user's browser.

## Details
* A clear "Download CSV" button is visible on the report page
* The downloaded file contains both the wealth and income tables
* The filename is descriptive (e.g., "Swiss-Tax-Report-2025.csv")

## Risks
* The CSV file might be formatted incorrectly and not open properly in my spreadsheet program
* I might not be able to find where the file was saved on my computer

## Concept
* It works like downloading a bank statement from an e-banking website
* The button just gives me a file with all the data I see on the screen

## Test Scenarios
* Verify clicking the download button saves a file to my computer
* Verify the file opens correctly in Microsoft Excel, Google Sheets, or LibreOffice Calc
* Verify the data in the CSV file exactly matches the report shown on the screen

## Up-stream references
* [PRQ-08: Report Export](../product/prq08-reportExport.md)