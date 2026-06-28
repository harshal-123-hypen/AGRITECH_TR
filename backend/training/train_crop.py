import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# ----------------------------
# Load Dataset
# ----------------------------
df = pd.read_csv("crop_data.csv")

# ----------------------------
# Encode Input Features
# ----------------------------
district_encoder = LabelEncoder()
df["district"] = district_encoder.fit_transform(df["district"])

# ----------------------------
# Encode Target Crop
# ----------------------------
crop_encoder = LabelEncoder()
df["crop"] = crop_encoder.fit_transform(df["crop"])

# ----------------------------
# Input Features
# ----------------------------
X = df[[
    "district",
    "rainfall",
    "temperature",
    "area",
    "market_price"
]]

# ----------------------------
# Target
# ----------------------------
y = df["crop"]

# ----------------------------
# Split Dataset
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ----------------------------
# Train Model
# ----------------------------
model = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Accuracy
# ----------------------------
accuracy = model.score(X_test, y_test)

print("Accuracy :", accuracy)

# ----------------------------
# Save Model
# ----------------------------
joblib.dump(model, "../models/crop_model.pkl")

joblib.dump(crop_encoder, "../models/crop_encoder.pkl")

joblib.dump(district_encoder, "../models/district_encoder.pkl")

print("Crop Model Saved Successfully!")