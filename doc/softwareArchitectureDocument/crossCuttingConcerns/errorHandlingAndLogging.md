
# Error Handling & Logging Strategy
This document defines the application's strategy for managing errors and recording diagnostic information. The primary goals are to provide a graceful and informative experience for the user when issues arise and to facilitate effective debugging for developers.

## Guiding Principles
- **Fail Gracefully:** The application must never crash due to a predictable error (e.g., network failure, invalid user input, external API issues). It should catch exceptions and continue to operate where possible.
- **Informative User Feedback:** Errors presented to the user must be clear, concise, and actionable. The user should understand what went wrong and what they can do about it, without being exposed to technical jargon.
- **No Sensitive Data Exposure:** Under no circumstances should error messages or log files ever contain sensitive information, such as API keys or secrets.

## API Error Handling (Backend)
The backend will use a standardized approach to communicate errors to the frontend via its REST API.

- **Mechanism:** Standard HTTP status codes will be used to indicate the class of error.
- **Format:** All error responses (4xx and 5xx status codes) will return a JSON body with a consistent structure: `{"detail": "A human-readable error message."}`.
- **Common Status Codes:**
    - `400 Bad Request`: Used for malformed requests.
    - `422 Unprocessable Entity`: Used for validation errors in the request body (e.g., an invalid API key format).
    - `500 Internal Server Error`: For unexpected, unhandled exceptions in the backend logic.
    - `503 Service Unavailable`: When an external dependency (like an exchange API) is down or unreachable.

## Error Presentation (Frontend)
The frontend is responsible for translating API error responses into user-friendly notifications.

- **Non-blocking Errors:** For transient or minor issues (e.g., a single data source failing to sync), non-intrusive **notification toasts** will be used (e.g., "Failed to sync Kraken: Exchange API is temporarily unavailable.").
- **Blocking Errors:** For critical issues that require user intervention (e.g., an invalid API key that prevents all syncing for a source), a more prominent message will be displayed in the relevant UI context (e.g., next to the data source configuration) with clear instructions.

## Logging Strategy
Logging is for developer diagnostics and will not be shown to the user.

- **Library:** The backend will use Python's standard `logging` module.
- **Location:** Logs will be written to a plain text file (`app.log`) in a standard application data directory to be easily accessible if the user needs to provide it for support.
- **Level:** The default logging level for production releases will be `INFO`.
- **Format:** Log entries will be structured to include a timestamp, log level, and the message (e.g., `2025-08-04 02:18:40,123 - INFO - Starting data sync for 3 sources...`).
- **Rotation:** A simple log rotation policy will be implemented (e.g., keeping the last 5 log files of 1MB each) to prevent the log file from growing indefinitely.