This document outlines the architectural decisions and strategies designed to protect user data and ensure the integrity of the application. Security is a primary architectural goal, focusing on data at rest, data in transit, and credential management.

## Data at Rest Encryption
The primary security risk is the exposure of user API keys stored on the local disk.

- **Requirement:** All sensitive data, particularly API credentials, must be encrypted before being written to the local database file.
- **Implementation:** The Python backend will use the **`cryptography`** library, a standard and well-vetted choice for encryption in Python.
- **Mechanism:** The encryption key will not be stored directly in the application's files. Instead, the backend will leverage the host operating system's native secret management service for key storage and retrieval.
    - **macOS:** Keychain Access
    - **Windows:** Windows Credential Manager
    - **Linux:** Secret Service API / Freedesktop Secrets
    This approach provides a secure key storage mechanism without requiring the user to manage a separate password for the application.
- **Scope:** Encryption will be applied to the `credentials` column in the `dataSources` table. General transaction data will not be encrypted at the field level to ensure high query performance, as it is not considered sensitive PII.

## Data in Transit Security
- **External Communication:** All outgoing API calls from the backend to external services (exchanges, price data providers) **must** use a secure, encrypted channel.
    - **Protocol:** TLS 1.2 or higher is enforced.
    - **Implementation:** Standard libraries like `requests` and `ccxt` handle this by default, but the application will not be configured to allow insecure connections.
- **Internal Communication:** Communication between the browser-based frontend and the Python backend occurs over the `localhost` network interface. This traffic does not leave the user's machine and is not exposed to external network snooping.

## Credential Management in Memory
- **Requirement:** Sensitive data like API keys should have a minimal lifetime in memory.
- **Implementation:** The backend will only decrypt an API key at the moment it is needed to make a request to an external exchange. The decrypted key will not be stored in long-lived variables, cached, or written to any log files.

## Application Integrity
- **Requirement:** The user must be able to verify that the application has not been tampered with.
- **Implementation:** For production releases, the final packaged application executable for each operating system will be **code-signed**. This allows the OS to verify the publisher's identity and guarantee the application's integrity.