"""
==============================================================================
Orbital Sentinel - Gemini AI Service
Risk analysis and reasoning chain generation using Google Gemini 2.0
==============================================================================
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List
from loguru import logger

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed, using simulation mode")

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from backend.models import (
    EnvironmentData,
    RiskPrediction,
    RiskType,
    RiskLevel,
    ReasoningStep,
    GeoLocation,
)
from configs.config import get_config


class GeminiService:
    """
    Gemini AI service for environmental risk analysis.
    Uses chain-of-thought reasoning to analyze sensor data and predict risks.
    """
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        self.config = get_config().gemini
        self.model = None
        self._initialized = False
        
        if GENAI_AVAILABLE and self.config.api_key:
            try:
                genai.configure(api_key=self.config.api_key)
                self.model = genai.GenerativeModel(self.config.model_name)
                self._initialized = True
                logger.info(f"Gemini service initialized with model: {self.config.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self._initialized = False
        else:
            logger.warning("Gemini API key not configured, using simulation mode")
    
    @property
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self._initialized
    
    def _build_analysis_prompt(self, data: EnvironmentData) -> str:
        """
        Build a comprehensive prompt for Gemini to analyze environmental data.
        Includes chain-of-thought reasoning instructions.
        """
        prompt = f"""You are Orbital Sentinel, an advanced AI system for Earth risk prediction.
Analyze the following environmental sensor data and predict potential risks.

## SENSOR DATA
- Location: {data.location.latitude}°, {data.location.longitude}° ({data.location.region or 'Unknown'}, {data.location.country or 'Unknown'})
- Timestamp: {data.timestamp.isoformat()}
- Temperature: {data.temperature}°C
- Humidity: {data.humidity}%
- Wind Speed: {data.wind_speed} km/h
- Wind Direction: {data.wind_direction}°
- Precipitation: {data.precipitation} mm
- Pressure: {data.pressure} hPa
- Air Quality Index: {data.air_quality_index}
- Seismic Activity: {data.seismic_activity} magnitude
- Soil Moisture: {data.soil_moisture}%
- Vegetation Index (NDVI): {data.vegetation_index}

## ANALYSIS INSTRUCTIONS
Perform a step-by-step reasoning analysis:

1. **OBSERVATION**: What do the sensor readings indicate?
2. **PATTERN RECOGNITION**: Identify any anomalies or concerning patterns
3. **RISK ASSESSMENT**: Determine the primary risk type and severity
4. **IMPACT ANALYSIS**: Estimate potential impact on population and infrastructure
5. **RECOMMENDATIONS**: Provide actionable safety recommendations

## OUTPUT FORMAT (JSON)
Return your analysis as valid JSON:
{{
    "risk_type": "fire|flood|earthquake|storm|air_quality|drought|volcanic|tsunami",
    "risk_level": "critical|high|moderate|low|minimal",
    "risk_score": 0-100,
    "title": "Brief descriptive title",
    "description": "Detailed risk description",
    "reasoning_chain": [
        {{
            "step_number": 1,
            "observation": "What you observed",
            "analysis": "Your analysis",
            "conclusion": "Your conclusion"
        }}
    ],
    "affected_population": estimated_number,
    "recommended_actions": ["action1", "action2"],
    "confidence": 0.0-1.0,
    "voice_summary": "A brief 2-3 sentence summary suitable for voice output"
}}

Analyze now and return ONLY the JSON response:"""
        
        return prompt
    
    async def analyze_risk(self, data: EnvironmentData) -> RiskPrediction:
        """
        Analyze environmental data and generate risk prediction.
        
        Args:
            data: Environmental sensor data
            
        Returns:
            RiskPrediction with reasoning chain
        """
        if not self._initialized:
            logger.info("Using simulated risk analysis (Gemini not configured)")
            return self._simulate_risk_analysis(data)
        
        try:
            # Generate analysis using Gemini
            prompt = self._build_analysis_prompt(data)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
            )
            
            # Parse the response
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(response_text)
            
            # Build reasoning chain
            reasoning_chain = [
                ReasoningStep(**step) for step in analysis.get("reasoning_chain", [])
            ]
            
            # Create prediction
            prediction = RiskPrediction(
                risk_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                risk_type=RiskType(analysis["risk_type"]),
                risk_level=RiskLevel(analysis["risk_level"]),
                risk_score=float(analysis["risk_score"]),
                location=data.location,
                title=analysis["title"],
                description=analysis["description"],
                reasoning_chain=reasoning_chain,
                affected_population=analysis.get("affected_population"),
                recommended_actions=analysis.get("recommended_actions", []),
                confidence=float(analysis.get("confidence", 0.8)),
                raw_data=data,
                voice_summary=analysis.get("voice_summary"),
            )
            
            logger.info(f"Risk analysis complete: {prediction.risk_type} - {prediction.risk_level}")
            return prediction
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}, using simulation")
            return self._simulate_risk_analysis(data)
    
    def _simulate_risk_analysis(self, data: EnvironmentData) -> RiskPrediction:
        """
        Generate simulated risk analysis when Gemini is not available.
        Uses rule-based logic to determine risk from sensor data.
        """
        import random
        
        # Determine risk type based on sensor readings
        risk_type = RiskType.LOW if hasattr(RiskType, 'LOW') else RiskType.FIRE
        risk_score = 0
        reasoning_steps = []
        
        # Fire risk analysis
        if data.temperature and data.temperature > 35:
            fire_risk = min((data.temperature - 35) * 5, 50)
            if data.humidity and data.humidity < 30:
                fire_risk += 25
            if data.wind_speed and data.wind_speed > 40:
                fire_risk += 15
            if data.vegetation_index and data.vegetation_index < 0.2:
                fire_risk += 10
            
            if fire_risk > risk_score:
                risk_score = fire_risk
                risk_type = RiskType.FIRE
                reasoning_steps = [
                    ReasoningStep(
                        step_number=1,
                        observation=f"Temperature detected at {data.temperature}°C, significantly above normal",
                        analysis="High temperatures combined with environmental factors increase ignition potential",
                        conclusion="Elevated fire risk conditions present"
                    ),
                    ReasoningStep(
                        step_number=2,
                        observation=f"Humidity at {data.humidity}%, wind speed at {data.wind_speed} km/h",
                        analysis="Low humidity and wind conditions can accelerate fire spread",
                        conclusion="Conditions favor rapid fire propagation"
                    ),
                ]
        
        # Flood risk analysis
        if data.precipitation and data.precipitation > 50:
            flood_risk = min((data.precipitation - 50) * 2, 60)
            if data.soil_moisture and data.soil_moisture > 80:
                flood_risk += 20
            
            if flood_risk > risk_score:
                risk_score = flood_risk
                risk_type = RiskType.FLOOD
                reasoning_steps = [
                    ReasoningStep(
                        step_number=1,
                        observation=f"Precipitation at {data.precipitation}mm, well above threshold",
                        analysis="Heavy rainfall can overwhelm drainage systems",
                        conclusion="Flood risk elevated in low-lying areas"
                    ),
                    ReasoningStep(
                        step_number=2,
                        observation=f"Soil moisture at {data.soil_moisture}%",
                        analysis="Saturated soil cannot absorb additional water",
                        conclusion="Surface runoff likely to increase"
                    ),
                ]
        
        # Earthquake risk analysis
        if data.seismic_activity and data.seismic_activity > 3.0:
            quake_risk = min(data.seismic_activity * 15, 90)
            
            if quake_risk > risk_score:
                risk_score = quake_risk
                risk_type = RiskType.EARTHQUAKE
                reasoning_steps = [
                    ReasoningStep(
                        step_number=1,
                        observation=f"Seismic activity detected at {data.seismic_activity} magnitude",
                        analysis="Magnitude above 3.0 can be felt by humans",
                        conclusion="Potential for structural damage if magnitude increases"
                    ),
                ]
        
        # Storm risk analysis
        if data.wind_speed and data.wind_speed > 60:
            storm_risk = min((data.wind_speed - 60) * 1.5, 70)
            if data.pressure and data.pressure < 1000:
                storm_risk += 20
            
            if storm_risk > risk_score:
                risk_score = storm_risk
                risk_type = RiskType.STORM
                reasoning_steps = [
                    ReasoningStep(
                        step_number=1,
                        observation=f"Wind speed at {data.wind_speed} km/h with pressure at {data.pressure} hPa",
                        analysis="High winds and low pressure indicate severe storm conditions",
                        conclusion="Storm damage likely to trees, structures, and power lines"
                    ),
                ]
        
        # Air quality risk analysis
        if data.air_quality_index and data.air_quality_index > 150:
            aqi_risk = min((data.air_quality_index - 150) * 0.3, 60)
            
            if aqi_risk > risk_score:
                risk_score = aqi_risk
                risk_type = RiskType.AIR_QUALITY
                reasoning_steps = [
                    ReasoningStep(
                        step_number=1,
                        observation=f"Air Quality Index at {data.air_quality_index} - Unhealthy level",
                        analysis="AQI above 150 poses health risks to sensitive groups",
                        conclusion="Outdoor activities should be limited for vulnerable populations"
                    ),
                ]
        
        # Default minimal risk
        if risk_score == 0:
            risk_score = random.uniform(5, 25)
            risk_type = random.choice(list(RiskType))
            reasoning_steps = [
                ReasoningStep(
                    step_number=1,
                    observation="Environmental readings within normal parameters",
                    analysis="No significant anomalies detected in current data",
                    conclusion="Baseline monitoring continues - low risk conditions"
                ),
            ]
        
        # Determine risk level from score
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MODERATE
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        # Generate recommendations based on risk type
        recommendations = self._get_recommendations(risk_type, risk_level)
        
        # Generate voice summary
        voice_summary = (
            f"Orbital Sentinel has detected a {risk_level.value} {risk_type.value} risk "
            f"with a score of {risk_score:.0f} out of 100 at coordinates "
            f"{data.location.latitude:.2f}, {data.location.longitude:.2f}. "
            f"{recommendations[0] if recommendations else 'Continue monitoring.'}"
        )
        
        return RiskPrediction(
            risk_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            risk_type=risk_type,
            risk_level=risk_level,
            risk_score=risk_score,
            location=data.location,
            title=f"{risk_level.value.title()} {risk_type.value.replace('_', ' ').title()} Risk Detected",
            description=f"Analysis of environmental data indicates {risk_level.value} "
                       f"{risk_type.value.replace('_', ' ')} risk conditions. "
                       f"Confidence level: {0.7 + risk_score/500:.1%}",
            reasoning_chain=reasoning_steps,
            affected_population=int(risk_score * 1000),
            recommended_actions=recommendations,
            confidence=0.7 + risk_score/500,
            raw_data=data,
            voice_summary=voice_summary,
        )
    
    def _get_recommendations(self, risk_type: RiskType, risk_level: RiskLevel) -> List[str]:
        """Get safety recommendations based on risk type and level"""
        recommendations = {
            RiskType.FIRE: [
                "Clear vegetation around structures",
                "Prepare evacuation routes",
                "Have fire extinguishers ready",
                "Monitor local fire department updates",
            ],
            RiskType.FLOOD: [
                "Move to higher ground if in flood zone",
                "Avoid driving through flooded areas",
                "Prepare emergency supplies",
                "Monitor weather alerts continuously",
            ],
            RiskType.EARTHQUAKE: [
                "Drop, Cover, and Hold On during shaking",
                "Stay away from windows and heavy objects",
                "Check for gas leaks after shaking stops",
                "Be prepared for aftershocks",
            ],
            RiskType.STORM: [
                "Secure loose outdoor objects",
                "Stay indoors and away from windows",
                "Charge electronic devices",
                "Have emergency supplies ready",
            ],
            RiskType.AIR_QUALITY: [
                "Limit outdoor activities",
                "Use air purifiers indoors",
                "Wear N95 masks if going outside",
                "Keep windows and doors closed",
            ],
            RiskType.DROUGHT: [
                "Conserve water usage",
                "Check for fire hazards",
                "Monitor crop and livestock conditions",
                "Follow water restriction guidelines",
            ],
            RiskType.VOLCANIC: [
                "Monitor official volcanic alerts",
                "Prepare evacuation kit",
                "Stay away from volcanic zones",
                "Protect respiratory system from ash",
            ],
            RiskType.TSUNAMI: [
                "Move to high ground immediately",
                "Do not return until all-clear is given",
                "Stay away from coastal areas",
                "Follow official evacuation orders",
            ],
        }
        
        base_recs = recommendations.get(risk_type, ["Monitor situation", "Follow official guidance"])
        
        # Add urgency based on risk level
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return ["IMMEDIATE ACTION REQUIRED: " + base_recs[0]] + base_recs[1:]
        
        return base_recs


# Singleton instance
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get or create the singleton Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
