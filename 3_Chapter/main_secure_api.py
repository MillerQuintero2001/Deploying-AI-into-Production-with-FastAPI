from sentiment_model import SentimentAnalyzer, verify_api_key
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel


# Define request/response models
class CommentRequest(BaseModel):
    text: str

class CommentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    status: str


def load_model():
    try:
        sentiment_model = SentimentAnalyzer()
        return sentiment_model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    model = load_model()
    if not model:
        raise RuntimeError("Failed to load the sentiment analysis model.")
    
    app.state.model = model
    print("[STARTUP] ML API is ready.")
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    print("[EXIT] Closing ML API...")


app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)

# This adds protection to the endpoint, requiring a valid API key,
# to protect the entire app:
# app = FastAPI(dependencies=[Depends(verify_api_key)])
@app.post("/predict")
def get_prediction(
    request: CommentRequest,
    # Authenticate the incoming API key using verify_api_key function
    api_key: str = Depends(verify_api_key)
):
    
    if app.state.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty text provided"
        )
    
    try:
        result = app.state.model(request.text)
        return CommentResponse(
            text=request.text,
            sentiment=result["label"],
            confidence=result["confidence"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during model inference: {str(e)}"
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# Good curl example:
# curl -X POST \
#   http://localhost:8080/predict \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "This is not a good product"}'

# Bad curl example (invalid API key):
# curl -X POST \
#   http://localhost:8080/predict \
#   -H "X-API-Key: invalid_key" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "This is not a good product"}'
