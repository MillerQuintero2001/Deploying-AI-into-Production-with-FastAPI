from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

SCRIPT_DIR = Path(__file__).parent

MODEL_PATH = SCRIPT_DIR / 'models/penguin_classifier.pkl'

model = joblib.load(MODEL_PATH)

app = FastAPI()

# Define el modelo de datos para la petición
class PenguinFeatures(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: int
    body_mass_g: int

@app.post("/predict")
def predict(penguin: PenguinFeatures):
    
    features = [[penguin.culmen_length_mm, penguin.culmen_depth_mm,
                penguin.flipper_length_mm, penguin.body_mass_g]]
    
    prediction = model.predict(features)[0]
    print(f"Predicted species: {prediction}")

    return {"predicted_species": prediction,
            "confidence": float(max(model.predict_proba(features)[0]))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Ejemplo de uso con curl:
# Envía una solicitud POST al endpoint /predict con las características del pingüino
# curl -X POST "http://localhost:8080/predict" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "culmen_length_mm": 39.1,
#     "culmen_depth_mm": 18.7,
#     "flipper_length_mm": 181,
#     "body_mass_g": 3750
#   }'