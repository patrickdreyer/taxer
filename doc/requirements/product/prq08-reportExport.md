# PRQ-08: Report Export
In order to save a copy of my tax data for my personal records or to share with a tax advisor  
As a user  
I want to download the complete generated tax report as a single CSV file

## Description
Provide a function to download the complete, generated tax report as a single CSV file.

## Details
- "Download CSV" button on report view
- Generates CSV with wealth and income tables
- Prompts user to save file

## Risks
- CSV formatted incorrectly, fails to open in software
- Data truncated or misrepresented

## Concept
- Backend endpoint generates CSV string
- Returns with `Content-Disposition` header for download

## Test Scenarios
- Verify downloaded CSV opens in Excel, Numbers, LibreOffice
- Verify data in CSV matches UI report
- Verify file has descriptive name

## Down-stream references
* [CRQ-014: Report Export for Record-Keeping](../customer/crq014-reportExport.md)
* [CRQ-015: Printable Report Export](../customer/crq015-printableReportExport.md)
