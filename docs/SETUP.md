# 🛰️ Orbital Sentinel - Setup Guide

Complete setup instructions for running Orbital Sentinel locally and in production.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- A code editor (VS Code recommended)

## 🔑 API Keys Required

### 1. Google Gemini API Key (Required)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 2. ElevenLabs API Key (Optional - for voice)

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Create an account or sign in
3. Go to Profile Settings → API
4. Copy your API key

### 3. Confluent Cloud (Optional - for real Kafka)

1. Go to [Confluent Cloud](https://confluent.cloud/)
2. Create a free account
3. Create a cluster
4. Create an API key and secret
5. Note the bootstrap server address

## 🚀 Local Development Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/ravigohel142996/Orbital-Sentinel-Earth-AI.git
cd Orbital-Sentinel-Earth-AI
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Use your favorite editor:
nano .env
# or
code .env
```

Required configuration in `.env`:

```env
# Required - Get from https://aistudio.google.com/apikey
GEMINI_API_KEY=your_actual_gemini_api_key

# Optional - Get from https://elevenlabs.io/
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Kafka settings (optional, simulation mode works without)
KAFKA_BOOTSTRAP_SERVERS=
KAFKA_API_KEY=
KAFKA_API_SECRET=

# Enable simulation mode for demo (recommended for local dev)
SIMULATION_MODE=true
```

### Step 5: Start the Backend Server

```bash
# From the project root
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Starting Orbital Sentinel API
```

### Step 6: Start the Frontend (New Terminal)

```bash
# Open a new terminal, activate venv
cd Orbital-Sentinel-Earth-AI
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Streamlit
cd frontend
streamlit run app.py --server.port 8501
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 7: Access the Application

1. **Dashboard**: Open http://localhost:8501 in your browser
2. **API Docs**: Open http://localhost:8000/docs for Swagger UI
3. **Health Check**: Visit http://localhost:8000/health

## 🧪 Testing the System

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Generate simulated analysis
curl http://localhost:8000/analyze/simulate

# Get predictions
curl http://localhost:8000/predictions
```

### Test with Python

```python
import httpx

# Test the API
response = httpx.get("http://localhost:8000/health")
print(response.json())

# Generate an analysis
response = httpx.get("http://localhost:8000/analyze/simulate")
print(response.json())
```

## 🐛 Troubleshooting

### Problem: "Cannot connect to backend"

**Solution:**
1. Make sure the backend is running on port 8000
2. Check if another process is using port 8000:
   ```bash
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows
   ```

### Problem: "Gemini API error"

**Solution:**
1. Verify your API key is correct
2. Check if you have API quota available
3. Ensure the key is in `.env` file
4. Restart the backend after changing `.env`

### Problem: Import errors

**Solution:**
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Problem: Streamlit won't start

**Solution:**
1. Check if port 8501 is available
2. Try a different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```

## ☁️ Production Deployment

### Option 1: Render (Backend)

1. Create a `render.yaml` in project root
2. Push to GitHub
3. Connect repo to Render
4. Set environment variables in Render dashboard

### Option 2: Streamlit Cloud (Frontend)

1. Push to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Deploy from your repository
4. Set secrets in Streamlit Cloud settings

### Option 3: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Backend
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t orbital-sentinel .
docker run -p 8000:8000 --env-file .env orbital-sentinel
```

## 📊 Performance Tips

1. **Reduce refresh interval**: In the sidebar, increase auto-refresh interval
2. **Limit predictions**: Use filters to show fewer markers on map
3. **Disable voice**: If not needed, don't request voice generation
4. **Use batch analysis**: For multiple data points

## 🔐 Security Notes

1. Never commit `.env` file to git
2. Use environment variables for all secrets
3. Rotate API keys periodically
4. Enable CORS only for trusted domains in production

---

Need help? Open an issue on GitHub! 🚀
