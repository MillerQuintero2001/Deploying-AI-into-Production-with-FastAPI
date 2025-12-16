from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path

class DiabetesFeatures(BaseModel):
    age: int
    bmi: float
    blood_pressure: float

# Create FastAPI instance
app = FastAPI()

SCRIPT_DIR = Path(__file__).parent

MODEL_PATH = SCRIPT_DIR / 'models/diabetes_model.pkl'

model = joblib.load(MODEL_PATH)

# Create a POST request endpoint at the route "/predict"
@app.post("/predict")
async def predict_progression(features: DiabetesFeatures):
    input_data = [[
        features.age,
        features.bmi,
        features.blood_pressure
    ]]
    
    # Use the predict method to make a prediction
    prediction = model.predict(input_data)
    return {"predicted_progression": float(prediction[0])}
