import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import defaultdict

load_dotenv()

# Ensure the models directory exists
Path(__file__).parent.joinpath("models").mkdir(parents=True, exist_ok=True)
PATH_TO_MODEL = Path(__file__).parent / "models" / "sentiment_model.joblib"

# Model creation
def train_and_save_model():
    data = {
        "review": [
            "I love this product, it's fantastic!",
            "Really satisfied with the quality!",
            "Terrible, I hate it.",
            "Not happy with the purchase.",
            "Absolutely amazing and wonderful!",
            "Worst experience ever.",
            "I am very pleased with my purchase.",
            "Disappointed, it didn't work as expected.",
            "The best thing I've ever bought.",
            "Totally awful, will not buy again."
        ],
        "label": [1, 1, 0, 0, 1, 0, 1, 0, 1, 0]  # 1 = Positive, 0 = Negative
    }

    df = pd.DataFrame(data)

    positive_words = ["love", "satisfied", "amazing", "fantastic", "wonderful", "pleased", "best"]
    negative_words = ["hate", "terrible", "worst", "disappointed", "awful"]

    df["num_words"] = df["review"].apply(lambda x: len(x.split()))
    df["num_positive_words"] = df["review"].apply(lambda x: sum(word in x.lower() for word in positive_words))
    df["num_complaints"] = df["review"].apply(lambda x: sum(word in x.lower() for word in negative_words))

    X = df[["num_words", "num_positive_words", "num_complaints"]]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = LogisticRegression(solver='lbfgs')
    model.fit(X_train.values, y_train.values)

    # Save model using joblib instead of pickle
    joblib.dump(model, PATH_TO_MODEL, compress=3)

# Define a callable class
class SentimentAnalyzer:
    def __init__(self, model_path):
        # Load the model using joblib

        # If model file does not exist, train and save it
        if not Path(model_path).is_file():
            print("[INFO] Training and saving new model...")
            train_and_save_model()
        self.model = joblib.load(model_path)
        self.positive_words = ["love", "satisfied", "amazing", "fantastic", "wonderful", "pleased", "best"]
        self.negative_words = ["hate", "terrible", "worst", "disappointed", "awful"]

    # It allows the instance to be called like a function, like use the prediction method, but with data processing included
    def __call__(self, text):
        num_words = len(text.split())
        num_positive_words = sum(word in text.lower() for word in self.positive_words)
        num_complaints = sum(word in text.lower() for word in self.negative_words)
        features = [[num_words, num_positive_words, num_complaints]]
        
        # Get prediction and confidence score
        prediction = self.model.predict(features)
        confidence_scores = self.model.predict_proba(features)
        
        # Return dictionary directly instead of JSON string
        result = {
            "label": "Positive" if prediction[0] == 1 else "Negative",
            "confidence": float(confidence_scores[0][prediction[0]])  
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