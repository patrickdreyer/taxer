# CRQ-005: Secure Credential Input
In order to trust the application with my sensitive information
As a user
I want to see that my API secrets are hidden from view to protect them from shoulder surfing.

## Description
The user needs visual confirmation that the application is handling their sensitive information with care. Masking secret fields by default is a standard security practice that builds user trust and protects against casual observation.

## Details
* API Secret fields are displayed as password inputs (showing dots `••••••••`)
* When editing an existing source, the secret field is always masked by default

## Risks
* I might not be able to easily check if I typed a long secret correctly

## Concept
* The secret field works like a password field on a website
* There should be a little "eye" icon to let me see what I typed if I need to

## Test Scenarios
* Verify the API secret field shows dots as I type
* Verify when I edit a source, the secret field is pre-filled with dots, not the actual secret
* Verify clicking a "show" icon next to the field reveals the secret, and clicking "hide" masks it again

## Up-stream references
* [PRQ-02: Data Source Management](../product/prq02-dataSources.md)
* [PRQ-09: Data Security](../product/prq09-dataSecurity.md)