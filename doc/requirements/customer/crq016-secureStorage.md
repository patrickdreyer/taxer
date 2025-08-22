# CRQ-016: Secure Credential Storage
In order to trust the application with my API keys  
As a user  
I want to know that my credentials are stored in an encrypted format on my computer.

## Description
The user needs assurance that the API keys they enter are not stored in a way that is easily readable by other programs or people with access to the computer's file system. The backend is solely responsible for encrypting this sensitive data before saving it to the local database or file, and decrypting it only when needed to connect to an exchange.

## Details
* Application documentation clearly states that sensitive data is encrypted at rest
* There is no way to open the local database/file and see API keys in plaintext
* The application handles all encryption and decryption automatically

## Risks
* I might lose access to my data if the encryption key gets corrupted or lost
* I might not believe it's actually encrypted unless the app communicates this fact

## Concept
* My API secrets are scrambled with a key before they are saved to disk
* Only the application knows the key to unscramble them when it needs to sync my data
* It's like storing a locked document; you can see the file, but you can't read its contents without the key

## Test Scenarios
* Verify that locating the local data file and opening it in a text/database editor does not show API keys in plaintext
* Verify the application's "Help" or "About" section contains a statement about local data encryption

## Up-stream references
* [PRQ-09: Data Security](../product/prq09-dataSecurity.md)