import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load dataset
df = pd.read_csv('dataset.csv')

print("Dataset loaded! Shape:", df.shape)
print("Columns:", df.columns.tolist())

# Clean data
df = df.dropna()

# Encode text columns
le = LabelEncoder()
for col in ['department', 'gender', 'education', 'recruitment_channel', 'region']:
    if col in df.columns:
        df[col] = le.fit_transform(df[col].astype(str))

# Features and target
features = ['age', 'department', 'no_of_trainings', 'previous_year_rating',
            'length_of_service', 'KPIs_met_more_than_80', 'awards_won']
target = 'avg_training_score'

X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test accuracy
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"Model Trained Successfully!")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"R2 Score: {r2:.2f}")

# Save model
joblib.dump(model, 'ml_model.pkl')
print("Model saved as ml_model.pkl")
