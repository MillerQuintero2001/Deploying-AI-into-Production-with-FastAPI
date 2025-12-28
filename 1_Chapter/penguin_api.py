from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).parent

MODEL_PATH = SCRIPT_DIR / 'models/penguin_classifier.pkl'

model = joblib.load(MODEL_PATH)

app = FastAPI()

# Define el modelo de datos para la petición
class PenguinFeatures(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: int
    body_mass_g: int

@app.post("/predict")
def predict(penguin: PenguinFeatures):
    df = pd.DataFrame([penguin.model_dump()])
    
    predictions = model.predict(df)
    confidence = model.predict_proba(df)

    return {"predicted_species": predictions.tolist(),
            "confidence": confidence.tolist(),
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Ejemplo de uso con curl:
# Envía una solicitud POST al endpoint /predict con las características del pingüino
# curl -X POST "http://localhost:8080/predict" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "bill_length_mm": 39.1,
#     "bill_depth_mm": 18.7,
#     "flipper_length_mm": 181,
#     "body_mass_g": 3750
#   }'
