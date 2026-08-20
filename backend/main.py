"""
BLACKOUT Backend - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from routers import simulate, recover, graph, resilience

app = FastAPI(
    title="BLACKOUT API",
    description="Chaos testing for enterprise knowledge graphs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router)
app.include_router(recover.router)
app.include_router(graph.router)
app.include_router(resilience.router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/cross-training/{person_id}")
async def get_cross_training(person_id: str):
    from services.cross_training import find_cross_training_recommendations
    from db import get_driver

    driver = get_driver()
    try:
        recommendations = await find_cross_training_recommendations(person_id, driver)
        return {"recommendations": recommendations}
    finally:
        driver.close()
