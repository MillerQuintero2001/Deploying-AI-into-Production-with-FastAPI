from fastapi.security import APIKeyHeader
from fastapi import HTTPException, FastAPI, Depends, Security
from dotenv import load_dotenv
import os

load_dotenv()


items = {
    "A1": {"name": "Foo", "price": 50.2},
    "A2": {"name": "Bar", "price": 62},
    "A3": {"name": "Baz", "price": 70.4},
}
# Load environment variables
API_SECRET_KEY = os.getenv("API_KEY", "your_secret_key")

# NOTE: auto_error=False allows us to handle missing API key manually
# NOTE 2: Also 'APIKeyQuery' can be used to get the key from query parameters
header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    api_key: str = Security(header_scheme)
):
    if api_key is None:
        raise HTTPException(
            status_code=403,
            detail="API key missing"
        )
    if api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail="API key invalid"
        )
    return api_key


app = FastAPI()

@app.get("/items/{item_id}")
def read_items(
    item_id: str,
    api_key: str = Depends(verify_api_key)
):
    return {"item": items.get(item_id, "Item not found")}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


# curl -X GET "http://localhost:8005/items/A1" -H "X-API-Key: your_secret_key"
# curl -X GET "http://localhost:8005/health" -H "accept: application/json"
