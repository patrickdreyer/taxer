# PRQ 02: Data Source Management
In order to connect the application to my financial accounts  
As a user  
I want to securely add, view, update, and remove my exchange API keys and public wallet addresses through the user interface

### Description
Offer a user interface where the user can securely add, view, update, and delete data sources, which include read-only exchange API keys and public wallet addresses.

### Details
- UI has dedicated section for source management
- Input forms provided for source name, API key, secret
- Wallet address fields for asset type and address

### Risks
- User enters incorrect API keys causing connection failure
- API keys with wrong permissions pose security risk

### Concept
- Simple CRUD interface for data sources
- Credentials encrypted before local save

### Test Scenarios
- Verify new exchange can be added and appears
- Verify new wallet address can be added
- Verify data source can be deleted
- Verify API secrets are masked in UI

### Down-stream references
* [CRQ-003: Add a New Data Source](../customer/crq003-addDataSource.md)
* [CRQ-004: Manage Existing Data Sources](../customer/crq004-manageDataSources.md)
* [CRQ-005: Secure Credential Input](../customer/crq005-secureCredentialInput.md)
