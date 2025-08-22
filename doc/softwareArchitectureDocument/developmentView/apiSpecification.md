# API Specification (High-Level)
This document defines the high-level RESTful API contract between the React frontend and the Python backend. All communication occurs over `localhost`, and the API serves as the single entry point for the frontend to access data and trigger business logic.

## General Principles
- **Base URL:** All endpoints are relative to the server's base URL (e.g., `http://localhost:8000/api/v1`).
- **Authentication:** None. As a local single-user application, no authentication tokens are required.
- **Data Format:** All request and response bodies use the `application/json` format.
- **Error Handling:** The API uses standard HTTP status codes to indicate success or failure. Error responses will contain a JSON body with a `detail` key explaining the error.
- **Type Safety:** TypeScript interfaces are generated from the API schema to ensure type safety between frontend and backend.

## Frontend API Integration
The React frontend integrates with the backend API using the following patterns:

- **HTTP Client:** Modern `fetch` API with TypeScript wrappers for type safety
- **State Management:** TanStack Query for server state management, caching, and background updates
- **Error Handling:** Centralized error handling with user-friendly error messages
- **Loading States:** Automatic loading state management for better user experience
- **Type Generation:** TypeScript types generated from FastAPI's OpenAPI schema

```typescript
// Example TypeScript interface for API responses
interface DataSource {
  id: string;
  name: string;
  type: 'exchange' | 'wallet';
  status: 'active' | 'inactive' | 'error';
  lastSync?: string;
}

// Example API service function
const useDataSources = () => {
  return useQuery({
    queryKey: ['dataSources'],
    queryFn: () => fetch('/api/v1/sources').then(res => res.json() as DataSource[])
  });
};
```

---
## Data Sources (`/sources`)
Endpoints for managing user-configured data sources.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/sources` | `GET` | Retrieves a list of all configured data sources. |
| `/sources` | `POST` | Creates a new data source. The request body contains the name, type, and credentials. |
| `/sources/{sourceId}` | `GET` | Retrieves the details of a single data source. |
| `/sources/{sourceId}` | `PUT` | Updates the details (e.g., name, credentials) of an existing data source. |
| `/sources/{sourceId}` | `DELETE` | Deletes a data source. |

---
## Transactions (`/transactions`)
Endpoints for viewing transactions and managing data synchronization.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/transactions` | `GET` | Retrieves a list of all transactions. Supports filtering via query parameters (e.g., `?asset=BTC`, `?sourceId=1`, `?startDate=...`, `?endDate=...`). |
| `/transactions/sync`| `POST` | Initiates the data synchronization process for all sources. This is a non-blocking, asynchronous operation. |
| `/transactions/sync/status` | `GET` | Retrieves the real-time status of the ongoing synchronization process. |

---
## Reports (`/reports`)
Endpoints for generating and exporting tax reports.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/reports/{year}` | `GET` | Generates and retrieves the tax report for the specified year as a JSON object for display in the UI. |
| `/reports/{year}/export` | `GET` | Generates a downloadable report file. The format is specified via a query parameter (e.g., `?format=csv`, `?format=pdf`). |
