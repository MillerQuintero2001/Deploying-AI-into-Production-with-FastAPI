from pydantic import BaseModel
from fastapi import FastAPI
import joblib
from pathlib import Path

class CoffeeQualityInput(BaseModel):
    # Use apt data type for each attribute of coffee quality
    aroma: float  
    flavor: float  
    altitude: int 


class QualityPrediction(BaseModel):
    quality_score: float 
    confidence: float

def predict_quality(coffee_data: CoffeeQualityInput) -> QualityPrediction:


    # Prepare features for prediction
    features = [[
        coffee_data.aroma,
        coffee_data.flavor,
        coffee_data.altitude
    ]]

    # Make prediction
    quality_score = model.predict(features)[0]
    confidence = float(max(model.predict_proba(features)[0]))

    return QualityPrediction(quality_score=quality_score, confidence=confidence)


app = FastAPI()

# Load the pre-trained model
SCRIPT_DIR = Path(__file__).parent
MODEL_PATH = SCRIPT_DIR / 'models/coffee_quality_model.pkl'
model = joblib.load(MODEL_PATH)

# Specify the data model to validate response
@app.post("/predict", response_model=QualityPrediction) 
# Specify the data model to validate input request
def predict(coffee_data: CoffeeQualityInput):
    prediction = predict_quality(coffee_data)
    return prediction
