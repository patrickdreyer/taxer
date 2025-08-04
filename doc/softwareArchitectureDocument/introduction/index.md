# Introduction

## Purpose
This document describes the software architecture for the **Swiss Crypto Tax Helper**, a local desktop application designed to simplify cryptocurrency tax reporting for private investors in Switzerland. It details the key architectural components, their interactions, and the design decisions made to satisfy the defined requirements.

## Scope
The application's scope includes:
* Connecting to external exchange APIs and public wallet addresses.
* Ingesting and normalizing transaction data.
* Applying Swiss-specific valuation rules using official ESTV rates.
* Generating wealth and income reports suitable for tax declaration.
* Storing all user data locally and securely.

## References
* Product Requirements (PRQs) located in `doc/requirements/product/`.
* Customer Requirements (CRQs) located in `doc/requirements/customer/`.
* Technical Requirements (TRQs) located in `doc/requirements/technical/`.
