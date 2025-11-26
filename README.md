# 🛰️ Orbital Sentinel - Earth Risk Prediction AI

<div align="center">

![Orbital Sentinel](https://img.shields.io/badge/🛰️-Orbital%20Sentinel-00D4FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?style=for-the-badge&logo=streamlit)

**Real-Time Earth Risk Prediction System**

*Gemini 2.0 + Confluent Data Streaming + ElevenLabs Voice Agent + Streamlit UI*

[Live Demo](#) • [Documentation](docs/ARCHITECTURE.md) • [API Reference](docs/API.md) • [Setup Guide](docs/SETUP.md)

</div>

---

## 🌍 Overview

**Orbital Sentinel** is a futuristic multi-agent AI system that predicts global environmental risks (fires, floods, earthquakes, storms, air quality) using real-time data streams and advanced AI reasoning models.

### ✨ Key Features

- 🤖 **Gemini 2.0 AI Analysis** - Chain-of-thought reasoning for risk prediction
- 📡 **Confluent Kafka Streaming** - Real-time data processing pipeline
- 🗣️ **ElevenLabs Voice Alerts** - AI-generated voice notifications
- 🗺️ **Interactive World Map** - Real-time risk visualization
- 📊 **Smart Dashboard** - Live metrics and analytics
- 🔄 **Data Simulation** - Realistic environmental data generator

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     🛰️ ORBITAL SENTINEL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │Streamlit │◄──►│ FastAPI  │◄──►│  Gemini  │    │ElevenLabs│ │
│   │Dashboard │    │ Backend  │    │    AI    │    │  Voice   │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│         │              │                               │       │
│         └──────────────┼───────────────────────────────┘       │
│                        │                                       │
│              ┌─────────┴─────────┐                             │
│              │ Confluent Kafka   │                             │
│              │ Data Streaming    │                             │
│              └─────────┬─────────┘                             │
│                        │                                       │
│              ┌─────────┴─────────┐                             │
│              │  Data Simulator   │                             │
│              │  (20+ Locations)  │                             │
│              └───────────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Gemini API Key](https://aistudio.google.com/apikey) (required)
- [ElevenLabs API Key](https://elevenlabs.io/) (optional)
- [Confluent Cloud](https://confluent.cloud/) (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/ravigohel142996/Orbital-Sentinel-Earth-AI.git
cd Orbital-Sentinel-Earth-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

**Access:**
- 🎨 Dashboard: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

---

## 📊 Risk Types Monitored

| Risk | Icon | Indicators |
|------|------|------------|
| Fire | 🔥 | High temperature, low humidity, dry vegetation |
| Flood | 🌊 | Heavy precipitation, saturated soil |
| Earthquake | 🌋 | Seismic activity > 3.0 magnitude |
| Storm | 🌪️ | High wind speed, low pressure |
| Air Quality | 💨 | AQI > 150 (Unhealthy) |
| Drought | 🏜️ | Low soil moisture |
| Volcanic | 🌋 | Seismic + thermal anomalies |
| Tsunami | 🌊 | Coastal seismic activity |

---

## 🧠 AI Reasoning Chain

Orbital Sentinel uses **chain-of-thought reasoning** to analyze environmental data:

1. **📊 Observation** - Analyze sensor readings
2. **🔍 Pattern Recognition** - Identify anomalies
3. **⚖️ Risk Assessment** - Calculate risk score
4. **👥 Impact Analysis** - Estimate affected population
5. **💡 Recommendations** - Generate safety actions

---

## 📁 Project Structure

```
Orbital-Sentinel-Earth-AI/
├── frontend/
│   └── app.py              # Streamlit dashboard
├── backend/
│   ├── main.py             # FastAPI application
│   └── models.py           # Data models
├── services/
│   ├── gemini_service.py   # Gemini AI integration
│   ├── voice_service.py    # ElevenLabs integration
│   └── storage_service.py  # Data persistence
├── streaming/
│   ├── data_simulator.py   # Data generator
│   └── kafka_service.py    # Kafka integration
├── configs/
│   └── config.py           # Configuration
├── docs/
│   ├── ARCHITECTURE.md     # System architecture
│   ├── SETUP.md            # Setup guide
│   └── API.md              # API documentation
└── requirements.txt        # Dependencies
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health status |
| `/analyze` | POST | Analyze environmental data |
| `/analyze/simulate` | GET | Generate + analyze data |
| `/predictions` | GET | Get recent predictions |
| `/predictions/stats` | GET | Dashboard statistics |
| `/voice/generate` | POST | Text-to-speech |
| `/simulator/start` | POST | Start data simulator |

[Full API Documentation →](docs/API.md)

---

## ⚙️ Configuration

Create a `.env` file:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
ELEVENLABS_API_KEY=your_elevenlabs_key
KAFKA_BOOTSTRAP_SERVERS=your_kafka_servers
KAFKA_API_KEY=your_kafka_key
KAFKA_API_SECRET=your_kafka_secret

# Settings
SIMULATION_MODE=true
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit, Folium |
| **Backend** | FastAPI, Uvicorn |
| **AI** | Google Gemini 2.0 |
| **Voice** | ElevenLabs |
| **Streaming** | Confluent Kafka |
| **Data** | Pydantic, JSON |

---

## 🚀 Deployment

### Render (Backend)
```yaml
# render.yaml
services:
  - type: web
    name: orbital-sentinel-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Streamlit Cloud (Frontend)
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Set secrets in dashboard

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

---

## 🙏 Acknowledgments

- Google Gemini AI
- Confluent Cloud
- ElevenLabs
- Streamlit Team

---

<div align="center">

**Made with ❤️ for Earth 🌍**

*Protecting our planet, one prediction at a time*

</div>  
