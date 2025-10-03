from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import tracking

app = FastAPI(
    title="Tracking & Attribution API",
    description="Advanced ad tracking platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracking.router)

@app.get("/")
async def root():
    return {
        "message": "Tracking & Attribution API", 
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
