from sentiment_model import SentimentAnalyzer, verify_api_key, PATH_TO_MODEL
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

# Is better practice to initialize the model as None, even if
# it will be declared as global later inside a function
sentiment_model = None

def load_model():
    global sentiment_model
    sentiment_model = SentimentAnalyzer(PATH_TO_MODEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
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
    
    if sentiment_model is None:
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
        result = sentiment_model(request.text)
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
