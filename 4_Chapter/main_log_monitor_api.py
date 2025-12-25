import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, model_validator
from contextlib import asynccontextmanager
from penguin_model import PenguinClassifier, initialize_rate_limiter, test_api_key


class PenguinV1(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: int
    body_mass_g: int

    # Validate that each value is positive
    @model_validator(mode="after")
    def check_positive_values(self):
        if (self.bill_length_mm <= 0 or self.bill_depth_mm <= 0 or
            self.flipper_length_mm <= 0 or self.body_mass_g <= 0):
            raise RequestValidationError(
                ["All measurements must be positive values."]
            )
        return self

# Add v2 model
class PenguinV2(BaseModel):
    data: str

    @model_validator(mode="after")
    def check_non_empty(self):
        if not self.data.strip():
            raise HTTPException(status_code=400, detail="Data must not be empty.")
        return self
    
    @model_validator(mode="after")
    def check_data_format(self):
        if not len(self.data.split()) == 4:
            raise HTTPException(status_code=400, detail="Data must contain exactly 4 space-separated values.")
        return self
    
    @model_validator(mode="after")
    def check_positive_values(self):
        values = self.data.split()
        for value in values:
            if float(value) <= 0:
                raise HTTPException(status_code=400, detail="All measurements must be positive values.")
        return self

class PredictionResponse(BaseModel):
    predicted_species: list[str]
    confidence: list[list[float]]

classifier = None

def load_model():
    global classifier
    classifier = PenguinClassifier()

# Set up logger
logger = logging.getLogger('uvicorn.error')

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    logger.info("Model loaded successfully.")
    initialize_rate_limiter(requests_per_minute=10)
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    logger.info("Closing ML API...")

app = FastAPI(title="Penguin Classifier API",
              description="An API to classify penguin species with versioned endpoints.",
              lifespan=lifespan)
logger.info("FastAPI app created.")


# Create global exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Return plain text response
    return PlainTextResponse(str(exc), status_code=400)

# Middleware to log request processing time
@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"Request: {request.method} {request.url} completed in {process_time} seconds.")
    return response


@app.post("/v1/penguin_classifier")
def classify_penguin_v1(penguin: PenguinV1, api_key: str = Depends(test_api_key)):

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    try:
        result = classifier(features=penguin.model_dump())
        return PredictionResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


# Add v2 endpoint
@app.post("/v2/penguin_classifier")
# Use v2 model
def classify_penguin_v2(penguin: PenguinV2, api_key: str = Depends(test_api_key)):

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    try:
        penguin_v1 = PenguinV1(
            bill_length_mm=float(penguin.data.split()[0]),
            bill_depth_mm=float(penguin.data.split()[1]),
            flipper_length_mm=int(penguin.data.split()[2]),
            body_mass_g=int(penguin.data.split()[3])
        )
        result = classifier(features=penguin_v1.model_dump())
        return PredictionResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )

# Create health check endpoint
@app.get("/health", response_class=PlainTextResponse, status_code=status.HTTP_200_OK)
async def get_health():
    # Capture the model params
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    params = classifier.model.get_params()
    safe_params = {k: str(v) for k, v in params.items() if isinstance(v, (str, int, float, bool, list, dict, tuple))}

    lines = [f"{k}: {v}" for k, v in safe_params.items()]
    return f"Health Check - Model Parameters:\n{'\n'.join(lines)}"


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

# curl -X GET "http://localhost:8080/health"