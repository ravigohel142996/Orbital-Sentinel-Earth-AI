"""
==============================================================================
Orbital Sentinel - Streamlit Frontend
Real-time Earth risk prediction dashboard with map visualization
==============================================================================
"""

import asyncio
import base64
import json
import time
from datetime import datetime
from typing import Optional

import folium
import httpx
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Orbital Sentinel 🛰️",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# Configuration
# ==============================================================================

API_BASE_URL = "http://localhost:8000"

# Risk level colors
RISK_COLORS = {
    "critical": "#FF0000",
    "high": "#FF6600",
    "moderate": "#FFCC00",
    "low": "#66CC00",
    "minimal": "#00CC66"
}

# Risk type icons
RISK_ICONS = {
    "fire": "🔥",
    "flood": "🌊",
    "earthquake": "🌋",
    "storm": "🌪️",
    "air_quality": "💨",
    "drought": "🏜️",
    "volcanic": "🌋",
    "tsunami": "🌊"
}


# ==============================================================================
# Custom CSS
# ==============================================================================

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    /* Main container */
    .main {
        background-color: #0E1117;
    }
    
    /* Headers */
    .stMarkdown h1 {
        color: #00D4FF;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #2D3748 100%);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Risk alert cards */
    .risk-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #2D3748 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    .risk-critical {
        border-left-color: #FF0000;
        background: linear-gradient(135deg, #2D1F1F 0%, #3D2828 100%);
    }
    
    .risk-high {
        border-left-color: #FF6600;
        background: linear-gradient(135deg, #2D251F 0%, #3D3428 100%);
    }
    
    .risk-moderate {
        border-left-color: #FFCC00;
        background: linear-gradient(135deg, #2D2B1F 0%, #3D3928 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0E1117 0%, #1A1F2E 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D4FF 0%, #00A3CC 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00A3CC 0%, #0088AA 100%);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
    }
    
    /* Animated header */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Status indicator */
    .status-online {
        color: #00FF00;
        font-weight: bold;
    }
    
    .status-offline {
        color: #FF0000;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# API Client
# ==============================================================================

class OrbitalSentinelClient:
    """API client for Orbital Sentinel backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        """Make HTTP request to API"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(method, f"{self.base_url}{endpoint}", **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            st.error("⚠️ Cannot connect to backend. Please ensure the API server is running.")
            return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def health_check(self) -> Optional[dict]:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    def get_predictions(self, limit: int = 50) -> Optional[dict]:
        """Get recent predictions"""
        return self._make_request("GET", f"/predictions?limit={limit}")
    
    def get_stats(self) -> Optional[dict]:
        """Get dashboard statistics"""
        return self._make_request("GET", "/predictions/stats")
    
    def simulate_analysis(self) -> Optional[dict]:
        """Trigger simulation and analysis"""
        return self._make_request("GET", "/analyze/simulate")
    
    def get_simulator_status(self) -> Optional[dict]:
        """Get simulator status"""
        return self._make_request("GET", "/simulator/status")
    
    def start_simulator(self) -> Optional[dict]:
        """Start the simulator"""
        return self._make_request("POST", "/simulator/start")
    
    def stop_simulator(self) -> Optional[dict]:
        """Stop the simulator"""
        return self._make_request("POST", "/simulator/stop")


# Initialize client
client = OrbitalSentinelClient()


# ==============================================================================
# UI Components
# ==============================================================================

def render_header():
    """Render the main header"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <h1 style="text-align: center; font-size: 3em; margin-bottom: 0;">
            🛰️ ORBITAL SENTINEL
        </h1>
        <p style="text-align: center; color: #00D4FF; font-size: 1.2em; margin-top: 0;">
            Real-Time Earth Risk Prediction System
        </p>
        """, unsafe_allow_html=True)


def render_status_bar():
    """Render the status bar"""
    health = client.health_check()
    
    if health:
        cols = st.columns(6)
        
        services = health.get("services", {})
        
        with cols[0]:
            status = "🟢" if services.get("gemini") else "🟡"
            st.markdown(f"**Gemini AI** {status}")
        
        with cols[1]:
            status = "🟢" if services.get("elevenlabs") else "🟡"
            st.markdown(f"**Voice** {status}")
        
        with cols[2]:
            status = "🟢" if services.get("streaming") else "🟡"
            st.markdown(f"**Streaming** {status}")
        
        with cols[3]:
            status = "🟢" if services.get("storage") else "🔴"
            st.markdown(f"**Storage** {status}")
        
        with cols[4]:
            status = "🟢" if services.get("simulator") else "⚪"
            st.markdown(f"**Simulator** {status}")
        
        with cols[5]:
            st.markdown(f"**API** 🟢 Online")
    else:
        st.error("⚠️ Backend Offline - Please start the API server")


def render_metrics_dashboard():
    """Render the metrics dashboard"""
    stats = client.get_stats()
    
    if not stats:
        # Show placeholder metrics
        stats = {
            "total_predictions": 0,
            "active_risks": 0,
            "critical_risks": 0,
            "regions_monitored": 0
        }
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            label="📊 Total Predictions",
            value=stats.get("total_predictions", 0),
            delta="+5 last hour"
        )
    
    with cols[1]:
        st.metric(
            label="⚠️ Active Risks",
            value=stats.get("active_risks", 0),
            delta="3 new"
        )
    
    with cols[2]:
        st.metric(
            label="🚨 Critical Alerts",
            value=stats.get("critical_risks", 0),
            delta="-1" if stats.get("critical_risks", 0) > 0 else None,
            delta_color="inverse"
        )
    
    with cols[3]:
        st.metric(
            label="🌍 Regions Monitored",
            value=stats.get("regions_monitored", 0) or 20,
        )


def render_world_map(predictions: list):
    """Render the world map with risk markers"""
    # Create base map
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB dark_matter"
    )
    
    # Add risk markers
    for pred in predictions[:50]:  # Limit markers
        location = pred.get("location", {})
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        
        if lat == 0 and lon == 0:
            continue
        
        risk_level = pred.get("risk_level", "minimal")
        risk_type = pred.get("risk_type", "unknown")
        risk_score = pred.get("risk_score", 0)
        
        # Determine marker color and icon
        color = RISK_COLORS.get(risk_level, "#FFFFFF")
        icon_emoji = RISK_ICONS.get(risk_type, "⚠️")
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="color: {color};">{icon_emoji} {risk_type.upper()}</h4>
            <p><strong>Level:</strong> {risk_level.upper()}</p>
            <p><strong>Score:</strong> {risk_score:.1f}/100</p>
            <p><strong>Location:</strong> {location.get('region', 'Unknown')}</p>
            <p><strong>Time:</strong> {pred.get('timestamp', '')[:19]}</p>
        </div>
        """
        
        # Add circle marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=max(5, risk_score / 10),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{icon_emoji} {risk_type} - {risk_level}"
        ).add_to(m)
    
    # Render map
    st_folium(m, width=None, height=500, returned_objects=[])


def render_risk_alerts(predictions: list):
    """Render risk alert cards"""
    st.subheader("📋 Recent Risk Alerts")
    
    if not predictions:
        st.info("No recent predictions. Click 'Generate Analysis' to create one.")
        return
    
    for pred in predictions[:10]:
        risk_level = pred.get("risk_level", "minimal")
        risk_type = pred.get("risk_type", "unknown")
        risk_score = pred.get("risk_score", 0)
        location = pred.get("location", {})
        
        icon = RISK_ICONS.get(risk_type, "⚠️")
        color = RISK_COLORS.get(risk_level, "#FFFFFF")
        
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            
            with col1:
                st.markdown(f"### {icon}")
            
            with col2:
                st.markdown(f"**{pred.get('title', 'Unknown Risk')}**")
                st.caption(f"📍 {location.get('region', 'Unknown')}, {location.get('country', '')}")
            
            with col3:
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{risk_level.upper()}</span>", unsafe_allow_html=True)
            
            with col4:
                st.progress(risk_score / 100)
                st.caption(f"{risk_score:.0f}/100")
            
            # Expandable details
            with st.expander("View Details"):
                st.markdown(f"**Description:** {pred.get('description', 'N/A')}")
                
                # Reasoning chain
                reasoning = pred.get("reasoning_chain", [])
                if reasoning:
                    st.markdown("**Reasoning Chain:**")
                    for step in reasoning:
                        st.markdown(f"""
                        - **Step {step.get('step_number', '?')}:** {step.get('observation', '')}
                          - *Analysis:* {step.get('analysis', '')}
                          - *Conclusion:* {step.get('conclusion', '')}
                        """)
                
                # Recommendations
                recommendations = pred.get("recommended_actions", [])
                if recommendations:
                    st.markdown("**Recommended Actions:**")
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
            
            st.divider()


def render_sidebar():
    """Render the sidebar controls"""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        st.divider()
        
        # Simulator controls
        st.markdown("### 🔄 Data Simulator")
        
        sim_status = client.get_simulator_status()
        is_running = sim_status.get("running", False) if sim_status else False
        
        if is_running:
            st.success("Simulator Running")
            if st.button("⏹️ Stop Simulator", use_container_width=True):
                client.stop_simulator()
                st.rerun()
        else:
            st.warning("Simulator Stopped")
            if st.button("▶️ Start Simulator", use_container_width=True):
                client.start_simulator()
                st.rerun()
        
        st.divider()
        
        # Manual analysis
        st.markdown("### 🔬 Manual Analysis")
        
        if st.button("🎲 Generate Analysis", use_container_width=True, type="primary"):
            with st.spinner("Analyzing..."):
                result = client.simulate_analysis()
                if result and result.get("success"):
                    st.success("Analysis Complete!")
                    pred = result.get("prediction", {})
                    st.info(f"Risk: {pred.get('risk_type', 'Unknown')} - {pred.get('risk_level', 'Unknown')}")
                    time.sleep(1)
                    st.rerun()
        
        st.divider()
        
        # Filters
        st.markdown("### 🔍 Filters")
        
        risk_filter = st.selectbox(
            "Risk Type",
            ["All", "fire", "flood", "earthquake", "storm", "air_quality", "drought", "volcanic", "tsunami"]
        )
        
        level_filter = st.selectbox(
            "Risk Level",
            ["All", "critical", "high", "moderate", "low", "minimal"]
        )
        
        st.divider()
        
        # Auto-refresh
        st.markdown("### ⏱️ Auto-Refresh")
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        refresh_interval = st.slider("Interval (seconds)", 5, 60, 10)
        
        st.divider()
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Orbital Sentinel** uses:
        - 🤖 Gemini 2.0 AI
        - 📡 Confluent Kafka
        - 🗣️ ElevenLabs Voice
        - 🌍 Real-time Data
        
        Made with ❤️ for Earth
        """)
        
        return {
            "risk_filter": risk_filter if risk_filter != "All" else None,
            "level_filter": level_filter if level_filter != "All" else None,
            "auto_refresh": auto_refresh,
            "refresh_interval": refresh_interval
        }


def render_analytics(predictions: list):
    """Render analytics section"""
    st.subheader("📈 Risk Analytics")
    
    if not predictions:
        st.info("No data available for analytics")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk type distribution
        st.markdown("**Risk Type Distribution**")
        risk_types = {}
        for pred in predictions:
            rt = pred.get("risk_type", "unknown")
            risk_types[rt] = risk_types.get(rt, 0) + 1
        
        if risk_types:
            df = pd.DataFrame(list(risk_types.items()), columns=["Risk Type", "Count"])
            st.bar_chart(df.set_index("Risk Type"))
    
    with col2:
        # Risk level distribution
        st.markdown("**Risk Level Distribution**")
        risk_levels = {}
        for pred in predictions:
            rl = pred.get("risk_level", "unknown")
            risk_levels[rl] = risk_levels.get(rl, 0) + 1
        
        if risk_levels:
            df = pd.DataFrame(list(risk_levels.items()), columns=["Risk Level", "Count"])
            st.bar_chart(df.set_index("Risk Level"))


# ==============================================================================
# Main Application
# ==============================================================================

def main():
    """Main application entry point"""
    apply_custom_css()
    
    # Render header
    render_header()
    st.divider()
    
    # Render status bar
    render_status_bar()
    st.divider()
    
    # Render sidebar and get filters
    filters = render_sidebar()
    
    # Render metrics
    render_metrics_dashboard()
    st.divider()
    
    # Get predictions
    predictions_data = client.get_predictions(limit=100)
    predictions = predictions_data.get("predictions", []) if predictions_data else []
    
    # Apply filters
    if filters["risk_filter"]:
        predictions = [p for p in predictions if p.get("risk_type") == filters["risk_filter"]]
    if filters["level_filter"]:
        predictions = [p for p in predictions if p.get("risk_level") == filters["level_filter"]]
    
    # Create two columns for map and alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Global Risk Map")
        render_world_map(predictions)
    
    with col2:
        render_risk_alerts(predictions)
    
    st.divider()
    
    # Analytics section
    render_analytics(predictions)
    
    # Auto-refresh
    if filters["auto_refresh"]:
        time.sleep(filters["refresh_interval"])
        st.rerun()


if __name__ == "__main__":
    main()
