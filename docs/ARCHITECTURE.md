# ==============================================================================
#                         🛰️ ORBITAL SENTINEL
#            Real-Time Earth Risk Prediction System
# ==============================================================================

## 🌍 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORBITAL SENTINEL                                   │
│                    Earth Risk Prediction System                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   FRONTEND    │          │   BACKEND     │          │   STREAMING   │
│   Streamlit   │◄────────►│   FastAPI     │◄────────►│   Confluent   │
│               │          │               │          │   Kafka       │
│ • Dashboard   │          │ • REST API    │          │               │
│ • Map View    │          │ • Async Ops   │          │ • Producer    │
│ • Alerts      │          │ • WebSocket   │          │ • Consumer    │
└───────────────┘          └───────────────┘          └───────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   GEMINI AI   │          │  ELEVENLABS   │          │   STORAGE     │
│   Risk        │          │   Voice       │          │   JSON/DB     │
│   Analysis    │          │   Output      │          │               │
│               │          │               │          │ • Predictions │
│ • Chain of    │          │ • TTS         │          │ • Statistics  │
│   Thought     │          │ • Alerts      │          │ • Logs        │
│ • Prediction  │          │ • Summaries   │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │      DATA SIMULATOR       │
                    │                           │
                    │ • Environmental Sensors   │
                    │ • Weather Data           │
                    │ • Seismic Activity       │
                    │ • Air Quality Index      │
                    └───────────────────────────┘
```

## 📊 Data Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Sensor Data │───►│    Kafka     │───►│   Gemini     │───►│  Dashboard   │
│  (Simulated) │    │   Stream     │    │   Analysis   │    │   Display    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │                   │
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
   Environment         Real-time           AI Reasoning        Visualization
   Readings            Processing          Chain                + Voice Alert
```

## 🧠 AI Reasoning Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                    GEMINI 2.0 REASONING                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: OBSERVATION                                            │
│  ├── Analyze sensor readings                                    │
│  └── Identify anomalies                                         │
│                                                                 │
│  Step 2: PATTERN RECOGNITION                                    │
│  ├── Compare with historical data                               │
│  └── Detect concerning trends                                   │
│                                                                 │
│  Step 3: RISK ASSESSMENT                                        │
│  ├── Determine risk type                                        │
│  ├── Calculate risk score (0-100)                               │
│  └── Assign severity level                                      │
│                                                                 │
│  Step 4: IMPACT ANALYSIS                                        │
│  ├── Estimate affected population                               │
│  └── Predict infrastructure impact                              │
│                                                                 │
│  Step 5: RECOMMENDATIONS                                        │
│  ├── Generate safety actions                                    │
│  └── Prioritize responses                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Risk Types & Levels

```
┌──────────────────┬────────────────────────────────────────────┐
│   RISK TYPE      │   INDICATORS                               │
├──────────────────┼────────────────────────────────────────────┤
│ 🔥 Fire          │ High temp, low humidity, dry vegetation    │
│ 🌊 Flood         │ Heavy precipitation, saturated soil        │
│ 🌋 Earthquake    │ Seismic activity > 3.0 magnitude           │
│ 🌪️ Storm         │ High wind speed, low pressure              │
│ 💨 Air Quality   │ AQI > 150 (Unhealthy levels)               │
│ 🏜️ Drought       │ Low soil moisture, low precipitation       │
│ 🌋 Volcanic      │ Seismic + thermal anomalies                │
│ 🌊 Tsunami       │ Coastal seismic activity                   │
└──────────────────┴────────────────────────────────────────────┘

┌──────────────────┬────────────────────────────────────────────┐
│   RISK LEVEL     │   SCORE RANGE      │   COLOR              │
├──────────────────┼────────────────────┼──────────────────────┤
│ 🔴 CRITICAL      │   80-100           │   Red                │
│ 🟠 HIGH          │   60-79            │   Orange             │
│ 🟡 MODERATE      │   40-59            │   Yellow             │
│ 🟢 LOW           │   20-39            │   Light Green        │
│ ⚪ MINIMAL       │   0-19             │   Green              │
└──────────────────┴────────────────────┴──────────────────────┘
```

## 🔧 API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI ENDPOINTS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HEALTH                                                         │
│  ├── GET  /                 API info                            │
│  ├── GET  /health           Service status                      │
│  └── GET  /config           Configuration status                │
│                                                                 │
│  ANALYSIS                                                       │
│  ├── POST /analyze          Analyze sensor data                 │
│  ├── POST /analyze/batch    Batch analysis                      │
│  └── GET  /analyze/simulate Simulate + analyze                  │
│                                                                 │
│  PREDICTIONS                                                    │
│  ├── GET  /predictions      List predictions                    │
│  ├── GET  /predictions/stats Dashboard stats                    │
│  └── DEL  /predictions/old  Clear old data                      │
│                                                                 │
│  VOICE                                                          │
│  ├── POST /voice/generate   Text to speech                      │
│  └── GET  /voice/voices     List voices                         │
│                                                                 │
│  STREAMING                                                      │
│  ├── POST /stream/publish   Publish to Kafka                    │
│  └── GET  /stream/status    Stream status                       │
│                                                                 │
│  SIMULATOR                                                      │
│  ├── POST /simulator/start  Start simulator                     │
│  ├── POST /simulator/stop   Stop simulator                      │
│  ├── GET  /simulator/status Get status                          │
│  └── GET  /simulator/generate Generate sample data              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Orbital-Sentinel-Earth-AI/
│
├── frontend/
│   └── app.py              # Streamlit dashboard
│
├── backend/
│   ├── __init__.py         # Package exports
│   ├── main.py             # FastAPI application
│   └── models.py           # Pydantic data models
│
├── services/
│   ├── __init__.py         # Package exports
│   ├── gemini_service.py   # Gemini AI integration
│   ├── voice_service.py    # ElevenLabs integration
│   └── storage_service.py  # JSON storage
│
├── streaming/
│   ├── __init__.py         # Package exports
│   ├── data_simulator.py   # Environmental data generator
│   └── kafka_service.py    # Confluent Kafka integration
│
├── configs/
│   ├── __init__.py         # Package exports
│   └── config.py           # Configuration management
│
├── docs/
│   ├── ARCHITECTURE.md     # This file
│   ├── SETUP.md            # Setup instructions
│   └── API.md              # API documentation
│
├── data/
│   ├── predictions.json    # Stored predictions
│   └── stats.json          # Dashboard statistics
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── README.md               # Project overview
└── Procfile                # Deployment config
```

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ravigohel142996/Orbital-Sentinel-Earth-AI.git
cd Orbital-Sentinel-Earth-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Start backend
cd backend && uvicorn main:app --reload --port 8000

# 6. Start frontend (new terminal)
cd frontend && streamlit run app.py --server.port 8501
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | No |
| `KAFKA_BOOTSTRAP_SERVERS` | Confluent Kafka servers | No |
| `KAFKA_API_KEY` | Confluent API key | No |
| `KAFKA_API_SECRET` | Confluent API secret | No |
| `SIMULATION_MODE` | Enable simulation (true/false) | Yes |

---

Made with ❤️ for Earth 🌍
