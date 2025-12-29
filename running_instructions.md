# How to Run the Expense Tracker

This project consists of a Python FastAPI backend, a React frontend, and an optional Streamlit interface.

## Prerequisites
- Python 3.8+
- Node.js & npm

## 1. Backend (FastAPI)
The backend handles the database and API logic.

1. Open a terminal and navigate to the project root:
   ```bash
   cd "/Users/apple/Desktop/Ratan/python/expences tracker"
   ```
2. Activate your virtual environment (if you have one).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   Server will run at `http://127.0.0.1:8000`.

## 2. Frontend (React + Vite)
The modern web interface.

1. Open a **new terminal** window.
2. Navigate to the frontend directory:
   ```bash
   cd "/Users/apple/Desktop/Ratan/python/expences tracker/frontend"
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
   Access the app at the URL shown (usually `http://localhost:5173`).

## 3. Alternative: Streamlit App
If you prefer the standard Python UI:

1. In the project root:
   ```bash
   streamlit run app.py
   ```
