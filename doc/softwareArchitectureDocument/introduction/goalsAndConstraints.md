# Architectural Goals and Constraints

The architecture is designed to meet the following key goals and adhere to specific constraints.

## Goals
* **Modularity:** The core logic is decoupled from country-specific tax rules. The Swiss valuation logic is a pluggable module, making it possible to add support for other countries in the future.
* **Security:** As the application handles sensitive API credentials, all data at rest must be encrypted, and all external communication must be secure.
* **Usability:** The application must be simple and frictionless for a non-technical user, with no login and automatic data persistence.
* **Maintainability:** A clean separation between the frontend (UI) and the backend (logic) allows for independent development, testing, and maintenance.

## Constraints
* **Technology:** The backend must be written in **Python**. The frontend will be a browser-based UI.
* **Deployment:** The application must run entirely on the user's local machine (localhost). It is not a cloud-based SaaS product.
* **User Model:** The system is designed for a **single user** per instance. There is no multi-user capability.