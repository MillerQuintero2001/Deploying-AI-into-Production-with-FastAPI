import asyncio
import joblib
from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

load_dotenv()

# Ensure the models directory exists
Path(__file__).parent.joinpath("models").mkdir(parents=True, exist_ok=True)
PATH_TO_MODEL = Path(__file__).parent / "models" / "penguin_classifier.pkl"

# Define a callable class
class PenguinClassifier:
    def __init__(self, model_path=PATH_TO_MODEL):
        self.model = joblib.load(model_path)

    # It allows the instance to be called like a function, like use the prediction method, but with data processing included
    def __call__(self, features):

        df = pd.DataFrame([features])

        # Get prediction and confidence score
        predictions = self.model.predict(df)
        confidence = self.model.predict_proba(df)
        
        # Return dictionary directly instead of JSON string
        result = {
            "predicted_species": predictions.tolist(),
            "confidence": confidence.tolist()
        }
        return result
    


class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # Store request timestamps per API key

    def is_rate_limited(self, api_key: str) -> tuple[bool, int]:
        """
        Check if the request should be rate limited
        Returns (is_limited, requests_remaining)
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Remove requests older than 1 minute
        self.requests[api_key] = [
            req_time for req_time in self.requests[api_key]
            if req_time > minute_ago
        ]
        
        # Check if rate limit is exceeded
        recent_requests = len(self.requests[api_key])
        if recent_requests >= self.requests_per_minute:
            return True, 0
            
        # Add new request timestamp
        self.requests[api_key].append(now)
        return False, self.requests_per_minute - recent_requests - 1


api_key_header = APIKeyHeader(name="X-API-Key")
API_KEY = os.getenv("API_KEY", "default_secret_key")

# Pass the variable containing the APIKeyHeader
def verify_api_key(api_key: str = Depends(api_key_header)):  
    # Verify the API key
    if api_key != API_KEY:  
      	# Raise the HTTP exception here
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


rate_limiter = None

def initialize_rate_limiter(requests_per_minute: int = 10):
    global rate_limiter
    rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)

# Check api key and rate limit
def test_api_key(api_key: str = Depends(api_key_header)):
    
    # Verify the API key
    if api_key != API_KEY:  
        raise HTTPException(status_code=403, detail="Invalid API Key")

    is_limited, requests_remaining = rate_limiter.is_rate_limited(api_key)
    if is_limited:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    return api_key