# 🤖 Autonomous Data Analyst: Multi-Agent Text-to-SQL System

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Framework-LangGraph-orange)](https://github.com/langchain-ai/langgraph)
[![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-green)](https://groq.com/)

## 📌 Project Overview
This project implements a fully autonomous, multi-agent system that translates natural language questions into complex, executable SQL queries. Unlike traditional Text-to-SQL tools, this system features a **self-correcting loop** where an agentic reviewer identifies execution errors, reads the traceback, and prompts the SQL writer to fix the query automatically.



## 🏗️ Architectural Deep Dive
To bridge the gap between unstructured human language and rigid relational databases, I designed a multi-agent graph using **LangGraph**:

* **The SQL Writer (Acter):** Utilizes **Llama-3.3-70B** to interpret user intent and map it against a dynamic database schema (Table-Augmented Generation).
* **The DB Executor & Reviewer (Critic):** Executes generated SQL against a simulated e-commerce SQLite database. If a syntax or logic error occurs (e.g., `OperationalError`), this node captures the error logs and routes the workflow back to the Writer for a re-try.
* **The Data Analyst:** Once the data is successfully retrieved, this agent synthesizes the raw result sets into concise, business-ready insights.

## 💾 Big Data Simulation
I engineered a complex relational database (`ecommerce.db`) specifically for this project, featuring:
* **Customers:** Segmented data (Retail, Wholesale, VIP).
* **Orders & OrderDetails:** Multi-table relationship requiring complex joins for profitability analysis.
* **Products:** Categorized inventory with pricing metadata.

## 🚀 Key Skills Showcased
* **Agentic AI Orchestration:** Implementing stateful graphs and conditional routing in LangGraph.
* **Data Architecture:** Designing relational schemas and handling dynamic metadata retrieval for LLM context.
* **Prompt Engineering:** Developing specialized system instructions for distinct agent personas to minimize hallucination.

## 🛠️ How to Run
1. Open the `.ipynb` file in Google Colab.
2. Obtain a free API key from [Groq Console](https://console.groq.com/).
3. Run all cells to launch the **Gradio Web Interface**.
