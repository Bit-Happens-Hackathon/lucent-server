"""
Main module for FastAPI application.
This is the entry point to the Lucent API.
"""
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# load the routers for each table
from app.api.users.router import router as users_router
from app.api.schools.router import router as schools_router
from app.api.counselers.router import router as counselors_router
from app.api.resources.router import router as resources_router
from app.api.wellness.router import router as wellness_router
from app.api.surveys.router import router as surveys_router
from app.api.activity.router import router as activity_router

#Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(users_router)
api_router.include_router(schools_router)
api_router.include_router(wellness_router)
api_router.include_router(surveys_router)
api_router.include_router(activity_router) 

api_router.include_router(counselors_router)
api_router.include_router(resources_router)
api_router.include_router()

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Lucent API",
    description="Lucent Server API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)

# Configure CORS
origins = [
    "http://localhost:8000",  # FastAPI default port
]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint returning a welcome message.
    
    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to Lucent API. Server is running."}

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)