from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException, FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
API_SECRET_KEY = os.getenv("API_KEY", "default_secret_key")

header_scheme = APIKeyHeader(name="X-API-Key", auto_error=True)

app = FastAPI()

@app.get("/items/")
def read_items(
    api_key: str = Depends(header_scheme)
):
    if api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return {"api_key": api_key}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


# curl -X GET "http://localhost:8005/items/" -H "X-API-Key: default_secret_key"
