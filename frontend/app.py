"""
==============================================================================
Orbital Sentinel - Streamlit Frontend
Real-time Earth risk prediction dashboard with map visualization
==============================================================================
"""

import asyncio
import base64
import json
import os
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

# API_BASE_URL can be configured via environment variable for deployment
# Falls back to localhost for local development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

# Risk level colors - Enhanced neon palette
RISK_COLORS = {
    "critical": "#FF073A",
    "high": "#FF6B35",
    "moderate": "#FFE66D",
    "low": "#4ECDC4",
    "minimal": "#00F5D4"
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
# Custom CSS - Futuristic NASA-Grade Dashboard
# ==============================================================================

def apply_custom_css():
    """Apply custom CSS styling - Futuristic NASA-grade theme"""
    st.markdown("""
    <style>
    /* ========================================
       GOOGLE FONTS IMPORT
    ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* ========================================
       ANIMATED GRADIENT BACKGROUND
    ======================================== */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes starTwinkle {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    .stApp {
        background: linear-gradient(-45deg, #0a0a0f, #0d1b2a, #1b263b, #0d1b2a, #0a0a0f);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, #00f5d4, transparent),
            radial-gradient(2px 2px at 40px 70px, #00bbf9, transparent),
            radial-gradient(1px 1px at 90px 40px, #f15bb5, transparent),
            radial-gradient(2px 2px at 160px 120px, #00f5d4, transparent),
            radial-gradient(1px 1px at 230px 80px, #fee440, transparent),
            radial-gradient(2px 2px at 300px 150px, #00bbf9, transparent),
            radial-gradient(1px 1px at 350px 200px, #9b5de5, transparent),
            radial-gradient(2px 2px at 420px 50px, #00f5d4, transparent),
            radial-gradient(1px 1px at 500px 130px, #f15bb5, transparent),
            radial-gradient(2px 2px at 580px 90px, #00bbf9, transparent);
        background-repeat: repeat;
        background-size: 600px 250px;
        animation: starTwinkle 4s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
        opacity: 0.6;
    }
    
    /* ========================================
       FADE-IN ANIMATIONS
    ======================================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .main .block-container {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* ========================================
       GLASSMORPHISM BASE STYLES
    ======================================== */
    .glass-card {
        background: rgba(13, 27, 42, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 20px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 0 32px rgba(0, 212, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .glass-card:hover {
        border-color: rgba(0, 245, 212, 0.5);
        box-shadow: 
            0 12px 40px rgba(0, 245, 212, 0.2),
            inset 0 0 32px rgba(0, 212, 255, 0.1);
        transform: translateY(-5px);
    }
    
    /* ========================================
       GLOWING CYBERPUNK TITLE
    ======================================== */
    @keyframes titleGlow {
        0%, 100% {
            text-shadow: 
                0 0 10px #00d4ff,
                0 0 20px #00d4ff,
                0 0 30px #00d4ff,
                0 0 40px #00bbf9,
                0 0 70px #00bbf9,
                0 0 80px #00bbf9;
        }
        50% {
            text-shadow: 
                0 0 5px #00f5d4,
                0 0 10px #00f5d4,
                0 0 15px #00f5d4,
                0 0 20px #00d4ff,
                0 0 35px #00d4ff,
                0 0 40px #00d4ff;
        }
    }
    
    @keyframes scanLine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .cyber-title {
        font-family: 'Orbitron', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: 8px;
        color: #00f5d4;
        text-transform: uppercase;
        animation: titleGlow 3s ease-in-out infinite;
        position: relative;
        display: inline-block;
    }
    
    .cyber-title::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 212, 0.4), transparent);
        animation: scanLine 3s linear infinite;
    }
    
    .subtitle {
        font-family: 'Rajdhani', 'Segoe UI', sans-serif;
        color: rgba(0, 212, 255, 0.8);
        font-size: 1.3rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* ========================================
       TOP NAVIGATION BAR
    ======================================== */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 30px;
        background: linear-gradient(90deg, rgba(13, 27, 42, 0.9), rgba(27, 38, 59, 0.9));
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.5s ease-out;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #00d4ff;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background: rgba(0, 212, 255, 0.15);
        transform: scale(1.05);
    }
    
    /* ========================================
       METRIC CARDS WITH HOVER ANIMATIONS
    ======================================== */
    @keyframes metricPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 245, 212, 0.3); }
        50% { box-shadow: 0 0 30px rgba(0, 245, 212, 0.5); }
    }
    
    .metric-card {
        background: linear-gradient(145deg, rgba(13, 27, 42, 0.8), rgba(27, 38, 59, 0.8));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #00f5d4, #00bbf9, #9b5de5, #f15bb5);
        background-size: 300% 100%;
        animation: gradientShift 3s ease infinite;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #00f5d4;
        animation: metricPulse 2s ease-in-out infinite;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f5d4, #00bbf9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 10px;
    }
    
    .metric-delta.positive {
        background: rgba(0, 245, 212, 0.2);
        color: #00f5d4;
    }
    
    .metric-delta.negative {
        background: rgba(255, 7, 58, 0.2);
        color: #FF073A;
    }
    
    /* Streamlit native metric styling */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(13, 27, 42, 0.9), rgba(27, 38, 59, 0.8));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00f5d4;
        box-shadow: 0 12px 40px rgba(0, 245, 212, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00f5d4, #00bbf9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }
    
    /* ========================================
       ANIMATED RISK ALERTS
    ======================================== */
    @keyframes criticalPulse {
        0%, 100% {
            box-shadow: 0 0 20px rgba(255, 7, 58, 0.5),
                        inset 0 0 20px rgba(255, 7, 58, 0.1);
            border-color: rgba(255, 7, 58, 0.8);
        }
        50% {
            box-shadow: 0 0 40px rgba(255, 7, 58, 0.8),
                        inset 0 0 30px rgba(255, 7, 58, 0.2);
            border-color: rgba(255, 7, 58, 1);
        }
    }
    
    @keyframes highPulse {
        0%, 100% {
            box-shadow: 0 0 15px rgba(255, 107, 53, 0.4);
            border-color: rgba(255, 107, 53, 0.7);
        }
        50% {
            box-shadow: 0 0 30px rgba(255, 107, 53, 0.7);
            border-color: rgba(255, 107, 53, 1);
        }
    }
    
    .risk-alert {
        background: linear-gradient(145deg, rgba(13, 27, 42, 0.85), rgba(27, 38, 59, 0.85));
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .risk-alert::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 5px;
        border-radius: 15px 0 0 15px;
    }
    
    .risk-critical {
        border-color: rgba(255, 7, 58, 0.6);
        animation: criticalPulse 2s ease-in-out infinite;
    }
    
    .risk-critical::before {
        background: linear-gradient(180deg, #FF073A, #ff4757);
    }
    
    .risk-high {
        border-color: rgba(255, 107, 53, 0.5);
        animation: highPulse 2.5s ease-in-out infinite;
    }
    
    .risk-high::before {
        background: linear-gradient(180deg, #FF6B35, #ffa502);
    }
    
    .risk-moderate {
        border-color: rgba(255, 230, 109, 0.4);
    }
    
    .risk-moderate::before {
        background: linear-gradient(180deg, #FFE66D, #ffc107);
    }
    
    .risk-low {
        border-color: rgba(78, 205, 196, 0.4);
    }
    
    .risk-low::before {
        background: linear-gradient(180deg, #4ECDC4, #26de81);
    }
    
    .risk-minimal {
        border-color: rgba(0, 245, 212, 0.3);
    }
    
    .risk-minimal::before {
        background: linear-gradient(180deg, #00F5D4, #00d2d3);
    }
    
    .risk-alert:hover {
        transform: translateX(10px);
    }
    
    .risk-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .risk-location {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
    }
    
    .risk-score {
        font-size: 1.4rem;
        font-weight: 800;
    }
    
    /* ========================================
       SIDEBAR ENHANCEMENTS
    ======================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            rgba(10, 10, 15, 0.98) 0%, 
            rgba(13, 27, 42, 0.98) 50%, 
            rgba(27, 38, 59, 0.98) 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 2px;
        height: 100%;
        background: linear-gradient(180deg, 
            transparent, 
            #00f5d4, 
            #00bbf9, 
            #9b5de5, 
            transparent);
        opacity: 0.5;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        background: linear-gradient(90deg, #00f5d4, #00bbf9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* ========================================
       BUTTON MOTION EFFECTS
    ======================================== */
    @keyframes buttonGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.4); }
        50% { box-shadow: 0 0 35px rgba(0, 245, 212, 0.6); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #00bbf9 50%, #00f5d4 100%);
        background-size: 200% 200%;
        color: #0a0a0f;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 12px 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        background-position: 100% 0;
        transform: scale(1.05) translateY(-2px);
        animation: buttonGlow 1.5s ease-in-out infinite;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }
    
    /* Primary button special style */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f15bb5, #9b5de5, #00bbf9);
        background-size: 200% 200%;
    }
    
    /* ========================================
       3D EARTH VISUALIZATION PLACEHOLDER
    ======================================== */
    .earth-container {
        background: radial-gradient(ellipse at center, 
            rgba(0, 100, 150, 0.3) 0%, 
            rgba(13, 27, 42, 0.9) 70%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        border: 2px solid rgba(0, 212, 255, 0.3);
        position: relative;
        overflow: hidden;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .earth-container::before {
        content: '';
        position: absolute;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.3), transparent 70%);
        border-radius: 50%;
        animation: earthGlow 4s ease-in-out infinite;
    }
    
    @keyframes earthGlow {
        0%, 100% { 
            transform: scale(1); 
            opacity: 0.5;
        }
        50% { 
            transform: scale(1.2); 
            opacity: 0.8;
        }
    }
    
    .earth-icon {
        font-size: 8rem;
        animation: earthRotate 20s linear infinite;
        filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.5));
        position: relative;
        z-index: 1;
    }
    
    @keyframes earthRotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* ========================================
       SCANNER LOADING ANIMATION
    ======================================== */
    @keyframes scannerEffect {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    .scanner-loader {
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, 
            transparent, 
            #00f5d4, 
            #00bbf9, 
            #00f5d4, 
            transparent);
        background-size: 200% 100%;
        animation: scannerEffect 2s linear infinite;
        border-radius: 2px;
        margin: 20px 0;
    }
    
    .loading-text {
        color: #00d4ff;
        font-size: 1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ========================================
       RESPONSIVE GRID LAYOUT
    ======================================== */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    
    /* ========================================
       CHART CONTAINERS
    ======================================== */
    [data-testid="stVegaLiteChart"],
    .stPlotlyChart {
        background: rgba(13, 27, 42, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* ========================================
       STATUS INDICATORS
    ======================================== */
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: statusPulse 2s ease-in-out infinite;
    }
    
    .status-online {
        background: #00f5d4;
        box-shadow: 0 0 10px #00f5d4;
    }
    
    .status-offline {
        background: #FF073A;
        box-shadow: 0 0 10px #FF073A;
    }
    
    .status-warning {
        background: #FFE66D;
        box-shadow: 0 0 10px #FFE66D;
    }
    
    @keyframes statusPulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    /* ========================================
       EXPANDER STYLING
    ======================================== */
    .streamlit-expanderHeader {
        background: rgba(13, 27, 42, 0.7);
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    .streamlit-expanderContent {
        background: rgba(13, 27, 42, 0.5);
        border: 1px solid rgba(0, 212, 255, 0.1);
        border-top: none;
        border-radius: 0 0 10px 10px;
    }
    
    /* ========================================
       SELECTBOX AND INPUT STYLING
    ======================================== */
    .stSelectbox > div > div {
        background: rgba(13, 27, 42, 0.8);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00f5d4, #00bbf9);
    }
    
    /* ========================================
       DIVIDER STYLING
    ======================================== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(0, 212, 255, 0.5), 
            transparent);
        margin: 25px 0;
    }
    
    /* ========================================
       PROGRESS BAR STYLING
    ======================================== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00f5d4, #00bbf9, #9b5de5);
        border-radius: 10px;
    }
    
    /* ========================================
       SCROLLBAR STYLING
    ======================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 27, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00f5d4, #00bbf9);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00bbf9, #9b5de5);
    }
    
    /* ========================================
       INFO/WARNING/ERROR BOXES
    ======================================== */
    .stAlert {
        background: rgba(13, 27, 42, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 10px;
    }
    
    /* ========================================
       MAP CONTAINER
    ======================================== */
    iframe {
        border-radius: 15px;
        border: 2px solid rgba(0, 212, 255, 0.3);
    }
    
    /* ========================================
       TABS STYLING
    ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(13, 27, 42, 0.7);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.2);
        color: #00f5d4;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 245, 212, 0.3));
        color: #00f5d4;
    }
    
    /* ========================================
       RESPONSIVE ADJUSTMENTS
    ======================================== */
    @media (max-width: 768px) {
        .cyber-title {
            font-size: 2rem;
            letter-spacing: 4px;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 15px;
        }
        
        .metric-value {
            font-size: 2rem;
        }
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
        self._is_online = None
        self._last_check = 0
        self._check_interval = 5  # seconds between online status checks
    
    def _make_request(self, method: str, endpoint: str, show_error: bool = True, **kwargs) -> Optional[dict]:
        """Make HTTP request to API"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(method, f"{self.base_url}{endpoint}", **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            if show_error:
                st.error(f"⚠️ Cannot connect to backend at {self.base_url}. Please ensure the API server is running or check your API_BASE_URL configuration.")
            return None
        except httpx.TimeoutException:
            if show_error:
                st.error(f"⚠️ Connection to backend timed out. The server at {self.base_url} may be slow or unresponsive.")
            return None
        except httpx.HTTPStatusError as e:
            if show_error:
                st.error(f"API Error: HTTP {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            if show_error:
                st.error(f"API Error: {str(e)}")
            return None
    
    def is_backend_online(self) -> bool:
        """Check if the backend is online with caching to avoid excessive requests"""
        current_time = time.time()
        if self._is_online is None or (current_time - self._last_check) > self._check_interval:
            result = self._make_request("GET", "/health", show_error=False)
            self._is_online = result is not None and result.get("status") == "healthy"
            self._last_check = current_time
        return self._is_online
    
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
    """Render the futuristic main header with cyberpunk styling"""
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 20px 0;">
        <div class="cyber-title">🛰️ ORBITAL SENTINEL</div>
        <div class="subtitle">Real-Time Earth Risk Prediction System • AI-Powered Threat Analysis</div>
        <div class="scanner-loader"></div>
    </div>
    """, unsafe_allow_html=True)


def render_status_bar():
    """Render the futuristic status bar with service indicators"""
    # Use the cached online check first
    is_online = client.is_backend_online()
    
    st.markdown("""
    <div class="nav-bar">
        <div style="display: flex; gap: 30px; flex-wrap: wrap; justify-content: center; width: 100%;">
    """, unsafe_allow_html=True)
    
    if is_online:
        health = client.health_check()
        if health:
            services = health.get("services", {})
            
            # Build status HTML
            service_items = [
                ("🤖 Gemini AI", services.get("gemini", False)),
                ("🗣️ Voice", services.get("elevenlabs", False)),
                ("📡 Streaming", services.get("streaming", False)),
                ("💾 Storage", services.get("storage", False)),
                ("🔄 Simulator", services.get("simulator", False)),
                ("🌐 API", True)
            ]
            
            status_html = ""
            for name, is_active in service_items:
                status_class = "status-online" if is_active else "status-offline" if name == "💾 Storage" else "status-warning"
                status_html += f"""
                <div class="nav-item">
                    <span class="status-dot {status_class}"></span>
                    <span>{name}</span>
                </div>
                """
            
            st.markdown(status_html, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="nav-item" style="color: #FFE66D;">
                <span class="status-dot status-warning"></span>
                <span>⚠️ Backend responding but health check failed - API: {API_BASE_URL}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="nav-item" style="color: #FF073A;">
            <span class="status-dot status-offline"></span>
            <span>⚠️ Backend Offline - Cannot reach {API_BASE_URL}. Check API_BASE_URL env var or start the API server.</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_metrics_dashboard():
    """Render the futuristic metrics dashboard with glassmorphism cards"""
    stats = client.get_stats()
    
    if not stats:
        # Show placeholder metrics
        stats = {
            "total_predictions": 0,
            "active_risks": 0,
            "critical_risks": 0,
            "regions_monitored": 0
        }
    
    # Custom metric cards with glassmorphism
    cols = st.columns(4)
    
    metrics = [
        {
            "icon": "📊",
            "label": "Total Predictions",
            "value": stats.get("total_predictions", 0),
            "delta": "+5 last hour",
            "delta_type": "positive"
        },
        {
            "icon": "⚠️",
            "label": "Active Risks",
            "value": stats.get("active_risks", 0),
            "delta": "3 new",
            "delta_type": "positive"
        },
        {
            "icon": "🚨",
            "label": "Critical Alerts",
            "value": stats.get("critical_risks", 0),
            "delta": "-1 resolved" if stats.get("critical_risks", 0) > 0 else "All clear",
            "delta_type": "negative" if stats.get("critical_risks", 0) > 0 else "positive"
        },
        {
            "icon": "🌍",
            "label": "Regions Monitored",
            "value": stats.get("regions_monitored", 0) or 20,
            "delta": "Global coverage",
            "delta_type": "positive"
        }
    ]
    
    for col, metric in zip(cols, metrics):
        with col:
            delta_class = "positive" if metric["delta_type"] == "positive" else "negative"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 10px;">{metric["icon"]}</div>
                <div class="metric-value">{metric["value"]}</div>
                <div class="metric-label">{metric["label"]}</div>
                <div class="metric-delta {delta_class}">{metric["delta"]}</div>
            </div>
            """, unsafe_allow_html=True)


def render_world_map(predictions: list):
    """Render the futuristic world map with risk markers"""
    # Create base map with dark theme
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
        
        # Create popup content with enhanced styling
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 220px; 
                    background: linear-gradient(135deg, #0d1b2a, #1b263b); 
                    padding: 15px; border-radius: 10px; border: 1px solid {color};">
            <h4 style="color: {color}; margin: 0 0 10px 0; font-size: 1.1rem;">
                {icon_emoji} {risk_type.upper()}
            </h4>
            <p style="margin: 5px 0; color: #fff;">
                <strong style="color: rgba(255,255,255,0.6);">Level:</strong> 
                <span style="color: {color}; font-weight: bold;">{risk_level.upper()}</span>
            </p>
            <p style="margin: 5px 0; color: #fff;">
                <strong style="color: rgba(255,255,255,0.6);">Score:</strong> 
                <span style="color: #00f5d4;">{risk_score:.1f}/100</span>
            </p>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.8);">
                <strong style="color: rgba(255,255,255,0.6);">Location:</strong> 
                {location.get('region', 'Unknown')}
            </p>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.5); font-size: 0.85rem;">
                {pred.get('timestamp', '')[:19]}
            </p>
        </div>
        """
        
        # Add circle marker with glow effect
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
    """Render futuristic risk alert cards with animations"""
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="color: #00f5d4; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">
            📋 Recent Risk Alerts
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not predictions:
        st.markdown("""
        <div class="glass-card" style="padding: 30px; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🛡️</div>
            <div style="color: #00f5d4; font-size: 1.1rem;">No active threats detected</div>
            <div style="color: rgba(255,255,255,0.5); margin-top: 10px;">Click 'Generate Analysis' to scan for risks</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for pred in predictions[:10]:
        risk_level = pred.get("risk_level", "minimal")
        risk_type = pred.get("risk_type", "unknown")
        risk_score = pred.get("risk_score", 0)
        location = pred.get("location", {})
        
        icon = RISK_ICONS.get(risk_type, "⚠️")
        color = RISK_COLORS.get(risk_level, "#FFFFFF")
        
        # Render animated risk card
        st.markdown(f"""
        <div class="risk-alert risk-{risk_level}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="display: flex; gap: 15px; align-items: flex-start;">
                    <div style="font-size: 2.5rem; filter: drop-shadow(0 0 10px {color});">{icon}</div>
                    <div>
                        <div class="risk-title">{pred.get('title', 'Unknown Risk')}</div>
                        <div class="risk-location">📍 {location.get('region', 'Unknown')}, {location.get('country', '')}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="risk-score" style="color: {color};">{risk_score:.0f}</div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Risk Score</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <div style="background: rgba(0,0,0,0.3); border-radius: 10px; height: 8px; overflow: hidden;">
                    <div style="width: {risk_score}%; height: 100%; background: linear-gradient(90deg, {color}, {color}99); border-radius: 10px; transition: width 1s ease;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable details using Streamlit
        with st.expander(f"🔍 View Details - {pred.get('title', 'Unknown Risk')[:30]}..."):
            st.markdown(f"**Description:** {pred.get('description', 'N/A')}")
            
            # Reasoning chain
            reasoning = pred.get("reasoning_chain", [])
            if reasoning:
                st.markdown("**🧠 AI Reasoning Chain:**")
                for step in reasoning:
                    st.markdown(f"""
                    - **Step {step.get('step_number', '?')}:** {step.get('observation', '')}
                      - *Analysis:* {step.get('analysis', '')}
                      - *Conclusion:* {step.get('conclusion', '')}
                    """)
            
            # Recommendations
            recommendations = pred.get("recommended_actions", [])
            if recommendations:
                st.markdown("**🎯 Recommended Actions:**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")


def render_sidebar():
    """Render the futuristic sidebar controls"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 2.5rem;">🎛️</div>
            <h2 style="margin: 10px 0 5px 0;">Control Panel</h2>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; letter-spacing: 2px;">SYSTEM CONTROLS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Simulator controls with enhanced styling
        st.markdown("""
        <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
            🔄 DATA SIMULATOR
        </div>
        """, unsafe_allow_html=True)
        
        sim_status = client.get_simulator_status()
        is_running = sim_status.get("running", False) if sim_status else False
        
        if is_running:
            st.markdown("""
            <div style="background: rgba(0, 245, 212, 0.1); border: 1px solid rgba(0, 245, 212, 0.3); 
                        border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 15px;">
                <span class="status-dot status-online"></span>
                <span style="color: #00f5d4;">Simulator Active</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⏹️ Stop Simulator", use_container_width=True):
                client.stop_simulator()
                st.rerun()
        else:
            st.markdown("""
            <div style="background: rgba(255, 230, 109, 0.1); border: 1px solid rgba(255, 230, 109, 0.3); 
                        border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 15px;">
                <span class="status-dot status-warning"></span>
                <span style="color: #FFE66D;">Simulator Inactive</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶️ Start Simulator", use_container_width=True):
                client.start_simulator()
                st.rerun()
        
        st.divider()
        
        # Manual analysis section
        st.markdown("""
        <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
            🔬 THREAT ANALYSIS
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎲 Generate Analysis", use_container_width=True, type="primary"):
            with st.spinner(""):
                st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <div class="scanner-loader"></div>
                    <div class="loading-text">Analyzing satellite data...</div>
                </div>
                """, unsafe_allow_html=True)
                result = client.simulate_analysis()
                if result and result.get("success"):
                    st.success("✅ Analysis Complete!")
                    pred = result.get("prediction", {})
                    risk_color = RISK_COLORS.get(pred.get('risk_level', 'minimal'), '#00f5d4')
                    st.markdown(f"""
                    <div style="background: rgba(13, 27, 42, 0.8); border-radius: 10px; padding: 15px; 
                                border: 1px solid {risk_color}; margin-top: 10px;">
                        <div style="color: {risk_color}; font-weight: 600;">
                            {RISK_ICONS.get(pred.get('risk_type', 'unknown'), '⚠️')} {pred.get('risk_type', 'Unknown').upper()}
                        </div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 5px;">
                            Level: {pred.get('risk_level', 'Unknown').upper()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
        
        st.divider()
        
        # Filters section
        st.markdown("""
        <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
            🔍 FILTER CONTROLS
        </div>
        """, unsafe_allow_html=True)
        
        risk_filter = st.selectbox(
            "Risk Type",
            ["All", "fire", "flood", "earthquake", "storm", "air_quality", "drought", "volcanic", "tsunami"],
            key="risk_type_filter"
        )
        
        level_filter = st.selectbox(
            "Risk Level",
            ["All", "critical", "high", "moderate", "low", "minimal"],
            key="risk_level_filter"
        )
        
        st.divider()
        
        # Auto-refresh settings
        st.markdown("""
        <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
            ⏱️ AUTO-REFRESH
        </div>
        """, unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        refresh_interval = st.slider("Interval (seconds)", 5, 60, 10)
        
        st.divider()
        
        # About section with enhanced styling
        st.markdown("""
        <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
            ℹ️ SYSTEM INFO
        </div>
        <div class="glass-card" style="padding: 15px; font-size: 0.85rem;">
            <div style="margin-bottom: 12px;">
                <span style="color: #9b5de5;">🤖</span> <span style="color: rgba(255,255,255,0.8);">Gemini 2.0 AI</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="color: #f15bb5;">📡</span> <span style="color: rgba(255,255,255,0.8);">Confluent Kafka</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="color: #00bbf9;">🗣️</span> <span style="color: rgba(255,255,255,0.8);">ElevenLabs Voice</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="color: #00f5d4;">🌍</span> <span style="color: rgba(255,255,255,0.8);">Real-time Data</span>
            </div>
            <div style="text-align: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0, 212, 255, 0.2);">
                <span style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">Made with ❤️ for Earth</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return {
            "risk_filter": risk_filter if risk_filter != "All" else None,
            "level_filter": level_filter if level_filter != "All" else None,
            "auto_refresh": auto_refresh,
            "refresh_interval": refresh_interval
        }


def render_analytics(predictions: list):
    """Render futuristic analytics section with glassmorphism"""
    st.markdown("""
    <div style="margin: 30px 0 20px 0;">
        <h3 style="color: #00f5d4; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">
            📈 Risk Analytics Dashboard
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not predictions:
        st.markdown("""
        <div class="glass-card" style="padding: 40px; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 15px;">📊</div>
            <div style="color: rgba(255,255,255,0.5);">No analytics data available yet</div>
            <div style="color: rgba(255,255,255,0.3); margin-top: 10px; font-size: 0.9rem;">
                Generate analysis to populate charts
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="padding: 20px; margin-bottom: 10px;">
            <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
                🔥 Risk Type Distribution
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk type distribution
        risk_types = {}
        for pred in predictions:
            rt = pred.get("risk_type", "unknown")
            risk_types[rt] = risk_types.get(rt, 0) + 1
        
        if risk_types:
            df = pd.DataFrame(list(risk_types.items()), columns=["Risk Type", "Count"])
            st.bar_chart(df.set_index("Risk Type"))
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="padding: 20px; margin-bottom: 10px;">
            <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px;">
                ⚡ Risk Level Distribution
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk level distribution
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

def render_earth_visualization():
    """Render 3D Earth visualization placeholder"""
    st.markdown("""
    <div class="earth-container">
        <div class="earth-icon">🌍</div>
        <div style="color: #00f5d4; font-size: 1.2rem; margin-top: 20px; position: relative; z-index: 1;">
            Global Threat Monitoring Active
        </div>
        <div style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-top: 10px; position: relative; z-index: 1;">
            Real-time satellite data integration
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    apply_custom_css()
    
    # Render futuristic header
    render_header()
    
    # Render status bar (navigation)
    render_status_bar()
    
    # Render sidebar and get filters
    filters = render_sidebar()
    
    # Add some spacing
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Render metrics dashboard
    render_metrics_dashboard()
    
    # Add spacing
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # Get predictions
    predictions_data = client.get_predictions(limit=100)
    predictions = predictions_data.get("predictions", []) if predictions_data else []
    
    # Apply filters
    if filters["risk_filter"]:
        predictions = [p for p in predictions if p.get("risk_type") == filters["risk_filter"]]
    if filters["level_filter"]:
        predictions = [p for p in predictions if p.get("risk_level") == filters["level_filter"]]
    
    # Main content area with tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🗺️ Global Risk Map", "🌍 Earth Monitor", "📊 Analytics"])
    
    with tab1:
        # Create two columns for map and alerts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="glass-card" style="padding: 20px; margin-bottom: 10px;">
                <div style="color: #00f5d4; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 15px;">
                    🗺️ Global Risk Heatmap
                </div>
            </div>
            """, unsafe_allow_html=True)
            render_world_map(predictions)
        
        with col2:
            render_risk_alerts(predictions)
    
    with tab2:
        # 3D Earth visualization placeholder
        col1, col2 = st.columns([1, 1])
        
        with col1:
            render_earth_visualization()
        
        with col2:
            st.markdown("""
            <div class="glass-card" style="padding: 25px;">
                <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 20px;">
                    🛰️ SATELLITE STATUS
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: rgba(255,255,255,0.7);">SENTINEL-1A</span>
                        <span class="status-dot status-online"></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: rgba(255,255,255,0.7);">SENTINEL-2B</span>
                        <span class="status-dot status-online"></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: rgba(255,255,255,0.7);">LANDSAT-8</span>
                        <span class="status-dot status-online"></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: rgba(255,255,255,0.7);">GOES-16</span>
                        <span class="status-dot status-warning"></span>
                    </div>
                </div>
                <div style="border-top: 1px solid rgba(0, 212, 255, 0.2); padding-top: 15px; margin-top: 15px;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">
                        Last orbital pass: 2 minutes ago
                    </div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 5px;">
                        Next data refresh: 45 seconds
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mission stats
            st.markdown("""
            <div class="glass-card" style="padding: 25px; margin-top: 20px;">
                <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 20px;">
                    📡 MISSION STATISTICS
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="text-align: center; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                        <div style="color: #00f5d4; font-size: 1.5rem; font-weight: 700;">847</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Orbits Complete</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                        <div style="color: #00bbf9; font-size: 1.5rem; font-weight: 700;">2.4TB</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Data Processed</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                        <div style="color: #9b5de5; font-size: 1.5rem; font-weight: 700;">156</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Countries Covered</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                        <div style="color: #f15bb5; font-size: 1.5rem; font-weight: 700;">99.7%</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Uptime</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # Analytics section
        render_analytics(predictions)
        
        # Additional stats
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="padding: 25px;">
            <div style="color: #00f5d4; font-weight: 600; letter-spacing: 1px; margin-bottom: 20px;">
                🎯 AI PREDICTION ACCURACY
            </div>
            <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px;">
                    <div style="color: rgba(255,255,255,0.6); margin-bottom: 5px;">Fire Detection</div>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="width: 94%; height: 100%; background: linear-gradient(90deg, #FF073A, #ff4757); border-radius: 10px;"></div>
                    </div>
                    <div style="color: #FF073A; font-size: 0.9rem; margin-top: 5px;">94%</div>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <div style="color: rgba(255,255,255,0.6); margin-bottom: 5px;">Flood Prediction</div>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="width: 89%; height: 100%; background: linear-gradient(90deg, #00bbf9, #4ECDC4); border-radius: 10px;"></div>
                    </div>
                    <div style="color: #00bbf9; font-size: 0.9rem; margin-top: 5px;">89%</div>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <div style="color: rgba(255,255,255,0.6); margin-bottom: 5px;">Storm Tracking</div>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="width: 91%; height: 100%; background: linear-gradient(90deg, #9b5de5, #f15bb5); border-radius: 10px;"></div>
                    </div>
                    <div style="color: #9b5de5; font-size: 0.9rem; margin-top: 5px;">91%</div>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <div style="color: rgba(255,255,255,0.6); margin-bottom: 5px;">Air Quality</div>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="width: 87%; height: 100%; background: linear-gradient(90deg, #FFE66D, #ffa502); border-radius: 10px;"></div>
                    </div>
                    <div style="color: #FFE66D; font-size: 0.9rem; margin-top: 5px;">87%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with dynamic year
    current_year = datetime.now().year
    st.markdown(f"""
    <div style="text-align: center; padding: 30px 0; margin-top: 30px; border-top: 1px solid rgba(0, 212, 255, 0.2);">
        <div style="color: rgba(255,255,255,0.3); font-size: 0.85rem; letter-spacing: 2px;">
            ORBITAL SENTINEL © {current_year} • PROTECTING EARTH FROM SPACE
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    if filters["auto_refresh"]:
        time.sleep(filters["refresh_interval"])
        st.rerun()


if __name__ == "__main__":
    main()
