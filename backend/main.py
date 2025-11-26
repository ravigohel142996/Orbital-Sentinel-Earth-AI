"""
==============================================================================
Orbital Sentinel - FastAPI Backend
Main API server for risk analysis and data streaming
==============================================================================
"""

import asyncio
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import (
    EnvironmentData,
    RiskPrediction,
    AnalysisRequest,
    AnalysisResponse,
    HealthStatus,
    DashboardStats,
    GeoLocation,
)
from services.gemini_service import get_gemini_service
from services.voice_service import get_voice_service
from services.storage_service import get_storage_service
from streaming.data_simulator import get_simulator
from streaming.kafka_service import get_streaming_service
from configs.config import get_config, validate_config


# Background task state
background_tasks_running = False
simulator_task = None

# CORS configuration from environment
# ALLOWED_ORIGINS can be set as a comma-separated list of URLs, or "*" for all origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS == "*":
    cors_origins = ["*"]
    # When using wildcard origins, credentials must be disabled for browser security
    cors_allow_credentials = False
else:
    cors_origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]
    # Allow credentials when specific origins are configured
    cors_allow_credentials = True

async def run_simulator():
    """Background task to run data simulation and analysis"""
    global background_tasks_running
    
    simulator = get_simulator()
    gemini = get_gemini_service()
    storage = get_storage_service()
    streaming = get_streaming_service()
    
    logger.info("Background simulator started")
    
    async for data in simulator.stream_data(interval_seconds=10):
        if not background_tasks_running:
            break
        
        try:
            # Publish to streaming service
            await streaming.publish(data)
            
            # Analyze risk
            prediction = await gemini.analyze_risk(data)
            
            # Save prediction
            await storage.save_prediction(prediction)
            
            logger.info(f"Processed data for {data.location.region}: {prediction.risk_level.value}")
            
        except Exception as e:
            logger.error(f"Simulator error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global background_tasks_running, simulator_task
    
    logger.info("Starting Orbital Sentinel API")
    
    # Start background simulator in simulation mode
    config = get_config()
    if config.simulation_mode:
        background_tasks_running = True
        simulator_task = asyncio.create_task(run_simulator())
        logger.info("Background simulator enabled")
    
    yield
    
    # Shutdown
    background_tasks_running = False
    if simulator_task:
        simulator_task.cancel()
        try:
            await simulator_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Orbital Sentinel API stopped")


# Create FastAPI application
app = FastAPI(
    title="Orbital Sentinel API",
    description="Real-time Earth risk prediction system powered by Gemini AI",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware with full support for all methods and headers
# Note: With allow_origins=["*"], credentials are automatically disabled for browser security.
# For production with credentials support, set ALLOWED_ORIGINS to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Health & Status Endpoints
# ==============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Orbital Sentinel API",
        "version": "1.0.0",
        "description": "Real-time Earth risk prediction system",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Check API and service health status"""
    config_status = validate_config()
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "gemini": get_gemini_service().is_available,
            "elevenlabs": get_voice_service().is_available,
            "streaming": get_streaming_service().is_available,
            "storage": True,
            "simulator": background_tasks_running,
        },
        version="1.0.0"
    )


@app.get("/config", tags=["Health"])
async def get_configuration():
    """Get current configuration status (without secrets)"""
    return validate_config()


# ==============================================================================
# Risk Analysis Endpoints
# ==============================================================================

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_risk(request: AnalysisRequest):
    """
    Analyze environmental data for risk prediction.
    
    - **data**: Environmental sensor data
    - **include_reasoning**: Include chain-of-thought reasoning
    - **generate_voice**: Generate voice output for the prediction
    """
    start_time = time.time()
    
    try:
        # Get services
        gemini = get_gemini_service()
        voice = get_voice_service()
        storage = get_storage_service()
        
        # Analyze risk
        prediction = await gemini.analyze_risk(request.data)
        
        # Save prediction
        await storage.save_prediction(prediction)
        
        # Generate voice if requested
        audio_url = None
        if request.generate_voice and prediction.voice_summary:
            audio_bytes, error = await voice.generate_speech(prediction.voice_summary)
            if audio_bytes:
                # In production, upload to storage and return URL
                # For now, we'll skip the audio URL
                pass
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnalysisResponse(
            success=True,
            prediction=prediction,
            audio_url=audio_url,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            processing_time_ms=(time.time() - start_time) * 1000
        )


@app.post("/analyze/batch", tags=["Analysis"])
async def analyze_batch(data_points: List[EnvironmentData]):
    """Analyze multiple data points in batch"""
    gemini = get_gemini_service()
    storage = get_storage_service()
    
    results = []
    for data in data_points:
        try:
            prediction = await gemini.analyze_risk(data)
            await storage.save_prediction(prediction)
            results.append({"success": True, "prediction": prediction})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    return {"results": results, "total": len(results)}


@app.get("/analyze/simulate", response_model=AnalysisResponse, tags=["Analysis"])
async def simulate_and_analyze():
    """Generate simulated data and analyze it"""
    simulator = get_simulator()
    gemini = get_gemini_service()
    storage = get_storage_service()
    
    start_time = time.time()
    
    try:
        # Generate simulated data
        data = simulator.generate_data_point()
        
        # Analyze
        prediction = await gemini.analyze_risk(data)
        
        # Save
        await storage.save_prediction(prediction)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnalysisResponse(
            success=True,
            prediction=prediction,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Simulation analysis failed: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            processing_time_ms=(time.time() - start_time) * 1000
        )


# ==============================================================================
# Predictions Endpoints
# ==============================================================================

@app.get("/predictions", tags=["Predictions"])
async def get_predictions(
    limit: int = Query(50, ge=1, le=200),
    risk_type: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get recent risk predictions with optional filtering"""
    storage = get_storage_service()
    predictions = await storage.get_predictions(limit, risk_type, risk_level)
    return {"predictions": predictions, "count": len(predictions)}


@app.get("/predictions/stats", response_model=DashboardStats, tags=["Predictions"])
async def get_stats():
    """Get dashboard statistics"""
    storage = get_storage_service()
    return await storage.get_stats()


@app.delete("/predictions/old", tags=["Predictions"])
async def clear_old_predictions(days: int = Query(7, ge=1, le=30)):
    """Clear predictions older than specified days"""
    storage = get_storage_service()
    removed = await storage.clear_old_predictions(days)
    return {"removed": removed, "days_cleared": days}


# ==============================================================================
# Voice Endpoints
# ==============================================================================

@app.post("/voice/generate", tags=["Voice"])
async def generate_voice(text: str, voice_id: Optional[str] = None):
    """Generate voice audio from text"""
    voice = get_voice_service()
    
    if not voice.is_available:
        raise HTTPException(status_code=503, detail="Voice service not available")
    
    audio_base64, error = await voice.generate_speech_base64(text, voice_id)
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    return {"audio_base64": audio_base64, "format": "mp3"}


@app.get("/voice/voices", tags=["Voice"])
async def list_voices():
    """List available voices"""
    voice = get_voice_service()
    return {"voices": voice.get_available_voices()}


# ==============================================================================
# Streaming Endpoints
# ==============================================================================

@app.post("/stream/publish", tags=["Streaming"])
async def publish_data(data: EnvironmentData):
    """Publish environmental data to the stream"""
    streaming = get_streaming_service()
    success = await streaming.publish(data)
    
    if success:
        return {"status": "published", "timestamp": datetime.utcnow()}
    else:
        raise HTTPException(status_code=500, detail="Failed to publish data")


@app.get("/stream/status", tags=["Streaming"])
async def stream_status():
    """Get streaming service status"""
    streaming = get_streaming_service()
    return {
        "kafka_available": streaming.producer.is_available,
        "fallback_active": not streaming.producer.is_available,
        "fallback_queue_size": len(streaming.producer._fallback_queue)
    }


# ==============================================================================
# Simulator Endpoints
# ==============================================================================

@app.post("/simulator/start", tags=["Simulator"])
async def start_simulator(background_tasks: BackgroundTasks):
    """Start the background data simulator"""
    global background_tasks_running, simulator_task
    
    if background_tasks_running:
        return {"status": "already_running"}
    
    background_tasks_running = True
    simulator_task = asyncio.create_task(run_simulator())
    
    return {"status": "started"}


@app.post("/simulator/stop", tags=["Simulator"])
async def stop_simulator():
    """Stop the background data simulator"""
    global background_tasks_running
    
    background_tasks_running = False
    
    return {"status": "stopped"}


@app.get("/simulator/status", tags=["Simulator"])
async def simulator_status():
    """Get simulator status"""
    return {"running": background_tasks_running}


@app.get("/simulator/generate", tags=["Simulator"])
async def generate_sample_data(count: int = Query(1, ge=1, le=20)):
    """Generate sample environmental data without analysis"""
    simulator = get_simulator()
    data = simulator.generate_batch(count)
    return {"data": [d.model_dump() for d in data]}


# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug,
        log_level="info"
    )
