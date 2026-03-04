# 📊 Financial AI Copilot (Containerized)

An advanced AI assistant designed to analyze and query complex financial documents using **GPT-5**, **MongoDB**, and the **Model Context Protocol (MCP)**. This version is fully containerized for easy deployment and scaling.

## 🚀 Overview

This application uses a **RAG (Retrieval-Augmented Generation)** architecture. By utilizing **Docker**, we decouple the database and the MCP server from the application logic, allowing the AI to interact with data through a standardized protocol.

### Key Features

* **Local MongoDB:** Persistent storage running in a Docker container.
* **MCP Server:** A dedicated container acting as the secure bridge between the LLM and your financial data.
* **Agentic Logic:** Uses **LangGraph** to handle multi-step financial reasoning.
* **Vector Search:** Native MongoDB vector indexing for high-speed document retrieval.

---

## 🛠️ Infrastructure Stack

* **Database:** MongoDB (Docker Image)
* **Protocol:** Model Context Protocol (MCP) Server (Docker Image)
* **LLM:** OpenAI GPT-5
* **Orchestration:** LangChain / LangGraph
* **Containerization:** Docker & Docker Compose

---

## ⚙️ Setup & Installation

### 1. Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.
* An OpenAI API Key.

### 2. Clone & Prepare

```bash
git clone https://github.com/your-username/financial-ai-copilot.git
cd financial-ai-copilot

```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# MongoDB Config
MONGO_URL=mongodb://mongodb:27017/financial_db
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password

# MCP & AI Config
OPENAI_API_KEY=your_api_key_here
MCP_SERVER_URL=http://mcp-server:8080

```

### 4. Deploy with Docker Compose

This command will pull the images and start the MongoDB instance, the MCP server, and the application simultaneously.

```bash
docker-compose up -d

```

---

## 🚢 Service Architecture

| Service | Port | Description |
| --- | --- | --- |
| **MongoDB** | `27017` | Stores document embeddings and metadata. |
| **MCP Server** | `8080` | Standardized interface for the AI to query the DB. |
| **Copilot App** | `8501` | The Streamlit-based UI for interacting with the AI. |

---

## 📈 Usage

1. **Ingest Financial Data:**
Place your PDFs in the `/data` folder and run:
```bash
docker exec -it financial-app python ingest.py

```


2. **Access the Copilot:**
Open your browser and navigate to `http://localhost:8501`.

---

## 🛡️ Security & Evaluation

* **Isolation:** All services run in a private Docker network.
* **MCP Protocol:** Ensures the LLM only accesses data through predefined tools, preventing prompt injection attacks on the database.

---