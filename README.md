# 🤖 Autonomous Data Analyst: Multi-Agent Text-to-SQL API

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)](#)
[![LangGraph](https://img.shields.io/badge/Framework-LangGraph-orange)](https://github.com/langchain-ai/langgraph)
[![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-green)](https://groq.com/)

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [The Business Problem](#-the-business-problem)
- [System Architecture](#-system-architecture)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Local Deployment (Docker)](#-local-deployment-docker)
- [Project Structure](#-project-structure)

---

## 📌 Project Overview
This project implements a fully autonomous, production-ready AI microservice that translates natural language questions into complex, executable SQL queries. 

Unlike traditional Text-to-SQL tools that crash when an LLM hallucinates a column name or makes a syntax error, this system features a **stateful, self-correcting agentic loop**. It writes the code, tests it in a secure sandbox, reads its own traceback logs if it fails, and patches the SQL before returning the final business insight to the user.

## 💼 The Business Problem
Enterprise business users often wait days for Data Engineering teams to write custom SQL queries for simple ad-hoc data requests. Standard LLMs attempt to solve this but fail in production because they:
1. Hallucinate non-existent tables.
2. Cannot handle complex `JOIN` logic without trial and error.
3. Return raw code instead of synthesized business answers.

**The Solution:** An orchestrated multi-agent workflow that utilizes **Table-Augmented Generation (TAG)** to fetch dynamic schema metadata, paired with a deterministic execution environment to validate the LLM's logic in real-time.

---

## 🏗️ System Architecture (LangGraph + FastAPI)

The core reasoning engine is built using **LangGraph** to manage state between three distinct AI personas:

1. **The SQL Writer (Actor):** Powered by `Llama-3.3-70B`. Ingests the user prompt and the injected database schema to generate a raw SQLite query.
2. **The DB Executor & Reviewer (Critic):** A deterministic Python node that attempts to execute the query. 
   * *Conditional Routing:* If execution succeeds, the raw data is passed forward. If it fails (e.g., `sqlite3.OperationalError`), the exact error string is appended to the graph's state, and the workflow is routed *back* to the SQL Writer for correction (capped at 3 retries to prevent infinite loops).
3. **The Data Analyst:** Takes the raw, mathematical result set from the database and synthesizes it into a concise, human-readable business insight.

**The MLOps Wrapper:** The entire LangGraph state machine is wrapped in a **FastAPI** backend and containerized using **Docker**, ensuring high-performance, stateless HTTP request handling suitable for cloud deployment.

---

## 💾 Database Schema (Simulated Enterprise Data)

To prove the system's ability to handle multi-table relational logic, the FastAPI startup event automatically generates an `ecommerce.db` SQLite database with the following schema:

* **`Customers`**: `customer_id` (PK), `name`, `segment`, `signup_date`
* **`Products`**: `product_id` (PK), `name`, `category`, `price`
* **`Orders`**: `order_id` (PK), `customer_id` (FK), `order_date`, `status`
* **`OrderDetails`**: `detail_id` (PK), `order_id` (FK), `product_id` (FK), `quantity`

---

## 🔌 API Reference

### `POST /ask`
The primary endpoint for interacting with the Data Analyst Agent.

**Request Payload:**
```json
{
  "question": "Which product category generated the most total revenue?"
}
