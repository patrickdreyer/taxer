This view describes the deployment topology. For this application, the topology is simple.

- The entire system runs on a **single machine (the user's computer)**.
- The application will be packaged into a single executable file (e.g., using **Electron** or a similar wrapper).
- When launched, this executable starts two main processes:
    - The **Python Backend Server** process.
    - The **Browser UI** process, which loads the frontend code and points to the backend's local API.
- All communication happens over `localhost`, requiring no external network access except for fetching data from exchange/price APIs.
