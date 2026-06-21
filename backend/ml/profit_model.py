import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load dataset
df = pd.read_csv("crop_data.csv")

print(df.head())

# Convert text columns to numbers
crop_encoder = LabelEncoder()
district_encoder = LabelEncoder()

df["crop"] = crop_encoder.fit_transform(df["crop"])
df["district"] = district_encoder.fit_transform(df["district"])

# Input features
X = df[[
    "crop",
    "district",
    "rainfall",
    "temperature",
    "area",
    "market_price"
]]

# Output column
y = df["profit"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
score = model.score(X_test, y_test)
print("Accuracy:", score)

# Save model
joblib.dump(model, "profit_model.pkl")

print("Model saved successfully!")