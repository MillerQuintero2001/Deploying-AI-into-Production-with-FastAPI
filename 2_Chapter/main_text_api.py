from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze_comment")
def analyze_comment(text: str):
    problem_keywords = ["spam", "hate", "offensive", "abuse"]
    
    # Convert the input text to lowercase
    text_lower = text.lower()
    # Extract matching flags using list comprehension
    found_issues = [keyword for keyword in problem_keywords if keyword in text_lower]
    # Return the dictionary with required keys
    return {
        "issues": found_issues,
        "issue_count": len(found_issues),
        "original_text": text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# curl -X POST "http://localhost:8000/analyze_comment?text=Este%20comentario%20es%20spam%20y%20ofensivo"