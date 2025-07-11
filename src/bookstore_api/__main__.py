import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main_page():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000)
