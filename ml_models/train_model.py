import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib

def train_and_save_model(df):
    """
    Trains a Linear Regression model on expense data and saves it.
    Args:
        df (pd.DataFrame): DataFrame with 'date' and 'amount' columns.
    """
    if df.empty or len(df) < 2:
        print("Not enough data to train the model.")
        return

    # Prepare data: Convert date to a numerical format (e.g., days since start)
    df['date'] = pd.to_datetime(df['date'])
    start_date = df['date'].min()
    df['days_since_start'] = (df['date'] - start_date).dt.days.astype(int)

    X = df[['days_since_start']]
    y = df['amount']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save the trained model to a file
    joblib.dump(model, 'ml_models/predictive_model.pkl')
    print("Model trained and saved as 'predictive_model.pkl'.")
    return model

if __name__ == '__main__':
    # Dummy data for demonstration. In your app, this would be your actual data.
    data = {
        'date': ['2025-01-01', '2025-01-05', '2025-01-10', '2025-01-15', '2025-01-20', '2025-01-25', '2025-01-30', '2025-02-05'],
        'amount': [50, 60, 55, 75, 80, 70, 90, 85]
    }
    dummy_df = pd.DataFrame(data)
    train_and_save_model(dummy_df)

# python3 ml_models/train_model.py