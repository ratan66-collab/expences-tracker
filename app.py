import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from data_management.database_manager import init_db, add_expense, get_all_expenses, save_and_reset, get_current_expenses, delete_expense
from ml_models.predict import predict_future_spending
from chatbot_logic.chatbot_engine import get_chatbot_response_llm, get_chatbot_response_rules
import json
import requests
import os

# --- Initialization and Setup ---
# Initialize the database on application startup.
init_db()

# Set Streamlit page configuration for a wider layout.
st.set_page_config(layout='wide')
st.title("💸 PENNY WI$E")
st.header("Your Personal Expense Tracker with AI Insights")

# Use st.session_state to store chat history and other session-specific data.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_date" not in st.session_state:
    st.session_state.last_date = date.today()
if "refresh_dashboard" not in st.session_state:
    st.session_state.refresh_dashboard = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    st.header("Add a New Expense")
    with st.form(key='expense_form', clear_on_submit=True):
        
        input_date = st.date_input("Date", st.session_state.last_date)
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        category = st.selectbox("Category", ["Food", "Transport", "Bills", "Entertainment", "Other"])
        description = st.text_input("Description (Optional)")

        submit_button = st.form_submit_button("Add Expense")

        if submit_button:
            # Call the database function to add the new expense.
            add_expense(str(input_date), category, amount, description)
            st.success("Expense added successfully!")
            st.session_state.messages.append({"role": "user", "content": f"Added ${amount:.2f} to {category}."})
            # Update the session state with the last selected date
            st.session_state.last_date = input_date
            st.session_state.refresh_dashboard = True

    # New button to save and reset data for a new day
    st.markdown("---")
    if st.button("Start New Day"):
        save_and_reset()
        st.success("Current expenses saved and cleared for a new day!")
        # Clear the chat history and reset the date as well for a fresh start
        st.session_state.messages = []
        st.session_state.last_date = date.today()
        st.session_state.refresh_dashboard = True
    
    # New button to reset current day's expenses
    if st.button("Reset Day"):
        # This will delete the data from the 'expenses' table
        save_and_reset(reset_only=True)
        st.success("Current day's expenses have been reset to 0.")
        st.session_state.messages = []
        st.session_state.last_date = date.today()
        st.session_state.refresh_dashboard = True

    # --- API Key Input for Chatbot ---
    st.markdown("---")
    st.subheader("Unlock AI Chatbot")
    # This input field stores the API key in the session state.
    api_key_input = st.text_input("Enter your Gemini API key:", type="password", value=st.session_state.api_key)
    
    # Update the session state only if the input has changed.
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.success("API key accepted!")
    elif st.session_state.api_key:
        st.success("API key is already set.")

col_graphs, col_predictions = st.columns([2, 1])

with col_graphs:
    st.header("📊 Your Spending Dashboard")
    
    if st.session_state.refresh_dashboard:
        st.session_state.refresh_dashboard = False
        st.rerun()

    # Get all expenses, including saved history and current unsaved expenses
    all_expenses_data = get_all_expenses()

    if not all_expenses_data:
        st.info("No expenses recorded yet. Add some to see your dashboard!")
    else:
        # Convert the retrieved data into a pandas DataFrame for analysis.
        df = pd.DataFrame(all_expenses_data, columns=['id', 'date', 'category', 'amount', 'description'])
        df['date'] = pd.to_datetime(df['date'])
        
        # --- Separate the current day's expenses for the total metric ---
        current_day_expenses = get_current_expenses()
        df_current = pd.DataFrame(current_day_expenses, columns=['id', 'date', 'category', 'amount', 'description'])
        # Display the total spending metric.
        total_spending = df_current['amount'].sum() if not df_current.empty else 0
        st.metric("Total Spending Today", f"${total_spending:,.2f}")

        st.subheader("Spending by category")
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        fig_pie = px.pie(
            category_spending,
            values='amount',
            names='category',
            title="Total Expenses by category",
            hole=0.3
            )
        st.plotly_chart(fig_pie, use_container_width = True)

        st.subheader("Daily Spending Trend")
        df['day'] = df['date'].dt.date
        daily_spending = df.groupby('day')['amount'].sum().reset_index()
        fig_daily = px.bar(
            daily_spending,
            x="day",
            y="amount",
            title="Daily Total Expenses",
            text_auto=True
        )
        st.plotly_chart(fig_daily, use_container_width=True)

        st.subheader("Weekly Spending Trend")
        df["week"] = df["date"].dt.isocalendar().week
        weekly_spending = df.groupby("week")["amount"].sum().reset_index()
        fig_bar = px.bar(
            weekly_spending,
            x="week",
            y="amount",
            title="Weekly Total Expenses",
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("Monthly Spending Trend")
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_spending = df.groupby('month')['amount'].sum().reset_index()
        fig_monthly = px.bar(
            monthly_spending,
            x='month',
            y='amount',
            title='Monthly Total Expenses',
            text_auto=True
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    # --- New Section: Expense List and Deletion ---
    st.markdown("---")
    st.header("📝 All Recorded Expenses")
    if all_expenses_data:
        # Create a display DataFrame for the table
        df_display = df.copy()
        df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')
        df_display = df_display[['date', 'category', 'amount', 'description', 'id']]

        # Iterate through the DataFrame to create rows with a delete button
        st.dataframe(df_display, hide_index=True)

        st.subheader("Delete an Expense")
        delete_col1, delete_col2 = st.columns([1, 10])
        with delete_col1:
            expense_id_to_delete = st.selectbox("Select ID to Delete", df_display['id'].tolist())
        with delete_col2:
            st.markdown(" ") # Add a bit of space
            if st.button("Delete Selected Expense"):
                try:
                    # Call the function from your database_manager.py
                    delete_expense(expense_id_to_delete)
                    st.success(f"Expense with ID {expense_id_to_delete} has been deleted.")
                    # Force a refresh to update the dashboard and table
                    st.session_state.refresh_dashboard = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not delete expense: {e}")
    else:
        st.info("No expenses to display. Add some using the form in the sidebar.")


with col_predictions:
    st.header("🔮 AI Prediction & Chatbot")

    expenses_data = get_all_expenses()
    df_for_pred = pd.DataFrame(expenses_data, columns=['id', 'date', 'category', 'amount', 'description'])

    if len(df_for_pred) > 5:
        st.subheader("Future Spending Prediction")
        predictions = predict_future_spending(df_for_pred)
        if predictions:
            pred_df = pd.DataFrame(predictions, columns =["Date", "Predicted Amount"])
            st.write(pred_df)
        else:
            st.warning("Model not trained . Please run 'python ml_models/train_model.py' first.")

    else:
        st.info("Add at least 5 Expenses to enable future predicitons.")


    st.subheader("Talk to your Financial Assistant")

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ask a Question about your spending..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)

        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Use LLM-powered chatbot if API key is provided, otherwise use the rule-based one.
                if st.session_state.api_key:
                    response = get_chatbot_response_llm(user_prompt, st.session_state.api_key)
                else:
                    response = get_chatbot_response_rules(user_prompt)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Instructions to run the app:
# cd "/Users/apple/Downloads/python_ratan/expences tracker"
# source venv/bin/activate
# python3 ml_models/train_model.py
# python3 -m streamlit run app.py


# api key : AIzaSyAXNRc791JCwInOsnm0WR-rWfQVb3ttwmo