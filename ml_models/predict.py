import joblib
import pandas as pd
from datetime import timedelta

MODEL_PATH = "ml_models/predictive_model.pkl"

def load_model():
    """Loads the trained model from the file."""
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return None

def predict_future_spending(df, days_to_predict=7):
    """
    Uses the loaded model to predict spending for the next few days.
    Args:
        df (pd.DataFrame): The DataFrame with historical data.
        days_to_predict (int): Number of days into the future to predict.
    Returns:
        list: A list of tuples with predicted dates and amounts.
    """
    model = load_model()
    if model is None:
        return []
    
    # Ensure the date column is in datetime format for calculations
    df['date'] = pd.to_datetime(df['date'])
    start_date = df['date'].min()
    
    last_date = df['date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_to_predict + 1)]

    future_days = [(d - start_date).days for d in future_dates]

    predictions = model.predict(pd.DataFrame({'days_since_start': future_days}))

    return list(zip(future_dates, predictions))
