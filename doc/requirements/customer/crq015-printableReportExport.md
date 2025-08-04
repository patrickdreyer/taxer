# CRQ-015: Printable Report Export
In order to have a clean, non-editable copy for my official records
As a user
I want to download a printable, read-only version of my tax report, like a PDF.

## Description
The user needs a way to create a permanent, read-only artifact of their tax report for archival purposes. While a CSV is good for data analysis, a PDF is better for official submissions and long-term storage, as it preserves the exact visual layout and prevents accidental modification.

## Details
* An "Export as PDF" button is available on the report page
* The downloaded PDF has a clean layout optimized for printing on A4 paper
* The PDF includes clear headers, footers, and page numbers

## Risks
* The PDF layout might break or look ugly with a very large number of assets
* I might not have a PDF viewer installed to open the file

## Concept
* The button tells the backend to render the report into a PDF document
* The visual style of the PDF should be very simple and professional, like an official document

## Test Scenarios
* Verify clicking the "Export as PDF" button saves a `.pdf` file to my computer
* Verify the downloaded PDF opens correctly in a standard browser or PDF reader
* Verify the content in the PDF exactly matches the report shown on the screen

## Up-stream references
* [PRQ-08: Report Export](../product/prq08-reportExport.md)