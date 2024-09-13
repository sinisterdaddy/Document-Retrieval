from fastapi import FastAPI
from app.api.routes import router

app = FastAPI()

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "API is running"}
