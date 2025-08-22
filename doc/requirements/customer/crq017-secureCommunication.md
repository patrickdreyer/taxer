# CRQ-017: Secure Communication with Exchanges
In order to protect my data when it's sent over the internet  
As a user  
I want the application to use secure, encrypted connections when communicating with external exchanges and services.

## Description
The user needs to trust that when the application connects to an exchange like Binance or Kraken, the connection is secure and private, just like their web browser connecting to an e-banking website. The backend is responsible for ensuring all its outgoing network requests use TLS (HTTPS).

## Details
* All communication with external APIs for exchanges or price data uses HTTPS
* The application will fail with a clear network error if a secure connection cannot be established

## Risks
* My local network configuration (like a corporate proxy) might interfere with secure connections, causing the app to fail

## Concept
* When the app talks to an exchange, it uses the same "padlock" security as my web browser
* The connection is a private, encrypted tunnel between the app on my computer and the exchange's server

## Test Scenarios
* Use a network monitoring tool during a data sync to verify that all traffic to exchange APIs is over TLS (HTTPS on port 443)
* Verify the app shows a clear error message if a DNS issue or firewall prevents a secure connection

## Up-stream references
* [PRQ-09: Data Security](../product/prq09-dataSecurity.md)