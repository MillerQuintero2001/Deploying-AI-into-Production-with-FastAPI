from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)  
    email: str
    age: int

    # Add the Pydantic decorator to validate
    @field_validator('email')  
    def email_must_be_example_domain(cls, user_email):
        # Use the endswith method to validate the email ends with @mode360.com
        if not user_email.endswith("@mode360.com"):
            raise ValueError('Email must be from the mode360.com domain')
        return user_email
    
try:
    user = User(username="john_doe", email="john@mode360.com", age=25)
except Exception as e:
    print(str(e))

try:
    user = User(username="john", email="john@mode360.com", age=25)
except Exception as e:
    print(str(e))

try:
    user = User(username="john"*20, email="john@hacker.com", age=25)
except Exception as e:
    print(str(e))

app = FastAPI()

# Create a post request endpoint
@app.post("/register")
# Validate incoming user data with a pydantic model
def register_user(user: User):
    return {"status": "success", "user": user.model_dump()}
  
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


# curl -X POST "http://localhost:8080/register" \
# -H "Content-Type: application/json" \
# -d '{"username": "jane_doe", "email": "jane@mode360.com", "age": 30}'
