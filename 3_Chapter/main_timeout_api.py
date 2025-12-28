import asyncio
from fastapi import FastAPI, HTTPException, Depends
from sentiment_model import SentimentAnalyzer, initialize_rate_limiter, test_api_key
from contextlib import asynccontextmanager
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
    initialize_rate_limiter(requests_per_minute=3)
    print("[STARTUP] ML API with timeout is ready.")
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    print("[EXIT] Closing ML API...")


app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)

@app.post("/analyze_reviews")
async def analyze_reviews(review: CommentRequest,
                          api_key: str = Depends(test_api_key)):
    
    if app.state.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    if not review.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty text provided"
        )

    try:
        # Set model input and timeout limit
        async with asyncio.timeout(5):
            result = await app.state.model.async_call(review.text, sleep=6)
        return CommentResponse(
            text=review.text,
            sentiment=result["label"],
            confidence=result["confidence"],
            status="success"
        )    
    except asyncio.TimeoutError:
        # Raise HTTP status code for timeout error
        raise HTTPException(status_code=408, detail="Analysis timed out")
    except Exception as e:
        # Raise HTTP status code for internal error
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# curl -X POST \
#   http://localhost:8080/analyze_reviews \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "This is a test"}'
