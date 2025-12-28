import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

class CommentMetrics(BaseModel):
    length: int
    user_reputation: int
    report_count: int

class CommentScorer:
    def predict(self, features: np.ndarray) -> float:
        """
        Predict trust score based on comment metrics
        features: [[length, user_reputation, report_count]]
        """
        # Unpack features
        length, reputation, reports = features[0]
        
        # Calculate trust score
        score = (0.3 * (length/500) +        # Normalize length
                 0.5 * (reputation/100) +    # Normalize reputation
                 -0.2 * reports)             # Reports reduce score
        
        return float(max(min(score * 100, 100), 0))  # Scale to 0-100


app = FastAPI()
model = CommentScorer()

@app.post("/predict_trust")
def predict_trust(comment: CommentMetrics):
    # Convert input and extract comment metrics
    features = np.array([[
        comment.length,
        comment.user_reputation,
        comment.report_count
    ]])
    # Get prediction from model 
    score = model.predict(features)
    return {
        "trust_score": round(score, 2),
        "comment_metrics": comment.model_dump()
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# curl -X POST "http://localhost:8080/predict_trust" \
#     -H "Content-Type: application/json" \
#     -d '{
#         "length": 150,
#         "user_reputation": 100,
#         "report_count": 0
#         }'
