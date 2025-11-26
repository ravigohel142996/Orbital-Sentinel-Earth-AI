"""
==============================================================================
Orbital Sentinel - ElevenLabs Voice Service
Text-to-speech conversion for risk alerts and summaries
==============================================================================
"""

import base64
import io
from typing import Optional, Tuple
from loguru import logger

try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("elevenlabs not installed, voice output disabled")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import get_config


class VoiceService:
    """
    ElevenLabs voice service for generating speech from risk summaries.
    Provides conversational AI voice output for alerts and notifications.
    """
    
    def __init__(self):
        """Initialize ElevenLabs voice service"""
        self.config = get_config().elevenlabs
        self.client = None
        self._initialized = False
        
        if ELEVENLABS_AVAILABLE and self.config.api_key:
            try:
                self.client = ElevenLabs(api_key=self.config.api_key)
                self._initialized = True
                logger.info("ElevenLabs voice service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs: {e}")
                self._initialized = False
        else:
            logger.warning("ElevenLabs API key not configured, voice output disabled")
    
    @property
    def is_available(self) -> bool:
        """Check if voice service is available"""
        return self._initialized
    
    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID override
            
        Returns:
            Tuple of (audio_bytes, error_message)
        """
        if not self._initialized:
            logger.warning("Voice service not available, returning None")
            return None, "Voice service not configured"
        
        try:
            # Use provided voice_id or default
            target_voice = voice_id or self.config.voice_id
            
            # Generate audio using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=target_voice,
                model_id=self.config.model_id,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                )
            )
            
            # Collect audio bytes from generator
            audio_bytes = b"".join(audio_generator)
            
            logger.info(f"Generated speech audio: {len(audio_bytes)} bytes")
            return audio_bytes, None
            
        except Exception as e:
            error_msg = f"Speech generation failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    async def generate_speech_base64(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate speech audio and return as base64 encoded string.
        Useful for web frontend integration.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID override
            
        Returns:
            Tuple of (base64_audio, error_message)
        """
        audio_bytes, error = await self.generate_speech(text, voice_id)
        
        if audio_bytes:
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            return base64_audio, None
        
        return None, error
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice objects with id, name, and description
        """
        if not self._initialized:
            return []
        
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "description": getattr(voice, 'description', ''),
                }
                for voice in voices.voices
            ]
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []
    
    def format_alert_text(
        self,
        risk_type: str,
        risk_level: str,
        risk_score: float,
        location: str,
        recommendations: list
    ) -> str:
        """
        Format risk information into natural speech text.
        
        Args:
            risk_type: Type of risk
            risk_level: Severity level
            risk_score: Risk score (0-100)
            location: Location description
            recommendations: List of recommended actions
            
        Returns:
            Formatted text suitable for speech synthesis
        """
        # Urgency prefix based on risk level
        urgency_prefix = {
            "critical": "Attention! Critical alert!",
            "high": "Important alert.",
            "moderate": "Advisory notice.",
            "low": "Information update.",
            "minimal": "Status report.",
        }
        
        prefix = urgency_prefix.get(risk_level.lower(), "Alert.")
        
        # Build the speech text
        text_parts = [
            prefix,
            f"Orbital Sentinel has detected a {risk_level} {risk_type.replace('_', ' ')} risk",
            f"at {location}.",
            f"The risk score is {risk_score:.0f} out of 100.",
        ]
        
        # Add top recommendation if available
        if recommendations:
            text_parts.append(f"Recommended action: {recommendations[0]}")
        
        text_parts.append("Stay safe and monitor for updates.")
        
        return " ".join(text_parts)


# Singleton instance
_voice_service = None


def get_voice_service() -> VoiceService:
    """Get or create the singleton voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
