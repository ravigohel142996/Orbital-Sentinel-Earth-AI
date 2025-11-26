"""
==============================================================================
Orbital Sentinel - Configuration Module
Centralized configuration management for all services
==============================================================================
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GeminiConfig(BaseModel):
    """Configuration for Google Gemini AI service"""
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 2048


class ElevenLabsConfig(BaseModel):
    """Configuration for ElevenLabs voice service"""
    api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    model_id: str = "eleven_monolingual_v1"


class KafkaConfig(BaseModel):
    """Configuration for Confluent Kafka streaming"""
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    api_key: str = os.getenv("KAFKA_API_KEY", "")
    api_secret: str = os.getenv("KAFKA_API_SECRET", "")
    topic: str = os.getenv("KAFKA_TOPIC", "orbital-sentinel-risks")
    group_id: str = "orbital-sentinel-consumer-group"


class ServerConfig(BaseModel):
    """Configuration for backend server"""
    host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    port: int = int(os.getenv("BACKEND_PORT", "8000"))
    debug: bool = os.getenv("LOG_LEVEL", "INFO") == "DEBUG"


class AppConfig(BaseModel):
    """Main application configuration"""
    gemini: GeminiConfig = GeminiConfig()
    elevenlabs: ElevenLabsConfig = ElevenLabsConfig()
    kafka: KafkaConfig = KafkaConfig()
    server: ServerConfig = ServerConfig()
    simulation_mode: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: Path = Path(__file__).parent.parent / "data"


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config


def validate_config() -> dict:
    """Validate configuration and return status"""
    status = {
        "gemini_configured": bool(config.gemini.api_key),
        "elevenlabs_configured": bool(config.elevenlabs.api_key),
        "kafka_configured": bool(config.kafka.api_key and config.kafka.api_secret),
        "simulation_mode": config.simulation_mode,
    }
    return status
