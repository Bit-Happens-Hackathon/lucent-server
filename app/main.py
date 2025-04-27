# Entry point to the app
from fastapi import FastAPI

app = FastAPI(
    title="Lucent API",
    description="Lucent Server API",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Lucent API. Server is running."}