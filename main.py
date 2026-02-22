import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Load API key from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Autonomous Text-to-SQL API")

# Initialize LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# --- Database Setup (Runs on API Startup) ---
@app.on_event("startup")
def setup_database():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.executescript('''
    DROP TABLE IF EXISTS OrderDetails; DROP TABLE IF EXISTS Orders;
    DROP TABLE IF EXISTS Products; DROP TABLE IF EXISTS Customers;
    CREATE TABLE Customers (customer_id INTEGER PRIMARY KEY, name TEXT, segment TEXT, signup_date DATE);
    CREATE TABLE Products (product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
    CREATE TABLE Orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date DATE, status TEXT);
    CREATE TABLE OrderDetails (detail_id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER);
    ''')
    categories, segments, statuses = ['Electronics', 'Clothing'], ['Retail', 'VIP'], ['Completed', 'Pending']
    for i in range(1, 10):
        c.execute("INSERT INTO Products VALUES (?, ?, ?, ?)", (i, f'Product_{i}', random.choice(categories), 50.0))
        c.execute("INSERT INTO Customers VALUES (?, ?, ?, ?)", (i, f'Customer_{i}', random.choice(segments), '2025-01-01'))
        c.execute("INSERT INTO Orders VALUES (?, ?, ?, ?)", (i, i, '2026-02-10', random.choice(statuses)))
        c.execute("INSERT INTO OrderDetails VALUES (?, ?, ?, ?)", (i, i, i, 2))
    conn.commit()
    conn.close()

def get_schema():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = "\n".join([row[0] for row in c.fetchall() if row[0]])
    conn.close()
    return schema

# --- LangGraph Setup ---
class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: str
    db_result: str
    error: str
    iterations: int
    final_answer: str

def sql_writer(state):
    prompt = ChatPromptTemplate.from_template(
        "You are an expert SQL developer. Write a valid SQLite query to answer the user's question.\n"
        "Schema:\n{schema}\n\nQuestion: {question}\n\n"
        "If you previously got an error, fix your code based on this message: {error}\n"
        "Return ONLY the SQL query. Do not include markdown formatting."
    )
    chain = prompt | llm
    response = chain.invoke({"schema": state["schema"], "question": state["question"], "error": state.get("error", "")})
    clean_sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    return {"sql_query": clean_sql, "iterations": state.get("iterations", 0) + 1}

def db_executor(state):
    query = state["sql_query"]
    try:
        conn = sqlite3.connect('ecommerce.db')
        c = conn.cursor()
        c.execute(query)
        result = c.fetchall()
        conn.close()
        return {"db_result": str(result), "error": ""}
    except Exception as e:
        return {"error": str(e), "db_result": ""}

def data_analyst(state):
    prompt = ChatPromptTemplate.from_template(
        "You are a data analyst. The user asked: {question}\n"
        "The database returned this raw data: {db_result}\n\n"
        "Write a clear, concise business answer based on this data. Do not mention SQL or databases."
    )
    chain = prompt | llm
    answer = chain.invoke({"question": state["question"], "db_result": state["db_result"]})
    return {"final_answer": answer.content}

def router(state):
    if state.get("error") and state.get("iterations") < 3:
        return "sql_writer"
    return "data_analyst"

workflow = StateGraph(AgentState)
workflow.add_node("sql_writer", sql_writer)
workflow.add_node("db_executor", db_executor)
workflow.add_node("data_analyst", data_analyst)
workflow.set_entry_point("sql_writer")
workflow.add_edge("sql_writer", "db_executor")
workflow.add_conditional_edges("db_executor", router)
workflow.add_edge("data_analyst", END)
agent_app = workflow.compile()

# --- API Endpoints ---
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_database(request: QueryRequest):
    try:
        schema = get_schema()
        initial_state = {"question": request.question, "schema": schema, "iterations": 0, "error": ""}
        result = agent_app.invoke(initial_state)
        return {
            "business_insight": result["final_answer"],
            "generated_sql": result["sql_query"],
            "retries_taken": result["iterations"] - 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))