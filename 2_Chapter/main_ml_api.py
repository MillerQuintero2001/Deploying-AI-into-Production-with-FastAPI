from sentiment_model import SentimentAnalyzer, PATH_TO_MODEL
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel

# Define request/response models
class CommentRequest(BaseModel):
    text: str

class CommentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float


def load_model():
    if not PATH_TO_MODEL.exists():
        raise FileNotFoundError(f"Model path {PATH_TO_MODEL} does not exist.")

    try:
        sentiment_model = SentimentAnalyzer(PATH_TO_MODEL)
        return sentiment_model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None     

@asynccontextmanager
async def lifespan(app: FastAPI):
    sentiment_model = load_model()

    if not sentiment_model:
        raise RuntimeError("Failed to load the sentiment analysis model.")
    
    app.state.model = sentiment_model
    print("[STARTUP] ML API is ready.")
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    print("[EXIT] Closing ML API...")
    del app.state.model

app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)


@app.post("/analyze")
def analyze_comment(request: CommentRequest):
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
        confidence=result["confidence"]
    )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during model inference: {str(e)}"
        )


# Define a GET endpoint at route "/health"
@app.get("/health")
def health_check():
  	# Check whether sentiment_model is loaded or not.
    return {
        "status": "healthy" if app.state.model is not None else "unhealthy",
        "model_loaded": app.state.model is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# curl -X GET "http://localhost:8080/health" -H "accept: application/json"


# curl -X POST "http://localhost:8080/analyze" \
#      -H "Content-Type: application/json" \
#      -d '{"text": "This is great, I can totally relate."}'
