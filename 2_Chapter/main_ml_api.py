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


@app.post("/analyze")
def analyze_comment(request: CommentRequest):
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
        "status": "healthy" if sentiment_model is not None else "unhealthy",
        "model_loaded": sentiment_model is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# curl -X GET "http://localhost:8080/health" -H "accept: application/json"


# curl -X POST "http://localhost:8080/analyze" \
#      -H "Content-Type: application/json" \
#      -d '{"text": "This is great, I can totally relate."}'
