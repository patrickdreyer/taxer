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
|-- /frontend               # React + TypeScript frontend source code
|   |-- /src
|   |   |-- /components     # Reusable React components
|   |   |-- /pages          # Page-level components
|   |   |-- /hooks          # Custom React hooks
|   |   |-- /services       # API client and data fetching
|   |   |-- /types          # TypeScript type definitions
|   |   |-- /utils          # Utility functions
|   |   |-- App.tsx         # Main application component
|   |   |-- main.tsx        # Application entry point
|   |-- /public             # Static assets
|   |-- package.json
|   |-- tsconfig.json       # TypeScript configuration
|   |-- vite.config.ts      # Vite build configuration
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
The frontend provides a modern, responsive web interface for interacting with the application.

- **Language:** **TypeScript** for strong typing, improved code quality, and better maintainability, especially crucial for financial data handling.
- **Framework:** **React 18+** with functional components and hooks for building a responsive and maintainable Single Page Application (SPA).
- **Build Tool:** **Vite** for lightning-fast development with hot module replacement and optimized production builds.
- **Key Libraries:**
    - `@tanstack/react-query`: For efficient API state management and caching
    - `react-router-dom`: For client-side routing
    - `recharts` or `d3.js`: For financial data visualization and charts
    - `tailwindcss`: For utility-first CSS styling
    - `@hookform/react-hook-form`: For form handling and validation
    - `zod`: For runtime type validation
- **Development Tools:**
    - `eslint` and `prettier`: For code quality and formatting
    - `vitest`: For unit testing React components
    - `@testing-library/react`: For component testing
- **Dependency Management:** Dependencies managed using `npm` and tracked in `frontend/package.json`.

## Build & Packaging
- **Frontend Build:** Vite builds the React/TypeScript code into optimized static files (HTML, CSS, JS) with code splitting and tree shaking for optimal performance.
- **Development Server:** Vite provides a fast development server with hot module replacement for rapid development iterations.
- **Production Build:** Optimized builds with minification, compression, and modern ES module support.
- **Packaging Tool:** **Electron** will be used to package the static frontend assets, the Python backend runtime, and all necessary dependencies into a single executable file for different operating systems (Windows, macOS, Linux).
- **Build Pipeline:** 
    1. Frontend build via `npm run build` (Vite)
    2. Backend packaging with dependencies
    3. Electron packaging for desktop distribution