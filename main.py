from src.main import app
def main():
    print("Hello from rag-fastapi!")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


