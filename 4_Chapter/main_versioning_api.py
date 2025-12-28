from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager
from penguin_model import PenguinClassifier, initialize_rate_limiter, test_api_key

class PenguinV1(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: int
    body_mass_g: int

# Add v2 model
class PenguinV2(BaseModel):
    data: str

class PredictionResponse(BaseModel):
    predicted_species: list[str]
    confidence: list[list[float]]

classifier = None

def load_model():
    try:
        classifier = PenguinClassifier()
        return classifier
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    classifier = load_model()
    if not classifier:
        raise RuntimeError("Failed to load the penguin classification model.")
    
    app.state.classifier = classifier
    initialize_rate_limiter(requests_per_minute=3)
    print("[STARTUP] Penguin Classifier API is ready.")
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    print("[EXIT] Closing ML API...")
    del app.state.classifier

app = FastAPI(title="Penguin Classifier API",
              description="An API to classify penguin species with versioned endpoints.",
              lifespan=lifespan)

@app.post("/v1/penguin_classifier")
def classify_penguin_v1(penguin: PenguinV1, api_key: str = Depends(test_api_key)):

    if app.state.classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    try:
        result = app.state.classifier(features=penguin.model_dump())
        return PredictionResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


# Add v2 endpoint
@app.post("/v2/penguin_classifier",
          description="Classify penguin species using space-separated feature values.")
# Use v2 model
def classify_penguin_v2(penguin: PenguinV2, api_key: str = Depends(test_api_key)):

    if app.state.classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    if not penguin.data.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty data provided"
        )
    
    if not len(penguin.data.split()) == 4:
        raise HTTPException(
            status_code=400,
            detail="Invalid data format. Expected 4 space-separated values."
        )

    try:
        penguin_v1 = PenguinV1(
            bill_length_mm=float(penguin.data.split()[0]),
            bill_depth_mm=float(penguin.data.split()[1]),
            flipper_length_mm=int(penguin.data.split()[2]),
            body_mass_g=int(penguin.data.split()[3])
        )
        result = app.state.classifier(features=penguin_v1.model_dump())
        return PredictionResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# curl -X POST "http://localhost:8080/v1/penguin_classifier" \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "bill_length_mm": 39.1,
#     "bill_depth_mm": 18.7,
#     "flipper_length_mm": 181,
#     "body_mass_g": 3750
#   }'

# curl -X POST "http://localhost:8080/v2/penguin_classifier" \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{"data": "39.1 18.7 181 3750"}'