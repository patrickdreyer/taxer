# PRQ-09: Data Security
In order to protect my sensitive financial information on my computer
As a user
I want the application to store my API keys securely and communicate with external services safely

## Description
Ensure all sensitive data, especially API credentials, is encrypted when stored locally. All external communication to services like exchange APIs must use an encrypted channel (TLS).

## Details
- Sensitive data encrypted before local storage
- All external API calls must use HTTPS (TLS)

## Risks
- Encryption key stored insecurely
- Application uses insecure non-TLS endpoint

## Concept
- Use standard cryptographic library for AES encryption
- Use modern HTTP library that enforces TLS by default

## Test Scenarios
- Inspect local storage file, verify secrets not in plaintext
- Use network monitor, verify outgoing calls use TLS

## Down-stream references
* [CRQ-005: Secure Credential Input](../customer/crq005-secureCredentialInput.md)
* [CRQ-016: Secure Credential Storage](../customer/crq016-secureStorage.md)
* [CRQ-017: Secure Communication with Exchanges](../customer/crq017-secureCommunication.md)
