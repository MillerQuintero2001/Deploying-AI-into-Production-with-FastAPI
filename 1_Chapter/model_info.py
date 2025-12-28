from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

model_db = {}

class ModelInfo(BaseModel):
    model_id: int
    model_name: str
    description: str

class RegisterModelResponse(BaseModel):
    message: str
    model: ModelInfo

def get_model_details(model_id: int):
    # Simulate fetching model details from a database
    model = model_db.get(model_id)
    if model:
        return model['model_name']
    else:
        return "Unknown Model"

# Add model_id as a path parameter in the route
@app.get("/model-info/{model_id}")
# Pass on the model id as an argument
async def get_model_info(model_id: int):
    if model_id == 0:
      	# Raise the right status code for not found
        raise HTTPException(status_code=404, detail="Model not found")
    model_info = get_model_details(model_id)  

    return {"model_id": model_id, "model_name": model_info}


# Create the POST request endpoint
# NOTE: 'status_code' parameter set default response code to 201, that means 'resource created successfully'
@app.post("/register-model", status_code=201, response_model=RegisterModelResponse)
# Pass the model info from the request as function parameter 
def register_model(model_info: ModelInfo):
    # Add new model's information dictionary to the model database
    model_db[model_info.model_id] = model_info.model_dump()
    
    return RegisterModelResponse(
        message="Model registered successfully",
        model=model_info
    )


# curl -X POST "http://localhost:8000/register-model" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "model_id": 1,
#     "model_name": "GPT-4",
#     "description": "Large language model"
#   }'


# curl -X GET "http://localhost:8000/model-info/1"
