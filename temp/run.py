import uvicorn
from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)