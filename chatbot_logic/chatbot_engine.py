import google.generativeai as genai
import pandas as pd
from data_management.database_manager import get_all_expenses
import requests
import json
import os

def get_chatbot_response_rules(user_prompt):
    """
    A simple rule-based chatbot for when no API key is provided.
    This provides a fallback for basic queries.
    """
    prompt = user_prompt.lower()
    
    if "hello" in prompt or "hi" in prompt:
        return "Hello! I am a financial assistant. I can help you with your spending data."
    elif "spending" in prompt and ("total" in prompt or "how much" in prompt):
        expenses_data = get_all_expenses()
        df = pd.DataFrame(expenses_data, columns=['id', 'date', 'category', 'amount', 'description'])
        total = df['amount'].sum()
        return f"Your total spending so far is ${total:,.2f}."
    elif "thanks" in prompt or "thank you" in prompt:
        return "You're welcome! Let me know if you have any other questions."
    else:
        return "I can't answer that with my current knowledge. Please add a Gemini API key to unlock the AI chatbot."

def get_chatbot_response_llm(user_prompt, api_key):
    """
    Sends the user's prompt to the Gemini API and returns the response.
    Includes financial data in the prompt for context.
    """
    try:
        # Use the provided API key to configure the model dynamically.
        genai.configure(api_key=api_key)

        # Set up the model with the new, faster model name.
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # The key change is here: using the gemini-1.5-flash-latest model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        all_expenses = get_all_expenses()
        df = pd.DataFrame(all_expenses, columns=['id', 'date', 'category', 'amount', 'description'])
        
        # Craft a comprehensive prompt with financial context.
        system_prompt = (
            "You are a friendly and helpful financial assistant. "
            "Your goal is to provide insights and answer questions based on the user's expense data. "
            "Analyze the data provided and give a concise, easy-to-understand response. "
            "You can talk about spending trends, categorize expenses, or offer general tips. "
            "Do not provide any financial advice."
        )

        user_query_with_data = f"{system_prompt}\n\nUser's prompt: {user_prompt}\n\nUser's raw expense data: {df.to_string()}"
        
        response = model.generate_content(user_query_with_data)
        
        if response and response.text:
            return response.text
        else:
            return "I'm sorry, I couldn't generate a response. Please try again."

    except Exception as e:
        return f"An error occurred: {e}"

# python3 ml_models/train_model.py