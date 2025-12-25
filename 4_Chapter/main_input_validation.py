from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi import FastAPI
from datetime import date
from pydantic import BaseModel, model_validator
from typing import List


# NOTE: This 2 models are just for demonstration purposes, not implemented in FastAPI
class ModelInput(BaseModel):
    latitude: float
    longitude: float
    date: date

# Create batch input model
class BatchInput(BaseModel):
    job_name: str
    # Inputs are list of model inputs
    inputs: List[ModelInput]

    @model_validator(mode="before")
    def check_inputs_not_empty(cls, values):
        if 'inputs' in values and len(values['inputs']) == 0:
            raise RequestValidationError(
                ["The 'inputs' list must contain at least one item."]
            )
        return values


class InventoryRecord(BaseModel):
    name: str
    quantity: int

    # Create custom validator that runs after default validation
    @model_validator(mode="after")
    def validate_after(self):
        if self.quantity < 0:
            # Raise request validation error
            raise RequestValidationError(
                ["Negative quantity is not allowed!"]
            )
        return self
    

app = FastAPI(title="Advanced Input Validation API",
              description="An API demonstrating advanced input validation with Pydantic.")

# Create global exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Return plain text response
    return PlainTextResponse(str(exc), status_code=400)


@app.post("/v1/register_inventory")
def register_inventory(record: InventoryRecord):
    return {"message": f"Registered {record.quantity} of {record.name}"}


@app.post("/v1/register_model_input")
def register_model_input(input: ModelInput):
    return {
        "message": f"Received input at ({input.latitude}, {input.longitude}) on {input.date}"
    }

@app.post("/v1/register_batch")
def register_batch(batch: BatchInput):
    return {
        "message": f"Received batch job '{batch.job_name}' with {len(batch.inputs)} inputs",
        "inputs": [i.model_dump() for i in batch.inputs]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# curl -X POST "http://localhost:8080/v1/register_inventory" \
#      -H "Content-Type: application/json" \
#      -d '{"name": "apple", "quantity": -5}'


# curl -X POST "http://localhost:8080/v1/register_model_input" \
#      -H "Content-Type: application/json" \
#      -d '{"latitude": 19.43, "longitude": -99.13, "date": "2025-12-25"}'

# curl -X POST "http://localhost:8080/v1/register_batch" \
#      -H "Content-Type: application/json" \
#      -d '{"job_name": "test_job", "inputs": [{"latitude": 19.43, "longitude": -99.13, "date": "2025-12-25"}, {"latitude": 40.71, "longitude": -74.01, "date": "2025-12-24"}]}'

# curl -X POST "http://localhost:8080/v1/register_batch" \
#      -H "Content-Type: application/json" \
#      -d '{"job_name": "empty_job", "inputs": []}'