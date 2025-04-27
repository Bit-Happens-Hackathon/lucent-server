# Entry point to the app
from datetime import datetime
from fastapi import FastAPI
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

app = FastAPI(
    title="Lucent API",
    description="Lucent Server API",
    version="0.1.0"
)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set as environment variables.")

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), key)

@app.get("/")
async def root():
    return {"message": "Welcome to Lucent API. Server is running."}
