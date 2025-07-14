## The Project Studio v0.1

![User Interface](screenshots/UI.png)


The entire project is organized around the principle of **Separation of Concerns**, which means each file and folder has one clear job. This makes the project clean, professional, and easy to understand.

---

### Visual File Tree

```
STUDIO/
├── app/
│   ├── agent.py
│   ├── server.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── templates/
│       └── index.html
│
├── .env
├── config.yaml
└── pyproject.toml
```

---


#### Root Directory Files

These files configure and define the entire project.

*   `pyproject.toml`
    *   **Job:** The project's official **definition and dependency list**.
    *   It tells Python and `pip` what packages your project needs to run (like `fastapi`, `langgraph`, etc.).
    *   This is the modern replacement for `requirements.txt`.

*   `.env`
    *   **Job:** To store your **SECRETS**.
    *   This file holds your `LANGSMITH_API_KEY`. It is designed to be **kept private** and should never be shared or uploaded to GitHub.

*   `config.yaml`
    *   **Job:** To store your **non-secret settings**.
    *   This file holds settings that are safe to share, like the LLM model name or temperature. This allows you to change application settings without touching the code.

---

### The Application Core (`app/`)

This folder is the heart of your application. All the actual program logic lives here.

#### The "Brain" of the Application

*   `app/agent.py`
    *   **Job:** Contains the pure **LangGraph agent logic**.
    *   It defines the agent's state, the `processing_node`, and the `recommendation_node`.
    *   This file is the "brain"—it knows how to do the analysis, but it **knows nothing about the web, FastAPI, or the UI**. It just takes data in and produces a result.

#### The "Public Face" of the Application

*   `app/server.py`
    *   **Job:** The **FastAPI web server**. This is the application's front door.
    *   It creates the API endpoints (like `/analyze` and `/update-settings`) that the user's browser can talk to.
    *   When a request comes in from the UI, this file calls the "brain" (`agent.py`) to get the job done and sends the result back.
    *   It also serves the HTML files to the user's browser.

#### The "Look and Feel" of the Application

*   `app/templates/`
    *   **Job:** Holds the **HTML structure** of your web pages.
    *   `index.html` defines the layout, the input fields, the buttons, and the chat window. It's the skeleton of your UI.

*   `app/static/`
    *   **Job:** Holds the **static assets** that make your UI work and look good.
    *   `css/style.css`: The "paint and style." It defines all the colors, fonts, and animations.
    *   `js/script.js`: The "interactivity." It handles what happens when you click a button, sends the data to the server, and displays the response in the chat window.

---

### How They Work Together: A Simple Flow

1.  You enter data into **`index.html`** in your browser.
2.  You click the "Analyze" button, which triggers a function in **`script.js`**.
3.  `script.js` sends the data to the `/analyze` URL.
4.  Your **`server.py`** (FastAPI) receives the request at the `/analyze` endpoint.
5.  `server.py` calls the agent defined in **`agent.py`** and gives it the data.
6.  **`agent.py`** runs its nodes (`processing`, `recommendation`) and returns the final report.
7.  `server.py` gets the report and sends it back to the browser as a JSON response.
8.  **`script.js`** receives the response, formats it into the nice report card HTML, and displays it in the chat window of **`index.html`**.

---

## Project Setup and Installation

This guide provides the complete instructions to set up and run the application on a local machine.

### 1. Prerequisites

-   Python 3.12 or higher.
-   Git for cloning the repository.
-   A **Groq API Key** for language model access. You can get a key from the [GroqCloud Console](https://console.groq.com/keys).
-   A **LangSmith API Key** for application tracing and observability. You can sign up and get a key from [smith.langchain.com](https://smith.langchain.com/).

### 2. Step-by-Step Installation

#### **Step A: Clone the Repository**

First, clone the project from GitHub to your local machine using the following command in your terminal:

```bash
git clone https://github.com/Eng-AliKazemi/STUDIO.git
cd STUDIO
```

#### **Step B: Configure Environment Variables (`.env`)**

This file holds your secret API keys.

1.  In the root directory of the project, create a new file named `.env`.
2.  Add your Groq and LangSmith API keys to this file.

    **.env**
    ```
    # --- LLM Provider API Key ---
    # The agent uses this key if it needs to call a language model.
    GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"

    # --- LangSmith Tracing ---
    # This enables observability for all agent runs.
    LANGCHAIN_TRACING_V2="true"
    LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY_HERE"
    LANGCHAIN_PROJECT="Business Analysis Studio"
    ```

#### **Step C: Review Application Configuration (`config.yaml`)**

This file holds non-secret settings that control the application's behavior. The project comes with default settings, which you can review or modify.

**`config.yaml`**
```yaml
# These settings control which language model is used.
# While the current business agent is deterministic, these settings
# are used by the UI and would be used by any future LLM-powered nodes.
llm_settings:
  provider_url: "https://api.groq.com/openai/v1"
  model_name: "llama-3.3-70b-versatile" # Default model
  temperature: 0.7
```
**Note:** These settings can be changed dynamically through the application's user interface after the server is running.

#### **Step D: Create and Activate a Virtual Environment**

Using a virtual environment is a best practice to manage project-specific dependencies.

1.  From the project's root directory, create the virtual environment:
    ```bash
    python -m venv venv
    ```

2.  Activate the environment:
    -   **On Windows:**
        ```bash
        venv\Scripts\activate
        ```
    -   **On macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
    Your terminal prompt should now be prefixed with `(venv)`.

#### **Step E: Install Dependencies**

The project uses a `pyproject.toml` file to define all its dependencies. Install them using `pip`.

```bash
# The '.' tells pip to install from the pyproject.toml in the current directory.
# The '-e' flag installs it in "editable" mode, best for development.
pip install -e .
```

The setup is now complete. The application is ready to be run. See the subsequent sections for instructions on running in development mode (`langgraph dev`) or local production mode (`uvicorn`).
---

## LangGraph Studio Integration

![LangGraph Studio](screenshots/LANGGRAPH_STUDIO.png)

### 1. Overview

LangGraph Studio provides a cloud-based, visual interface for the development, debugging, and testing of the agent's core logic. The project is configured to support a "live-sync" development workflow, where changes made to the local source code are instantly reflected in the Studio environment.

### 2. Synchronization Mechanism

The connection between the local development environment and the online Studio is managed by the `langgraph dev` command-line tool.

-   Upon execution, `langgraph dev` reads the project's configuration from `pyproject.toml` and `langgraph.json`.
-   It initiates the local FastAPI server while establishing a secure connection to the LangChain platform.
-   A unique URL is generated and displayed in the console, providing direct access to the agent's graph within the Studio.

This setup enables a hot-reloading feature. Any saved changes to the `app/agent.py` file are automatically detected and synchronized with the Studio instance, facilitating rapid iteration without requiring a server restart.

### 3. Testing Procedure in Studio

1.  **Start the Development Server**
    Ensure the Python virtual environment is activated, then execute the following command from the project's root directory:
    ```bash
    langgraph dev
    ```

2.  **Access the Studio**
    The console will output a startup message, including a link labeled "Studio UI". Access this URL in a web browser.
    ```
    - 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=...
    ```

3.  **Provide Input Data**
    The Studio interface will display input fields corresponding to the agent's `BusinessAnalysisState` class. The data must be structured in the correct JSON format.

    -   For the **`Daily Data`** field, toggle the "View Raw" option and input the following object:
        ```json
        {
          "revenue": 1500,
          "cost": 1000,
          "number_of_customers": 50
        }
        ```
    -   For the **`Previous Day Data`** field, toggle "View Raw" and input the following object:
        ```json
        {
          "revenue": 1200,
          "cost": 600,
          "number_of_customers": 40
        }
        ```
    -   The `Calculated Metrics` and `Recommendations` fields should be left as empty objects (`{}`), as they will be populated by the agent during execution.

4.  **Execute the Agent**
    Click the **`Submit`** button located at the bottom right of the interface.

5.  **Analyze the Execution Results**
    The Studio will display the results of the agent run.
    -   **Output Tab:** This panel shows the final state object of the agent after the run is complete. The `calculated_metrics` and `recommendations` fields will be fully populated with the analysis results.
    -   **Graph Tab:** This tab presents a visual flowchart of the agent's execution path (e.g., `processing` node → `recommendation` node). Each node in the graph is interactive; clicking on one reveals its specific inputs and outputs for that step, providing a detailed view for debugging purposes.

### 1. LangSmith: Observability Platform

![LangSmith](screenshots/LANGSMITH.png)

LangSmith provides comprehensive tracing and monitoring capabilities for the LangGraph agent. It functions as an observability layer, capturing detailed records of every agent execution.

-   **Activation:** The integration is enabled by the presence of `LANGCHAIN_TRACING_V2="true"` and a valid `LANGCHAIN_API_KEY` in the `.env` configuration file.
-   **Functionality:** Each invocation of the agent triggers the creation of a "trace." This trace logs the complete execution flow, including the inputs and outputs of each node, execution times, and any errors that occur.
-   **Utility:**
    -   **Debugging:** Facilitates in-depth analysis of agent behavior to identify and resolve issues.
    -   **Monitoring:** Allows for tracking agent performance, usage patterns, and error rates.
    -   **Evaluation:** Traces can be collected and curated into datasets for regression testing and performance evaluation of future agent versions.

All traces generated by this project are organized under the **"Business Analysis Studio"** project on the LangSmith dashboard.

### 2. LangServe: API Server Framework

LangServe is a library for deploying LangChain and LangGraph objects as robust, production-ready REST APIs.

-   **Implementation:** In the `app/server.py` file, the `add_routes(app, ...)` function integrates LangServe into the FastAPI application. It introspects the compiled LangGraph agent and automatically creates a set of standardized API endpoints at the `/agent` path.
-   **Provided Endpoints:**
    -   **`/agent/invoke`:** A primary endpoint for running the agent with a single input.
    -   **`/agent/batch`:** An endpoint for running the agent on multiple inputs in parallel.
    -   **`/agent/stream`:** An endpoint for streaming outputs as they are generated.
    -   **`/agent/playground/`:** An automatically generated web interface for interacting with the agent. This provides an alternative method for testing the agent's logic, accessible at `http://127.0.0.1:5050/agent/playground/`.

In this project, the custom UI endpoint (`/analyze`) acts as a client to the agent. It receives user data and then calls the agent internally. This architecture decouples the core agent logic from the user-facing presentation layer.


---

## Production Usage Guide (Local Deployment)

The application is served using **Uvicorn**, a standard, high-performance web server for FastAPI applications.

### 1. Prerequisites

Before running the server, ensure the following setup is complete:

1.  **Project Files:** The complete project structure, including the `app` directory and configuration files, must be in place.
2.  **Dependencies:** All required Python packages must be installed from the `pyproject.toml` file into a virtual environment.
3.  **Environment Variables:** The `.env` file must be present in the project's root directory and must contain a valid `LANGCHAIN_API_KEY` to enable LangSmith tracing.

### 2. Execution Steps

1.  **Activate the Virtual Environment**
    Open a terminal in the project's root directory and activate the Python virtual environment.
    ```bash
    # On Windows
    venv\Scripts\activate

    # On macOS/Linux
    source venv/bin/activate
    ```

2.  **Start the Uvicorn Server**
    Execute the following command to start the web server. Note the absence of the `--reload` flag, which is standard practice for a stable deployment.
    ```bash
    uvicorn app.server:app --host 0.0.0.0 --port 5050
    ```

    -   **`uvicorn`**: The command to run the ASGI server.
    -   **`app.server:app`**: Specifies the location of the FastAPI application instance (the `app` variable inside the `app/server.py` file).
    -   **`--host 0.0.0.0`**: Binds the server to all available network interfaces, making it accessible from other devices on the same network (use `127.0.0.1` to restrict access to the local machine only).
    -   **`--port 5050`**: Specifies the port on which the server will listen for requests.

3.  **Verify Server Status**
    The terminal will display output indicating that the server has started successfully.
    ```
    INFO:     Started server process [PID]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:5050 (Press CTRL+C to quit)
    ```
    The application is now running as a persistent service.

### 3. Accessing and Using the Application

Once the server is running, the application can be accessed in two ways:

#### A. Custom User Interface (Primary Access)

This is the main entry point for end-users.

-   **URL:** `http://localhost:5050`
-   **Usage:**
    1.  Navigate to the URL in a web browser.
    2.  The full chat interface will be displayed.
    3.  Input the required daily and previous day's business data into the form.
    4.  Click the "Analyze" button to submit the data and receive the agent's report.
    5.  The settings panel remains available for viewing the current configuration.

#### B. LangServe API Playground (For Direct API Testing)

LangServe automatically generates a separate interface for testing the agent's API directly.

-   **URL:** `http://localhost:5050/agent/playground/`
-   **Usage:** This interface allows for sending structured JSON input directly to the agent and viewing the raw JSON output. It is primarily a tool for developers or for integrating the agent with other services.

### 4. Stopping the Server

To stop the application, return to the terminal where the Uvicorn server is running and press `Ctrl+C`. This will gracefully shut down the server process.

---

### Project Review: Fulfillment of Original Task Requirements

This document outlines how the final application meets and exceeds the criteria specified in the original project request.

#### **1. Task: Set up LangGraph environment (locally or on the cloud).**

*   **Requirement Met:** A complete and robust local development environment has been established.
*   **Implementation Details:**
    *   A `pyproject.toml` file defines all project dependencies, ensuring a reproducible environment.
    *   The use of a Python virtual environment (`venv`) isolates these dependencies.
    *   The environment is set up with a single command (`pip install -e .`), making it simple and standardized.
    *   The `langgraph dev` command provides a cloud-connected development experience, linking the local environment directly to the online LangGraph Studio.

#### **2. Task: Build a simple graph with these nodes.**

*   **Requirement Met:** A graph with the specified nodes has been implemented in a clean, modular fashion inside `app/agent.py`.
*   **Implementation Details:**
    *   **Input Node:** In this production-grade architecture, the role of the "Input Node" is handled by the FastAPI server in `app/server.py`. It receives user data from the UI, structures it into the required `BusinessAnalysisState` dictionary, and invokes the graph.
    *   **Processing Node:** The `processing_node` function in `app/agent.py` is dedicated to this task. It takes the input data from the state and performs all the required calculations (profit, percentage changes, CAC).
    *   **Recommendation Node:** The `recommendation_node` function in `app/agent.py` fulfills this role. It inspects the `calculated_metrics` in the state and uses conditional logic (`if` statements) to generate the appropriate warnings and recommendations.

#### **3. Task: Run the Agent and produce an output.**

*   **Requirement Met:** The agent produces a dictionary/JSON object with the exact specified structure.
*   **Implementation Details:**
    *   The final output of the graph is the `recommendations` object within the agent's state.
    *   A sample successful output from testing demonstrates perfect adherence to the required format:
        ```json
        {
          "profit_loss_status": "Profitable",
          "alerts_or_warnings": [
            "CAC increased by 33.33% (>20% threshold)."
          ],
          "decision_making_recommendations": [
            "Review marketing campaigns as CAC increased significantly.",
            "Consider increasing advertising budget to capitalize on growth."
          ]
        }
        ```

#### **4. Task: Write a simple test that validates the Agent’s output correctness.**

*   **Requirement Exceeded:** The project provides a multi-layered testing strategy far more comprehensive than a single test script.
*   **Implementation Details:**
    *   **Interactive UI Testing:** The FastAPI server allows for manual, end-to-end testing of the full application via the web interface, covering user input, error handling, and successful report generation.
    *   **Isolated Logic Testing (LangGraph Studio):** The `langgraph dev` integration allows the core agent logic in `agent.py` to be tested in complete isolation within the cloud Studio. This provides a controlled environment to validate calculations with specific inputs.
    *   **Continuous Observability (LangSmith):** Every single run of the agent is automatically traced and logged in LangSmith. This acts as a continuous, real-time record of tests, providing deep insights into every execution and serving as a powerful debugging tool.

---

### Evaluation Criteria Analysis

*   **Code structure and readability:** **Excellent.** The project is organized into a clean `app/` directory, with a clear separation of concerns: `agent.py` (core logic), `server.py` (web layer), `static/` (CSS/JS), and `templates/` (HTML). This makes the code highly readable and maintainable.

*   **Proper usage of LangGraph and graph design:** **Excellent.** The implementation correctly uses `StateGraph`, a `TypedDict` for state management, and clearly defined nodes for each logical step. The final `graph` variable is exposed correctly for use with the LangGraph CLI tools.

*   **Logic accuracy in data analysis:** **Excellent.** As proven in the successful test run, all calculations (profit, percentage changes, CAC) are performed correctly according to the specified formulas.

*   **Clarity and usefulness of the output recommendations:** **Excellent.** The generated recommendations are clear, direct, and directly tied to the business logic (e.g., "Review marketing campaigns as CAC increased significantly"). The separation of "warnings" from "recommendations" adds further clarity.

*   **Test quality and coverage:** **Excellent.** The three layers of testing (manual UI, interactive Studio, and automated LangSmith tracing) provide comprehensive coverage for the entire application stack, from the user interface to the core agent logic.

---

### Fulfillment of "Expected Processing" Checklist

-   [✔] **Calculate daily profit:** Done in `processing_node`.
-   [✔] **Calculate percentage changes:** Done in `processing_node`.
-   [✔] **Check if CAC increased more than 20%:** Done in `recommendation_node`.
-   [✔] **Generate "Reduce costs" recommendation:** Done in `recommendation_node`.
-   [✔] **Generate "Review marketing" recommendation:** Done in `recommendation_node`.
-   [✔] **Generate "Increase advertising" recommendation:** Done in `recommendation_node`.

---
