from flask import Flask, request, jsonify
import joblib

# Create Flask app
app = Flask(__name__)

# Load trained ML model
model = joblib.load("profit_model.pkl")


# Home route
@app.route("/")
def home():
    return "Agriculture ML API is running!"


# Prediction route
@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    crop = data["crop"]
    district = data["district"]
    rainfall = data["rainfall"]
    temperature = data["temperature"]
    area = data["area"]
    market_price = data["market_price"]

    # Predict profit
    prediction = model.predict([[
        crop,
        district,
        rainfall,
        temperature,
        area,
        market_price
    ]])

    return jsonify({
        "profit": float(prediction[0])
    })


# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)