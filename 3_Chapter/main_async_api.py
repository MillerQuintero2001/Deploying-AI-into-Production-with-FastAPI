from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager
from sentiment_model import SentimentAnalyzer, initialize_rate_limiter, test_api_key
from typing import List
from pydantic import BaseModel


# Define request/response models
class CommentRequest(BaseModel):
    text: str

class Reviews(BaseModel):
    texts: List[str]

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
    print("[STARTUP] ML API with rate limiting is ready.")
    # This indicate to FastAPI that the startup tasks are done
    yield
    # The code after yield is executed during shutdown
    print("[EXIT] Closing ML API...")

app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)

# Create async endpoint at /analyze route
@app.post("/analyze")
# Write an asynchronous function to process review's text
async def analyze_review(review: CommentRequest,
    # Authenticate the incoming API key using verify_api_key function
    api_key: str = Depends(test_api_key)
):
    
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
        # Run the model in a separate thread to avoid any event loop blockage
        # NOTE: If the __call__ method in SentimentAnalyzer is not async, use asyncio.to_thread
        # but if the __call__ method is async, use await directly
        result = await asyncio.to_thread(app.state.model, review.text)
        return CommentResponse(
            text=review.text,
            sentiment=result["label"],
            confidence=result["confidence"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during model inference: {str(e)}"
        )


# Create a background task dependency
@app.post("/analyze_batch")
async def analyze_batch(
    reviews: Reviews,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(test_api_key)
):
    
    if app.state.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    async def process_reviews(texts: List[str]):
        for text in texts:

            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Empty text provided"
                )
            
            try:
                result = await asyncio.to_thread(app.state.model, text)
                print(f"Processed: {result['label']}")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during model inference: {str(e)}"
                )
    # Add the task of analysing reviews' texts to the background
    background_tasks.add_task(process_reviews, reviews.texts)
    return {"message": "Processing started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# curl -X POST \
#   http://localhost:8080/analyze \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "This is not a good product"}'

# curl -X POST \
#   http://localhost:8080/analyze_batch \
#   -H "X-API-Key: your_secret_key" \
#   -H "Content-Type: application/json" \
#   -d '{"texts": ["I love this product", "I did not like it", "It is acceptable"]}'
