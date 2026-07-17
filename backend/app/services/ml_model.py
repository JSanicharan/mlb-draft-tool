import joblib

model = joblib.load("rf_model.pkl")

def predict_ml_score(features: list) -> float:
    prediction = model.predict([features])
    return prediction[0]