# 🛰️ Orbital Sentinel - API Documentation

Complete API reference for the Orbital Sentinel backend.

## Base URL

```
Local: http://localhost:8000
Production: https://your-deployment-url.com
```

## Authentication

Currently, the API does not require authentication. For production, implement API key or OAuth2.

---

## Health Endpoints

### GET /

Get API information and status.

**Response:**
```json
{
    "name": "Orbital Sentinel API",
    "version": "1.0.0",
    "description": "Real-time Earth risk prediction system",
    "docs": "/docs",
    "status": "operational"
}
```

### GET /health

Check health status of all services.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
        "gemini": true,
        "elevenlabs": false,
        "streaming": true,
        "storage": true,
        "simulator": true
    },
    "version": "1.0.0"
}
```

### GET /config

Get configuration status (without secrets).

**Response:**
```json
{
    "gemini_configured": true,
    "elevenlabs_configured": false,
    "kafka_configured": false,
    "simulation_mode": true
}
```

---

## Analysis Endpoints

### POST /analyze

Analyze environmental data for risk prediction.

**Request Body:**
```json
{
    "data": {
        "timestamp": "2024-01-15T10:30:00Z",
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "region": "Los Angeles",
            "country": "USA"
        },
        "temperature": 42.5,
        "humidity": 15.0,
        "wind_speed": 45.0,
        "wind_direction": 270,
        "precipitation": 0.0,
        "pressure": 1013.25,
        "air_quality_index": 85,
        "seismic_activity": 0.5,
        "soil_moisture": 12.0,
        "vegetation_index": 0.15,
        "source": "sensor_network"
    },
    "include_reasoning": true,
    "generate_voice": false
}
```

**Response:**
```json
{
    "success": true,
    "prediction": {
        "risk_id": "uuid-string",
        "timestamp": "2024-01-15T10:30:05Z",
        "risk_type": "fire",
        "risk_level": "high",
        "risk_score": 72.5,
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "region": "Los Angeles",
            "country": "USA"
        },
        "title": "High Fire Risk Detected",
        "description": "Analysis indicates elevated fire risk...",
        "reasoning_chain": [
            {
                "step_number": 1,
                "observation": "Temperature at 42.5°C, significantly above normal",
                "analysis": "High temperatures increase ignition potential",
                "conclusion": "Elevated fire risk conditions present"
            }
        ],
        "affected_population": 50000,
        "recommended_actions": [
            "IMMEDIATE ACTION REQUIRED: Clear vegetation around structures",
            "Prepare evacuation routes",
            "Monitor local fire department updates"
        ],
        "confidence": 0.85,
        "voice_summary": "Orbital Sentinel has detected a high fire risk..."
    },
    "audio_url": null,
    "processing_time_ms": 1250.5
}
```

### POST /analyze/batch

Analyze multiple data points.

**Request Body:**
```json
[
    {
        "timestamp": "2024-01-15T10:30:00Z",
        "location": {"latitude": 34.0522, "longitude": -118.2437},
        "temperature": 42.5,
        "humidity": 15.0
    },
    {
        "timestamp": "2024-01-15T10:30:00Z",
        "location": {"latitude": 37.7749, "longitude": -122.4194},
        "temperature": 22.0,
        "humidity": 65.0
    }
]
```

**Response:**
```json
{
    "results": [
        {"success": true, "prediction": {...}},
        {"success": true, "prediction": {...}}
    ],
    "total": 2
}
```

### GET /analyze/simulate

Generate simulated data and analyze it.

**Response:**
```json
{
    "success": true,
    "prediction": {...},
    "processing_time_ms": 1100.0
}
```

---

## Predictions Endpoints

### GET /predictions

Get recent predictions.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 50 | Max results (1-200) |
| risk_type | string | null | Filter by type |
| risk_level | string | null | Filter by level |

**Example:**
```
GET /predictions?limit=10&risk_type=fire&risk_level=high
```

**Response:**
```json
{
    "predictions": [...],
    "count": 10
}
```

### GET /predictions/stats

Get dashboard statistics.

**Response:**
```json
{
    "total_predictions": 150,
    "active_risks": 12,
    "critical_risks": 2,
    "regions_monitored": 20,
    "last_update": "2024-01-15T10:30:00Z",
    "risk_breakdown": {
        "fire": 45,
        "flood": 30,
        "storm": 25,
        "earthquake": 20,
        "air_quality": 30
    }
}
```

### DELETE /predictions/old

Clear old predictions.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 7 | Days to keep (1-30) |

**Response:**
```json
{
    "removed": 45,
    "days_cleared": 7
}
```

---

## Voice Endpoints

### POST /voice/generate

Generate speech from text.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| text | string | Yes | Text to convert |
| voice_id | string | No | Voice ID override |

**Response:**
```json
{
    "audio_base64": "base64-encoded-audio-data",
    "format": "mp3"
}
```

### GET /voice/voices

List available voices.

**Response:**
```json
{
    "voices": [
        {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "name": "Rachel",
            "description": "Calm and professional"
        }
    ]
}
```

---

## Streaming Endpoints

### POST /stream/publish

Publish data to Kafka stream.

**Request Body:**
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "location": {"latitude": 34.0522, "longitude": -118.2437},
    "temperature": 25.0,
    "humidity": 50.0
}
```

**Response:**
```json
{
    "status": "published",
    "timestamp": "2024-01-15T10:30:01Z"
}
```

### GET /stream/status

Get streaming service status.

**Response:**
```json
{
    "kafka_available": false,
    "fallback_active": true,
    "fallback_queue_size": 25
}
```

---

## Simulator Endpoints

### POST /simulator/start

Start the background simulator.

**Response:**
```json
{
    "status": "started"
}
```

### POST /simulator/stop

Stop the background simulator.

**Response:**
```json
{
    "status": "stopped"
}
```

### GET /simulator/status

Get simulator status.

**Response:**
```json
{
    "running": true
}
```

### GET /simulator/generate

Generate sample data without analysis.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| count | int | 1 | Number of samples (1-20) |

**Response:**
```json
{
    "data": [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "location": {...},
            "temperature": 28.5,
            "humidity": 55.0,
            ...
        }
    ]
}
```

---

## Data Models

### EnvironmentData

| Field | Type | Description |
|-------|------|-------------|
| timestamp | datetime | Data timestamp |
| location | GeoLocation | Geographic location |
| temperature | float | Temperature (°C) |
| humidity | float | Humidity (%) |
| wind_speed | float | Wind speed (km/h) |
| wind_direction | float | Wind direction (degrees) |
| precipitation | float | Precipitation (mm) |
| pressure | float | Pressure (hPa) |
| air_quality_index | float | AQI (0-500) |
| seismic_activity | float | Magnitude |
| soil_moisture | float | Soil moisture (%) |
| vegetation_index | float | NDVI (-1 to 1) |

### RiskPrediction

| Field | Type | Description |
|-------|------|-------------|
| risk_id | string | Unique identifier |
| risk_type | enum | fire, flood, earthquake, storm, air_quality, drought, volcanic, tsunami |
| risk_level | enum | critical, high, moderate, low, minimal |
| risk_score | float | Score 0-100 |
| reasoning_chain | array | Chain of thought steps |
| recommended_actions | array | Safety recommendations |
| confidence | float | Prediction confidence (0-1) |

---

## Error Handling

### Error Response Format

```json
{
    "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limits

Currently no rate limits. Implement for production:
- 100 requests/minute per IP
- 10 analysis requests/minute per IP

---

## Examples

### cURL

```bash
# Get health status
curl -X GET http://localhost:8000/health

# Run simulation
curl -X GET http://localhost:8000/analyze/simulate

# Analyze custom data
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "location": {"latitude": 34.05, "longitude": -118.24},
      "temperature": 40,
      "humidity": 20
    }
  }'
```

### Python

```python
import httpx

# Async example
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/health")
    print(response.json())
```

### JavaScript

```javascript
// Fetch example
fetch('http://localhost:8000/analyze/simulate')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

For more examples, see the [Swagger UI](http://localhost:8000/docs).
