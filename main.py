from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from data_management.database_manager import init_db, add_expense, get_all_expenses, delete_expense, save_and_reset
from chatbot_logic.chatbot_engine import get_chatbot_response_llm, get_chatbot_response_rules
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class ExpenseModel(BaseModel):
    date: str
    category: str
    amount: float
    description: Optional[str] = ""

class ChatRequest(BaseModel):
    prompt: str
    api_key: Optional[str] = ""

@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running"}

@app.get("/expenses")
def get_expenses():
    return get_all_expenses()

@app.post("/expenses")
def add_new_expense(expense: ExpenseModel):
    try:
        add_expense(expense.date, expense.category, expense.amount, expense.description)
        return {"message": "Expense added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/expenses/{expense_id}")
def delete_expense_endpoint(expense_id: int):
    try:
        delete_expense(expense_id)
        return {"message": f"Expense {expense_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        if request.api_key:
            response = get_chatbot_response_llm(request.prompt, request.api_key)
        else:
            response = get_chatbot_response_rules(request.prompt)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)