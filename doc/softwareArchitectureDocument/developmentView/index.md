This view describes the organization of the source code, development environment, and build processes required to develop and maintain the application.

## Source Code Organization

The project will be organized into a monorepo containing distinct directories for the backend, frontend, and documentation.

```plaintext
/swiss-crypto-tax-helper
|
|-- /backend                # Python backend source code
|   |-- /app
|   |   |-- /api            # API endpoint definitions (e.g., using FastAPI)
|   |   |-- /services       # Business logic (ingestion, reporting, etc.)
|   |   |-- /strategies     # Pluggable valuation strategies (e.g., swiss_strategy.py)
|   |   |-- /core           # Core components (config, security, persistence)
|   |   |-- main.py         # Server entry point
|   |-- requirements.txt
|
|-- /frontend               # Frontend source code (e.g., React, Vue, Svelte)
|   |-- /src
|   |-- package.json
|
|-- /doc                    # All documentation
|   |-- /requirements
|   |   |-- /product
|   |   |-- /customer
|   |-- /softwareArchitectureDocument
|   |   |-- introduction.md
|   |   |-- goalsAndConstraints.md
|   |   |-- logicalView.md
|   |   |-- processView.md
|   |   |-- developmentView.md
|   |   |-- physicalView.md
|
|-- .gitignore
```

## Backend Development
The backend is responsible for all business logic and data handling.

- **Language:** **Python** (version 3.11+ is recommended).
- **Web Framework:** **FastAPI** is chosen for its high performance, modern asynchronous capabilities, and automatic API documentation generation, which simplifies development and testing.
- **Key Libraries:**
    - `duckdb`: For the data persistence layer.
    - `pandas`: For data manipulation and analysis.
    - `ccxt`: A unified library for connecting to numerous cryptocurrency exchanges.
    - `pydantic`: For data validation and settings management (included with FastAPI).
- **Dependency Management:** Dependencies will be managed using `pip` and tracked in the `backend/requirements.txt` file.

## Frontend Development
- **Language:** **TypeScript** is recommended over plain JavaScript for its strong typing, which improves code quality and maintainability, especially for a data-heavy application.
- **Framework:** A modern JavaScript framework such as **Svelte** or **React** is recommended to build a responsive and maintainable Single Page Application (SPA). The final choice is to be determined.
- **Dependency Management:** Dependencies will be managed using `npm` (or `yarn`) and tracked in the `frontend/package.json` file.

## Build & Packaging
- **Process:** The frontend code will be built into a set of static files (HTML, CSS, JS).
- **Packaging Tool:** A tool like **Electron** will be used to package the static frontend assets, the Python backend runtime, and all necessary dependencies into a single executable file for different operating systems (e.g., Windows, macOS).