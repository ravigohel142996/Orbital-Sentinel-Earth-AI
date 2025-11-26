"""
==============================================================================
Orbital Sentinel - Data Models
Pydantic models for risk analysis and streaming data
==============================================================================
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskType(str, Enum):
    """Types of environmental risks monitored by Orbital Sentinel"""
    FIRE = "fire"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    STORM = "storm"
    AIR_QUALITY = "air_quality"
    DROUGHT = "drought"
    VOLCANIC = "volcanic"
    TSUNAMI = "tsunami"


class RiskLevel(str, Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


class GeoLocation(BaseModel):
    """Geographic location data"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    region: Optional[str] = Field(None, description="Region or area name")
    country: Optional[str] = Field(None, description="Country name")


class EnvironmentData(BaseModel):
    """Environmental sensor data from streaming sources"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: GeoLocation
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed in km/h")
    wind_direction: Optional[float] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    precipitation: Optional[float] = Field(None, ge=0, description="Precipitation in mm")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    air_quality_index: Optional[float] = Field(None, ge=0, le=500, description="AQI value")
    seismic_activity: Optional[float] = Field(None, ge=0, description="Seismic magnitude")
    soil_moisture: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture percentage")
    vegetation_index: Optional[float] = Field(None, ge=-1, le=1, description="NDVI vegetation index")
    source: str = Field(default="sensor", description="Data source identifier")


class ReasoningStep(BaseModel):
    """Single step in the AI reasoning chain"""
    step_number: int
    observation: str
    analysis: str
    conclusion: str


class RiskPrediction(BaseModel):
    """Risk prediction result from Gemini analysis"""
    risk_id: str = Field(..., description="Unique identifier for this risk prediction")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    risk_type: RiskType
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    location: GeoLocation
    title: str = Field(..., description="Brief risk title")
    description: str = Field(..., description="Detailed risk description")
    reasoning_chain: List[ReasoningStep] = Field(default_factory=list)
    affected_population: Optional[int] = Field(None, description="Estimated affected population")
    recommended_actions: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence 0-1")
    raw_data: Optional[EnvironmentData] = None
    voice_summary: Optional[str] = Field(None, description="Voice-friendly summary")


class StreamMessage(BaseModel):
    """Message structure for Kafka streaming"""
    message_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    payload: Dict[str, Any]
    source: str


class AnalysisRequest(BaseModel):
    """Request for risk analysis"""
    data: EnvironmentData
    include_reasoning: bool = True
    generate_voice: bool = False


class AnalysisResponse(BaseModel):
    """Response from risk analysis"""
    success: bool
    prediction: Optional[RiskPrediction] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None
    processing_time_ms: float = 0


class HealthStatus(BaseModel):
    """System health status"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, bool]
    version: str = "1.0.0"


class DashboardStats(BaseModel):
    """Statistics for the dashboard"""
    total_predictions: int = 0
    active_risks: int = 0
    critical_risks: int = 0
    regions_monitored: int = 0
    last_update: datetime = Field(default_factory=datetime.utcnow)
    risk_breakdown: Dict[str, int] = Field(default_factory=dict)
