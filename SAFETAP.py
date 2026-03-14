import streamlit as st
import time
import datetime
import pandas as pd
import folium
from streamlit_folium import folium_static, st_folium
import base64
from PIL import Image
import io
import json
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    # Create dummy objects to prevent errors
    class DummyPlotly:
        def __getattr__(self, name):
            def dummy(*args, **kwargs):
                st.warning("Plotly charts not available - install plotly for full functionality")
                return None
            return dummy
    px = DummyPlotly()
    go = DummyPlotly()

# Helper function for safe plotly chart rendering
def safe_plotly_chart(fig, **kwargs):
    if PLOTLY_AVAILABLE and fig is not None:
        st.plotly_chart(fig, **kwargs)
    else:
        st.info("📊 Chart visualization not available - install plotly for full functionality")

# ---- Page Configuration ----
st.set_page_config(
    page_title="SafeTap - One-Tap Emergency Help", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Enhanced Custom CSS with Theme-Aware Text Colors ----
st.markdown("""
<style>
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    /* Light mode text colors */
    @media (prefers-color-scheme: light) {
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) {
            color: #000000 !important;
        }
        
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stCaption,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) small,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .small {
            color: #333333 !important;
        }
        
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stMetricValue,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) [data-testid="stMetricValue"],
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stat-value {
            color: #1a5f9e !important;
        }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox select,
        .stNumberInput input, .stDateInput input, .stTimeInput input {
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 1px solid #dddddd !important;
        }
        
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: #666666 !important;
        }
        
        .stProgress > div > div > div {
            background-color: #1a5f9e !important;
        }
    }
    
    /* Dark mode text colors */
    @media (prefers-color-scheme: dark) {
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) {
            color: #ffffff !important;
        }
        
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stCaption,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) small,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .small {
            color: #cccccc !important;
        }
        
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stMetricValue,
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) [data-testid="stMetricValue"],
        .main :not(.safe-header):not(.safe-header *):not([data-testid="stSidebar"]):not([data-testid="stSidebar"] *) .stat-value {
            color: #ffeb3b !important;
        }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox select,
        .stNumberInput input, .stDateInput input, .stTimeInput input {
            color: #ffffff !important;
            background-color: #333333 !important;
            border: 1px solid #555555 !important;
        }
        
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: #999999 !important;
        }
        
        .stProgress > div > div > div {
            background-color: #ffeb3b !important;
        }
    }
    
    /* Smooth transitions for all elements */
    * {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Enhanced particles */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        overflow: hidden;
    }
    
    .particle {
        position: absolute;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        animation: float 20s infinite ease-in-out;
        box-shadow: 0 0 20px rgba(255,255,255,0.3);
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg) scale(0.5); opacity: 0; }
        10% { opacity: 0.6; transform: scale(1); }
        90% { opacity: 0.6; }
        100% { transform: translateY(-100px) rotate(360deg) scale(0.5); opacity: 0; }
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    .sidebar .sidebar-content {
        background: transparent !important;
    }
    
    [data-testid="stSidebarNav"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
    }
    
    .stSidebar button {
        background: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    .stSidebar button:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: #ffeb3b !important;
    }
    
    .sidebar-section {
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 15px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid transparent;
        font-weight: 600;
        color: #ffffff !important;
        text-decoration: none !important;
        display: block;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        font-size: 1rem;
        border: none;
    }
    
    .sidebar-section:hover {
        background: rgba(255,255,255,0.2);
        border-left: 4px solid #ff6b6b;
        transform: translateX(10px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        color: #ffffff !important;
    }
    
    .sidebar-section.active {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(255, 193, 7, 0.3));
        border-left: 4px solid #ff6b6b;
        color: #ffffff !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
    
    .sidebar-header {
        text-align: center;
        padding: 25px 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 25px;
    }
    
    .sidebar-header h2 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sidebar-header p {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .sidebar-user-info {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-user-info h4 {
        color: #ffffff !important;
    }
    
    .user-info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 8px 0;
        padding: 5px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .user-info-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.8) !important;
    }
    
    .user-info-value {
        font-size: 0.9rem;
        font-weight: bold;
        color: #ffeb3b !important;
    }
    
    /* Safe Header */
    .safe-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        backdrop-filter: blur(15px);
        color: #ffffff !important;
        border-radius: 0 0 25px 25px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        padding: 3rem 0 2rem 0;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .safe-header h1, .safe-header p {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .safe-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: rotate(45deg) translateX(-100%); }
        100% { transform: rotate(45deg) translateX(100%); }
    }
    
    /* Circular Emergency Alert Button */
    .emergency-alert-button {
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b6b, #ff4757);
        color: #ffffff !important;
        border: none;
        font-size: 1.3rem;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: pulse-glow 2s infinite;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        padding: 20px;
        text-align: center;
    }
    
    .emergency-alert-button:hover {
        transform: scale(1.1);
        box-shadow: 0 20px 50px rgba(255, 107, 107, 0.6);
        animation: none;
    }
    
    .emergency-alert-button:active {
        transform: scale(0.95);
    }
    
    .alert-icon {
        font-size: 5rem;
        margin-bottom: 0.5rem;
        color: #ffffff !important;
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 20px 5px rgba(255, 107, 107, 0.6); }
        50% { box-shadow: 0 0 30px 15px rgba(255, 107, 107, 0.8); }
        100% { box-shadow: 0 0 20px 5px rgba(255, 107, 107, 0.6); }
    }
    
    /* Hide the actual Streamlit button */
    .stButton button[key="panic_btn"] {
        display: none !important;
    }
    
    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-top: 1rem;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .stat-value {
        font-size: 1.6rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    /* Dashboard Container */
    .dashboard-container {
        margin: 2rem 0;
    }
    
    .dashboard-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Location info boxes */
    .location-info-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    .location-coordinates {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        font-family: monospace;
    }
    
    /* Map container */
    .map-container {
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .emergency-alert-button {
            width: 200px;
            height: 200px;
        }
        
        .alert-icon {
            font-size: 4rem;
        }
    }
    
    @media (max-width: 480px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .emergency-alert-button {
            width: 180px;
            height: 180px;
        }
        
        .alert-icon {
            font-size: 3.5rem;
        }
    }
</style>

<div class="particles" id="particles"></div>
<script>
    // Create enhanced animated background particles
    function createParticles() {
        const container = document.getElementById('particles');
        const particleCount = 25;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 8 + 3;
            const left = Math.random() * 100;
            const animationDuration = Math.random() * 25 + 15;
            const animationDelay = Math.random() * 8;
            const colors = ['rgba(255, 107, 107, 0.3)', 'rgba(255, 193, 7, 0.3)', 'rgba(79, 172, 254, 0.3)', 'rgba(118, 75, 162, 0.3)'];
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${left}vw`;
            particle.style.background = randomColor;
            particle.style.animationDuration = `${animationDuration}s`;
            particle.style.animationDelay = `${animationDelay}s`;
            
            container.appendChild(particle);
        }
    }
    
    createParticles();
    
    document.addEventListener('DOMContentLoaded', function() {
        const elements = document.querySelectorAll('.stat-card, .location-info-box');
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            setTimeout(() => {
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 100);
        });
    });
</script>
""", unsafe_allow_html=True)

# ---- Session State Initialization (No Demo Data) ----
if "registered_users" not in st.session_state:
    # Initialize with only admin user (no demo users)
    st.session_state.registered_users = {
        "admin": {
            "password": "admin123",
            "name": "System Administrator",
            "email": "admin@safetap.com",
            "phone": "+63 900 000 0000",
            "id": "ADMIN001",
            "authority": "Administrator",
            "role": "admin",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "profile_pic": None,
            "status": "active",
            "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_location": None,
            "location_history": []
        }
    }

if "view" not in st.session_state:
    st.session_state.view = "login"
if "user" not in st.session_state:
    st.session_state.user = None
if "panic_active" not in st.session_state:
    st.session_state.panic_active = False
if "panic_timer" not in st.session_state:
    st.session_state.panic_timer = None
if "location" not in st.session_state:
    st.session_state.location = None  # No default location
if "history" not in st.session_state:
    st.session_state.history = []
if "contacts" not in st.session_state:
    st.session_state.contacts = []  # Empty contacts - user must add
if "settings" not in st.session_state:
    st.session_state.settings = {
        "notifications": True,
        "location_tracking": True,
        "high_accuracy": True,
        "vibration": True,
        "sound_alerts": True,
        "voice_recording": True,
        "auto_send_alerts": True,
        "panic_duration": 3,
        "emergency_message": "EMERGENCY! I need immediate assistance. My current location has been shared with this alert."
    }
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False
if "map_click_location" not in st.session_state:
    st.session_state.map_click_location = None

# ---- Emergency Features ----
if "emergency_type" not in st.session_state:
    st.session_state.emergency_type = "general"
if "safety_timer" not in st.session_state:
    st.session_state.safety_timer = None
if "fake_call_time" not in st.session_state:
    st.session_state.fake_call_time = None
if "safety_network" not in st.session_state:
    st.session_state.safety_network = []
if "evidence_recordings" not in st.session_state:
    st.session_state.evidence_recordings = []
if "offline_mode" not in st.session_state:
    st.session_state.offline_mode = False

# ---- Admin Tracking ----
if "panic_events" not in st.session_state:
    st.session_state.panic_events = []
if "system_logs" not in st.session_state:
    st.session_state.system_logs = []
if "admin_settings" not in st.session_state:
    st.session_state.admin_settings = {
        "system_name": "SafeTap Emergency System",
        "emergency_response_time": "5 minutes",
        "auto_backup": True,
        "data_retention_days": 90,
        "max_users": 1000,
        "alert_cooldown": 300,
        "system_status": "operational",
        "location_update_interval": 30
    }

# ---- Emergency Protocols ----
EMERGENCY_PROTOCOLS = {
    "emergency": {
        "icon": "🚨",
        "color": "#ff6b6b",
        "message": "EMERGENCY! I need immediate assistance.",
        "actions": ["Assess situation", "Call emergency services", "Move to safe location"],
        "contacts": ["all"],
        "bg_color": "rgba(255, 107, 107, 0.3)"
    },
    "medical": {
        "icon": "🚑",
        "color": "#e74c3c",
        "message": "MEDICAL EMERGENCY! Need immediate medical assistance.",
        "actions": ["Check responsiveness", "Call emergency services", "Provide first aid if trained"],
        "contacts": ["emergency", "family"],
        "bg_color": "rgba(231, 76, 60, 0.3)"
    },
    "fire": {
        "icon": "🔥",
        "color": "#e67e22",
        "message": "FIRE EMERGENCY! Need immediate fire department assistance.",
        "actions": ["Evacuate area", "Call fire department", "Use fire extinguisher if safe"],
        "contacts": ["emergency", "family"],
        "bg_color": "rgba(230, 126, 34, 0.3)"
    },
    "personal_safety": {
        "icon": "🛡️",
        "color": "#9b59b6",
        "message": "PERSONAL SAFETY ALERT! I feel unsafe and need assistance.",
        "actions": ["Find safe location", "Contact emergency services", "Stay on phone"],
        "contacts": ["emergency", "family"],
        "bg_color": "rgba(155, 89, 182, 0.3)"
    },
    "general": {
        "icon": "⚠️",
        "color": "#ff6b6b",
        "message": "GENERAL EMERGENCY! I need immediate assistance.",
        "actions": ["Assess situation", "Call emergency services", "Move to safe location"],
        "contacts": ["all"],
        "bg_color": "rgba(255, 107, 107, 0.3)"
    }
}

# ---- Helper Functions ----
def add_history(event_type, title, details):
    """Add an event to history"""
    event = {
        "type": event_type,
        "title": title,
        "details": details,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.datetime.now().strftime("%B %d, %Y - %H:%M")
    }
    st.session_state.history.insert(0, event)

def log_panic_event(username, emergency_type, location):
    """Log panic button usage for admin tracking"""
    if username in st.session_state.registered_users:
        user_name = st.session_state.registered_users[username]["name"]
        event = {
            "username": username,
            "user_name": user_name,
            "emergency_type": emergency_type,
            "location": location,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.datetime.now().strftime("%B %d, %Y - %H:%M")
        }
        st.session_state.panic_events.insert(0, event)

def update_user_location(username, lat, lng, source="manual"):
    """Update user's current location and add to history"""
    if username in st.session_state.registered_users:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        location_entry = {
            "lat": lat,
            "lng": lng,
            "timestamp": timestamp,
            "source": source
        }
        
        if "location_history" not in st.session_state.registered_users[username]:
            st.session_state.registered_users[username]["location_history"] = []
        
        st.session_state.registered_users[username]["location_history"].insert(0, location_entry)
        
        st.session_state.registered_users[username]["current_location"] = {
            "lat": lat,
            "lng": lng,
            "timestamp": timestamp,
            "source": source
        }
        
        add_history("location", f"Location Updated", 
                   f"New location: {lat:.6f}, {lng:.6f} via {source}")
        
        return True
    return False

def get_user_location(username):
    """Get user's current location"""
    if username in st.session_state.registered_users:
        return st.session_state.registered_users[username].get("current_location")
    return None

def start_panic_timer():
    """Start the panic button timer"""
    st.session_state.panic_timer = time.time()
    st.session_state.panic_active = True

def check_panic_timer():
    """Check if panic button has been held for required seconds"""
    if st.session_state.panic_active and st.session_state.panic_timer:
        elapsed = time.time() - st.session_state.panic_timer
        required_duration = st.session_state.settings["panic_duration"]
        if elapsed >= required_duration:
            st.session_state.panic_active = False
            st.session_state.panic_timer = None
            return True
    return False

def cancel_panic():
    """Cancel the panic alert"""
    st.session_state.panic_active = False
    st.session_state.panic_timer = None

def send_enhanced_emergency_alert():
    """Send enhanced emergency alert with type-specific messaging"""
    if not st.session_state.location:
        st.error("❌ Cannot send alert: No location available. Please update your location first.")
        return
        
    protocol = EMERGENCY_PROTOCOLS[st.session_state.emergency_type]
    
    if st.session_state.user:
        update_user_location(st.session_state.user["username"], 
                           st.session_state.location["lat"], 
                           st.session_state.location["lng"],
                           source="panic_alert")
    
    if st.session_state.user:
        log_panic_event(st.session_state.user["username"], st.session_state.emergency_type, st.session_state.location)
    
    contacts_to_notify = []
    if "all" in protocol["contacts"]:
        contacts_to_notify = st.session_state.contacts
    else:
        contacts_to_notify = [c for c in st.session_state.contacts if c["type"] in protocol["contacts"]]
    
    priority_contacts = [c for c in st.session_state.contacts if c.get("priority", 0) == 1]
    contacts_to_notify.extend(priority_contacts)
    
    contacts_to_notify = list({c["name"]: c for c in contacts_to_notify}.values())
    
    for contact in contacts_to_notify:
        add_history("alert", f"Alert sent to {contact['name']}", 
                   f"Emergency: {st.session_state.emergency_type}. {protocol['message']}")
    
    if st.session_state.settings.get("sound_alerts", True):
        add_history("alert", "Emergency Siren Activated", "Loud alarm activated to attract attention")
    
    st.success(f"🚨 {protocol['icon']} {protocol['message']} Sent to {len(contacts_to_notify)} contacts!")

def register_user(username, password, name, email, phone, authority="Civilian", role="user"):
    """Register a new user"""
    if username in st.session_state.registered_users:
        return False, "Username already exists"
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.registered_users[username] = {
        "password": password,
        "name": name,
        "email": email,
        "phone": phone,
        "id": f"USER{len(st.session_state.registered_users):03d}",
        "authority": authority,
        "role": role,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "profile_pic": None,
        "status": "active",
        "last_login": timestamp,
        "current_location": None,
        "location_history": []
    }
    return True, "User registered successfully"

def authenticate_user(username, password):
    """Authenticate user credentials"""
    if username in st.session_state.registered_users:
        user_data = st.session_state.registered_users[username]
        if user_data["password"] == password:
            user_data["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True, user_data
    return False, None

def save_profile_picture(username, uploaded_file):
    """Save profile picture to user data"""
    if username in st.session_state.registered_users:
        st.session_state.registered_users[username]["profile_pic"] = uploaded_file
        return True
    return False

def get_profile_picture(username):
    """Get profile picture from user data"""
    if username in st.session_state.registered_users:
        return st.session_state.registered_users[username].get("profile_pic")
    return None

# ---- Admin Functions (No Demo Data) ----
def get_system_stats():
    """Get comprehensive system statistics for admin dashboard"""
    total_users = len([u for u in st.session_state.registered_users.values() if u.get("role") != "admin"])
    active_users = len([u for u in st.session_state.registered_users.values() 
                       if u.get("role") != "admin" and u.get("status") == "active"])
    total_emergencies = len(st.session_state.panic_events)
    today_emergencies = len([e for e in st.session_state.panic_events 
                           if e["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d"))])
    
    emergency_types = {}
    for event in st.session_state.panic_events:
        e_type = event["emergency_type"]
        emergency_types[e_type] = emergency_types.get(e_type, 0) + 1
    
    users_in_emergency = len(set([e["username"] for e in st.session_state.panic_events 
                                if e["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d"))]))
    
    recent_location_users = 0
    five_min_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    for user in st.session_state.registered_users.values():
        if user.get("role") == "admin":
            continue
        loc = user.get("current_location")
        if loc and loc.get("timestamp", "") >= five_min_ago:
            recent_location_users += 1
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_emergencies": total_emergencies,
        "today_emergencies": today_emergencies,
        "emergency_types": emergency_types,
        "users_in_emergency": users_in_emergency,
        "recent_location_users": recent_location_users
    }

def export_system_data():
    """Export system data for backup"""
    export_data = {
        "users": st.session_state.registered_users,
        "panic_events": st.session_state.panic_events,
        "system_logs": st.session_state.system_logs,
        "admin_settings": st.session_state.admin_settings,
        "export_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return json.dumps(export_data, indent=2)

def import_system_data(uploaded_file):
    """Import system data from backup"""
    try:
        data = json.load(uploaded_file)
        st.session_state.registered_users = data.get("users", st.session_state.registered_users)
        st.session_state.panic_events = data.get("panic_events", st.session_state.panic_events)
        st.session_state.system_logs = data.get("system_logs", st.session_state.system_logs)
        st.session_state.admin_settings = data.get("admin_settings", st.session_state.admin_settings)
        return True, "System data imported successfully"
    except Exception as e:
        return False, f"Error importing data: {str(e)}"

def create_user_report():
    """Create a comprehensive user report"""
    users_data = []
    for username, user_data in st.session_state.registered_users.items():
        if user_data.get("role") == "admin":
            continue
            
        location = user_data.get('current_location')
        location_str = f"{location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}" if location else "No location"
        location_time = location.get('timestamp', 'Never') if location else "Never"
        
        users_data.append({
            "User ID": user_data["id"],
            "Username": username,
            "Name": user_data["name"],
            "Email": user_data["email"],
            "Phone": user_data["phone"],
            "Authority": user_data["authority"],
            "Role": user_data["role"],
            "Status": user_data.get("status", "active"),
            "Created At": user_data["created_at"],
            "Last Login": user_data.get("last_login", "Never"),
            "Current Location": location_str,
            "Location Updated": location_time
        })
    return pd.DataFrame(users_data)

def create_emergency_report():
    """Create a comprehensive emergency report"""
    emergencies_data = []
    for event in st.session_state.panic_events:
        emergencies_data.append({
            "Username": event["username"],
            "User Name": event.get("user_name", event["username"]),
            "Emergency Type": event["emergency_type"],
            "Timestamp": event["timestamp"],
            "Date": event["date"],
            "Latitude": event["location"]["lat"],
            "Longitude": event["location"]["lng"],
            "Status": "Active" if event["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d")) else "Resolved"
        })
    return pd.DataFrame(emergencies_data)

def create_live_tracking_map():
    """Create an enhanced folium map with all users' real-time locations"""
    locations = []
    for username, user_data in st.session_state.registered_users.items():
        if user_data.get("role") != "admin" and user_data.get("current_location"):
            loc = user_data["current_location"]
            if isinstance(loc, dict) and "lat" in loc and "lng" in loc:
                locations.append((loc["lat"], loc["lng"]))
    
    if locations:
        avg_lat = sum([loc[0] for loc in locations]) / len(locations)
        avg_lng = sum([loc[1] for loc in locations]) / len(locations)
    else:
        avg_lat, avg_lng = 14.5995, 120.9842  # Default center
    
    m = folium.Map(location=[avg_lat, avg_lng], zoom_start=13, control_scale=True)
    
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        name='CartoDB Light',
        attr='© OpenStreetMap, © CartoDB'
    ).add_to(m)
    
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        name='CartoDB Dark',
        attr='© OpenStreetMap, © CartoDB'
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        name='OpenStreetMap'
    ).add_to(m)
    
    folium.plugins.Fullscreen().add_to(m)
    folium.plugins.MousePosition().add_to(m)
    
    for username, user_data in st.session_state.registered_users.items():
        if user_data.get("role") == "admin":
            continue
            
        location = user_data.get("current_location")
        if not location or not isinstance(location, dict):
            continue
            
        lat = location.get("lat")
        lng = location.get("lng")
        timestamp = location.get("timestamp", "Unknown")
        source = location.get("source", "unknown")
        
        if lat is None or lng is None:
            continue
        
        try:
            loc_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            time_diff = (datetime.datetime.now() - loc_time).total_seconds() / 60
            is_recent = time_diff < 30
        except:
            is_recent = False
        
        if user_data.get("status") == "active" and is_recent:
            color = "green"
            status_icon = "🟢"
        elif user_data.get("status") == "active":
            color = "orange"
            status_icon = "🟡"
        else:
            color = "gray"
            status_icon = "⚪"
        
        has_emergency = False
        for event in st.session_state.panic_events:
            if event["username"] == username and event["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d")):
                has_emergency = True
                color = "red"
                status_icon = "🔴"
                break
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 300px; background: white; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px;">
                <h4 style="margin: 0; font-size: 16px; color: white;">{user_data['name']}</h4>
                <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9; color: white;">{username}</p>
            </div>
            <div style="padding: 15px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <div>
                        <div style="color: #666; font-size: 11px;">STATUS</div>
                        <div style="font-weight: bold; font-size: 14px; color: #000;">{status_icon} {user_data.get('status', 'active').title()}</div>
                    </div>
                    <div>
                        <div style="color: #666; font-size: 11px;">ROLE</div>
                        <div style="font-weight: bold; font-size: 14px; color: #000;">{user_data['role'].title()}</div>
                    </div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="color: #666; font-size: 11px;">CURRENT LOCATION</div>
                    <div style="font-family: monospace; background: #f5f5f5; padding: 8px; border-radius: 5px; font-size: 12px; color: #000;">
                        {lat:.6f}, {lng:.6f}
                    </div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="color: #666; font-size: 11px;">LAST UPDATE</div>
                    <div style="font-size: 12px; color: #000;">{timestamp}</div>
                    <div style="font-size: 11px; color: #666;">via {source.replace('_', ' ').title()}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="color: #666; font-size: 11px;">CONTACT</div>
                    <div style="font-size: 12px; color: #000;">📞 {user_data['phone']}</div>
                    <div style="font-size: 12px; color: #000;">✉️ {user_data['email']}</div>
                </div>
                <a href="https://www.google.com/maps?q={lat},{lng}" target="_blank" 
                   style="display: block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                          text-align: center; padding: 8px; border-radius: 5px; text-decoration: none; font-size: 12px;">
                    📍 Open in Google Maps
                </a>
            </div>
        </div>
        """
        
        if has_emergency:
            icon = folium.Icon(
                color="red",
                icon="exclamation-triangle",
                prefix="fa",
                icon_color="white"
            )
            folium.Circle(
                [lat, lng],
                radius=200,
                color="red",
                weight=2,
                fill=True,
                fillColor="red",
                fillOpacity=0.2,
                popup="Emergency Zone"
            ).add_to(m)
        elif user_data.get("status") == "active":
            if is_recent:
                icon = folium.Icon(
                    color="green",
                    icon="user-check",
                    prefix="fa",
                    icon_color="white"
                )
            else:
                icon = folium.Icon(
                    color="orange",
                    icon="user-clock",
                    prefix="fa",
                    icon_color="white"
                )
        else:
            icon = folium.Icon(
                color="gray",
                icon="user-slash",
                prefix="fa",
                icon_color="white"
            )
        
        folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"<b>{user_data['name']}</b><br>{status_icon} {user_data.get('status', 'active').title()}",
            icon=icon
        ).add_to(m)
        
        folium.Circle(
            [lat, lng],
            radius=50,
            color=color,
            weight=1,
            fill=True,
            fillColor=color,
            fillOpacity=0.1
        ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    
    return m

def get_active_emergencies():
    """Get currently active emergencies"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    active = []
    for event in st.session_state.panic_events:
        if event["timestamp"].startswith(today):
            active.append(event)
    return active

# ---- Sidebar with User Info ----
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🛡️ SafeTap</h2>
            <p>One Tap Can Save a Life</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user:
            if st.session_state.user.get("role") == "admin":
                sections = [
                    {"icon": "🏠", "name": "Admin Dashboard", "view": "admin_dashboard"},
                    {"icon": "🗺️", "name": "Live Tracking Map", "view": "live_tracking"},
                    {"icon": "👥", "name": "User Management", "view": "user_management"},
                    {"icon": "📊", "name": "System Analytics", "view": "system_analytics"},
                    {"icon": "⚙️", "name": "System Settings", "view": "system_settings"},
                ]
            else:
                sections = [
                    {"icon": "🏠", "name": "Home", "view": "main"},
                    {"icon": "👤", "name": "Profile", "view": "profile"},
                    {"icon": "📍", "name": "My Location", "view": "my_location"},
                    {"icon": "📚", "name": "History", "view": "history"},
                    {"icon": "⚙️", "name": "Settings", "view": "settings"},
                ]
            
            for section in sections:
                is_active = st.session_state.view == section["view"]
                
                if st.button(
                    f"{section['icon']} {section['name']}", 
                    key=f"nav_{section['view']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.view = section["view"]
                    st.rerun()
        
        if st.session_state.user:
            st.markdown("---")
            
            role_text = "Admin Info" if st.session_state.user.get("role") == "admin" else "User Info"
            st.markdown(f"""
            <div class="sidebar-user-info">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0;">👋 {role_text}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            user_info_items = [
                ("Name", st.session_state.user['name']),
                ("Authority", st.session_state.user['authority']),
                ("Status", "🟢 Online"),
                ("Role", st.session_state.user.get('role', 'user').title()),
                ("User ID", st.session_state.user['id'])
            ]
            
            for label, value in user_info_items:
                st.markdown(f"""
                <div class="user-info-item">
                    <span class="user-info-label">{label}</span>
                    <span class="user-info-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
                st.session_state.user = None
                st.session_state.view = "login"
                st.rerun()

# ---- Mini Dashboard (No Demo Data) ----
def show_mini_dashboard():
    alerts_sent = len([h for h in st.session_state.history if h["type"] == "alert"])
    location_updates = len([h for h in st.session_state.history if h["type"] == "location"])
    contacts_count = len(st.session_state.contacts)
    
    st.markdown("""
    <div class="dashboard-container">
        <div class="dashboard-title">
            📊 Safety Dashboard
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🛡️</div>
                <div class="stat-value">{}</div>
                <div class="stat-label">Alerts Sent</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📍</div>
                <div class="stat-value">{}</div>
                <div class="stat-label">Location Updates</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value">{}</div>
                <div class="stat-label">Emergency Contacts</div>
            </div>
        </div>
    </div>
    """.format(alerts_sent, location_updates, contacts_count), unsafe_allow_html=True)

# ---- Emergency Button Component ----
def create_emergency_button():
    if not st.session_state.location:
        st.warning("⚠️ Please set your location first in 'My Location' before using the emergency button.")
        return
        
    protocol = EMERGENCY_PROTOCOLS[st.session_state.emergency_type]
    
    if st.session_state.panic_active:
        elapsed = time.time() - st.session_state.panic_timer
        required_duration = st.session_state.settings["panic_duration"]
        progress = min(elapsed / required_duration, 1.0)
        st.progress(progress, text=f"HOLDING... {int(elapsed)}s / {required_duration}s")
        
        st.warning(f"{protocol['icon']} {protocol['message']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("❌ Cancel Alert", key="cancel_panic", use_container_width=True):
                cancel_panic()
                st.rerun()
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.button("", key="panic_btn", on_click=start_panic_timer)
            
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem; cursor: pointer;" 
                 onclick="document.querySelector('button[key=\\'panic_btn\\']').click()">
                <div class="emergency-alert-button" style="background: linear-gradient(135deg, {protocol['color']}, #ff6b6b);">
                    <div class="alert-icon">{protocol['icon']}</div>
                </div>
            </div>
            <script>
            document.querySelector('.emergency-alert-button').addEventListener('click', function() {{
                document.querySelector('button[key="panic_btn"]').click();
            }});
            </script>
            """, unsafe_allow_html=True)

# ---- Main View ----
def show_main():
    if check_panic_timer():
        send_enhanced_emergency_alert()
        st.rerun()
    
    st.markdown('<div class="safe-header"><h1>🛡️ SafeTap Dashboard</h1><p>Emergency Response System</p></div>', unsafe_allow_html=True)
    
    if st.session_state.user:
        st.write(f"### 👋 Welcome, {st.session_state.user['name']}")
        
        if not st.session_state.location:
            st.warning("⚠️ Please go to 'My Location' to set your location before using the emergency button.")
        else:
            st.write("Your safety is our priority. Tap the alert icon below in case of emergency.")
        
        st.write("")
    
    create_emergency_button()
    show_mini_dashboard()

# ---- Profile View ----
def show_profile():
    st.markdown('<div class="safe-header"><h1>👤 User Profile</h1><p>Manage your account information</p></div>', unsafe_allow_html=True)
    
    if st.session_state.user:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Profile Picture")
            
            current_profile_pic = get_profile_picture(st.session_state.user["username"])
            
            if current_profile_pic is not None:
                image = Image.open(current_profile_pic)
                st.image(image, caption="Current Profile Picture", width=150)
            else:
                st.info("No profile picture uploaded")
            
            uploaded_file = st.file_uploader("Upload Profile Picture", type=['jpg', 'png', 'jpeg'], key="profile_pic_uploader")
            if uploaded_file is not None:
                if save_profile_picture(st.session_state.user["username"], uploaded_file):
                    st.success("✅ Profile picture saved successfully!")
                    st.rerun()
            
            if current_profile_pic is not None:
                if st.button("🗑️ Remove Profile Picture", use_container_width=True):
                    if save_profile_picture(st.session_state.user["username"], None):
                        st.success("✅ Profile picture removed!")
                        st.rerun()
            
            st.subheader("Account Status")
            st.info(f"**Status:** 🟢 Active")
            st.info(f"**Member Since:** {st.session_state.user.get('created_at', '2024-01-01')}")
            st.info(f"**User ID:** {st.session_state.user.get('id', 'N/A')}")
        
        with col2:
            st.subheader("Personal Information")
            
            with st.form("profile_form"):
                name = st.text_input("Full Name", value=st.session_state.user.get('name', ''))
                email = st.text_input("Email", value=st.session_state.user.get('email', ''))
                phone = st.text_input("Phone", value=st.session_state.user.get('phone', ''))
                authority = st.text_input("Authority", value=st.session_state.user.get('authority', ''), disabled=True)
                
                if st.form_submit_button("💾 Update Profile"):
                    st.session_state.user['name'] = name
                    st.session_state.user['email'] = email
                    st.session_state.user['phone'] = phone
                    st.success("✅ Profile updated successfully!")
        
        st.subheader("🆘 Emergency Contacts")
        
        if not st.session_state.contacts:
            st.info("No emergency contacts added yet. Add your first contact below.")
        
        contacts_col1, contacts_col2, contacts_col3 = st.columns(3)
        
        with contacts_col1:
            st.write("**Primary Contacts**")
            for contact in st.session_state.contacts[:2]:
                st.info(f"{contact.get('icon', '👤')} **{contact['name']}**\n\n{contact['number']}")
        
        with contacts_col2:
            st.write("**Secondary Contacts**")
            for contact in st.session_state.contacts[2:]:
                st.info(f"{contact.get('icon', '👤')} **{contact['name']}**\n\n{contact['number']}")
        
        with contacts_col3:
            st.write("**Add New Contact**")
            with st.form("new_contact"):
                new_name = st.text_input("Contact Name")
                new_number = st.text_input("Phone Number")
                contact_type = st.selectbox("Type", ["Family", "Friend", "Emergency", "Other"])
                
                if st.form_submit_button("➕ Add Contact"):
                    if new_name and new_number:
                        new_contact = {
                            "name": new_name,
                            "number": new_number,
                            "type": contact_type.lower(),
                            "icon": "👤",
                            "priority": 2
                        }
                        st.session_state.contacts.append(new_contact)
                        st.success(f"✅ Added {new_name} to emergency contacts!")
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all fields")

# ---- Settings View ----
def show_settings():
    st.markdown('<div class="safe-header"><h1>⚙️ Settings</h1><p>Customize your SafeTap experience</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔔 Notifications", "📍 Location", "🔄 System"])
    
    with tab1:
        st.subheader("Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Alert Preferences**")
            st.session_state.settings["notifications"] = st.toggle("Push Notifications", 
                                                                 value=st.session_state.settings.get("notifications", True))
            st.session_state.settings["sound_alerts"] = st.toggle("Sound Alerts", 
                                                                value=st.session_state.settings.get("sound_alerts", True))
            st.session_state.settings["vibration"] = st.toggle("Vibration", 
                                                             value=st.session_state.settings.get("vibration", True))
        
        with col2:
            st.write("**Alert Methods**")
            st.session_state.settings["auto_send_alerts"] = st.toggle("Auto-send Alerts", 
                                                                     value=st.session_state.settings.get("auto_send_alerts", True))
            st.session_state.settings["voice_recording"] = st.toggle("Voice Recording", 
                                                                   value=st.session_state.settings.get("voice_recording", True))
    
    with tab2:
        st.subheader("Location Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tracking Preferences**")
            st.session_state.settings["location_tracking"] = st.toggle("Location Tracking", 
                                                                      value=st.session_state.settings.get("location_tracking", True))
            st.session_state.settings["high_accuracy"] = st.toggle("High Accuracy Mode", 
                                                                 value=st.session_state.settings.get("high_accuracy", True))
    
    with tab3:
        st.subheader("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Emergency Settings**")
            panic_duration = st.slider("Panic Button Hold Duration (seconds)", 
                                      min_value=1, max_value=10, 
                                      value=st.session_state.settings.get("panic_duration", 3))
            st.session_state.settings["panic_duration"] = panic_duration
            
            emergency_message = st.text_area("Default Emergency Message", 
                                           value=st.session_state.settings.get("emergency_message", ""),
                                           height=100)
            st.session_state.settings["emergency_message"] = emergency_message
        
        with col2:
            st.write("**System Info**")
            st.info(f"**App Version:** 2.1.0")
            st.info(f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d')}")
            
            if st.button("🔄 Reset Settings to Default"):
                st.session_state.settings = {
                    "notifications": True,
                    "location_tracking": True,
                    "high_accuracy": True,
                    "vibration": True,
                    "sound_alerts": True,
                    "voice_recording": True,
                    "auto_send_alerts": True,
                    "panic_duration": 3,
                    "emergency_message": "EMERGENCY! I need immediate assistance. My current location has been shared with this alert."
                }
                st.success("✅ Settings reset to defaults!")

# ---- History View ----
def show_history():
    st.markdown('<div class="safe-header"><h1>📚 History</h1><p>View your emergency activity history</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("📝 No history records yet. Your emergency alerts and activities will appear here.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "Alert", "Location", "System"])
        with col2:
            date_filter = st.date_input("Filter by Date", value=datetime.datetime.now())
        with col3:
            search_term = st.text_input("Search History")
        
        for i, event in enumerate(st.session_state.history):
            if filter_type != "All" and event["type"] != filter_type.lower():
                continue
            
            if search_term and search_term.lower() not in event["title"].lower() and search_term.lower() not in event["details"].lower():
                continue
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    icon = "📱"
                    if event["type"] == "alert":
                        icon = "🚨"
                    elif event["type"] == "location":
                        icon = "📍"
                    elif event["type"] == "system":
                        icon = "⚙️"
                    
                    st.write(f"**{icon} {event['title']}**")
                    st.write(event["details"])
                
                with col2:
                    st.write(f"**{event['date']}**")
                    st.caption(event["timestamp"])
                
                st.divider()

# ---- My Location View ----
def show_my_location():
    st.markdown('<div class="safe-header"><h1>📍 My Location</h1><p>Set and update your current location</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.user:
        st.error("Please login first")
        return
    
    user_loc = get_user_location(st.session_state.user["username"])
    
    st.markdown("""
    <div class="location-info-box">
        <h2 style="margin:0;">📍 Current Location</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.session_state.location:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 2rem; margin: 1rem 0;">
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; opacity: 0.8;">Coordinates</div>
                    <div class="location-coordinates">
                        {st.session_state.location['lat']:.6f}<br>
                        {st.session_state.location['lng']:.6f}
                    </div>
                    <div class="location-accuracy">
                        📡 Accuracy: ±{st.session_state.location['accuracy']} meters
                    </div>
                    <div class="location-timestamp">
                        Last Updated: {user_loc.get('timestamp', 'Not yet updated') if user_loc else 'Not yet updated'}<br>
                        Source: {user_loc.get('source', 'unknown').replace('_', ' ').title() if user_loc else 'Unknown'}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📍 No location set. Please set your location below.")
        
        st.subheader("📍 Recent Location History")
        user_data = st.session_state.registered_users.get(st.session_state.user["username"], {})
        location_history = user_data.get("location_history", [])
        
        if location_history:
            for entry in location_history[:5]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 0.8rem; margin: 0.5rem 0;">
                    <div style="font-family: monospace;">📍 {entry['lat']:.6f}, {entry['lng']:.6f}</div>
                    <div style="font-size: 0.8rem; opacity: 0.7;">🕐 {entry['timestamp']} via {entry['source'].replace('_', ' ').title()}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No location history yet")
    
    with col2:
        st.subheader("📍 Set Location")
        st.write("Enter your current coordinates:")
        
        with st.form("location_form"):
            lat = st.number_input("Latitude", value=14.5995 if not st.session_state.location else st.session_state.location['lat'], format="%.6f")
            lng = st.number_input("Longitude", value=120.9842 if not st.session_state.location else st.session_state.location['lng'], format="%.6f")
            accuracy = st.number_input("Accuracy (meters)", value=50, min_value=1, max_value=1000)
            
            if st.form_submit_button("📍 Set Location", use_container_width=True):
                st.session_state.location = {
                    "lat": lat,
                    "lng": lng,
                    "accuracy": accuracy
                }
                update_user_location(st.session_state.user["username"], lat, lng, source="manual_entry")
                st.success("✅ Location set successfully!")
                st.rerun()
        
        st.markdown("---")
        st.subheader("📍 Location Actions")
        
        if st.session_state.location:
            if st.button("📱 Share Location", use_container_width=True):
                update_user_location(st.session_state.user["username"], 
                                   st.session_state.location["lat"], 
                                   st.session_state.location["lng"],
                                   source="share")
                st.success("✅ Location shared with emergency contacts!")
            
            if st.button("📍 Save Current Location", use_container_width=True):
                update_user_location(st.session_state.user["username"], 
                                   st.session_state.location["lat"], 
                                   st.session_state.location["lng"],
                                   source="save")
                st.success("✅ Location saved to history!")
            
            st.markdown(f"""
            <div style="margin-top: 2rem;">
                <a href="https://www.google.com/maps?q={st.session_state.location['lat']},{st.session_state.location['lng']}" 
                   target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); 
                   color: white; padding: 1rem; border-radius: 10px; text-decoration: none;">
                    📍 Open in Google Maps
                </a>
            </div>
            """, unsafe_allow_html=True)

# ---- Live Tracking View for Admin ----
def show_live_tracking():
    st.markdown('<div class="safe-header"><h1>🗺️ Live User Tracking</h1><p>Real-time location tracking</p></div>', unsafe_allow_html=True)
    
    total_users = len([u for u in st.session_state.registered_users.values() if u.get("role") != "admin"])
    active_users = len([u for u in st.session_state.registered_users.values() 
                       if u.get("role") != "admin" and u.get("status") == "active"])
    
    recent_users = 0
    five_min_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    for user in st.session_state.registered_users.values():
        if user.get("role") == "admin":
            continue
        loc = user.get("current_location")
        if loc and loc.get("timestamp", "") >= five_min_ago:
            recent_users += 1
    
    update_interval = st.session_state.admin_settings.get("location_update_interval", 30)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Active Users", active_users)
    with col3:
        st.metric("Recent Locations", recent_users)
    with col4:
        st.metric("Update Interval", f"{update_interval}s")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔄 Refresh Map", use_container_width=True):
            st.rerun()
    with col2:
        show_history_toggle = st.checkbox("Show Location History")
    
    st.subheader("📍 Live User Locations")
    
    if total_users == 0:
        st.info("No users registered yet. Users will appear here once they register and set their location.")
    else:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        live_map = create_live_tracking_map()
        folium_static(live_map, width=1200, height=600)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <h4>📍 Map Legend</h4>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><span style="color: green;">🟢</span> Active User (recent location)</div>
                <div><span style="color: orange;">🟡</span> Active User (stale location)</div>
                <div><span style="color: red;">🔴</span> Emergency Active</div>
                <div><span style="color: gray;">⚪</span> Inactive User</div>
                <div><span>📍</span> Click on markers for details</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 User Location List")
        
        location_data = []
        for username, user_data in st.session_state.registered_users.items():
            if user_data.get("role") == "admin":
                continue
                
            location = user_data.get("current_location")
            lat = location.get("lat", "N/A") if location else "N/A"
            lng = location.get("lng", "N/A") if location else "N/A"
            timestamp = location.get("timestamp", "Never") if location else "Never"
            source = location.get("source", "unknown") if location else "unknown"
            
            has_emergency = False
            for event in st.session_state.panic_events:
                if event["username"] == username and event["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d")):
                    has_emergency = True
                    break
            
            status = "🔴 EMERGENCY" if has_emergency else "🟢 Active" if user_data.get("status") == "active" else "⚪ Inactive"
            
            location_data.append({
                "User": user_data["name"],
                "Username": username,
                "Status": status,
                "Latitude": f"{lat:.6f}" if lat != "N/A" else "N/A",
                "Longitude": f"{lng:.6f}" if lng != "N/A" else "N/A",
                "Last Update": timestamp,
                "Source": source.replace("_", " ").title() if source != "unknown" else "Unknown"
            })
        
        if location_data:
            df = pd.DataFrame(location_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Location Report (CSV)",
                data=csv,
                file_name=f"user_locations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        if show_history_toggle:
            st.subheader("📍 Location History")
            user_list = [u for u in st.session_state.registered_users.keys() if u != "admin"]
            if user_list:
                selected_user = st.selectbox("Select user to view history", user_list)
                
                if selected_user:
                    user_data = st.session_state.registered_users[selected_user]
                    history = user_data.get("location_history", [])
                    
                    if history:
                        for entry in history[:20]:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"📍 **Location:** {entry['lat']:.6f}, {entry['lng']:.6f}")
                                    st.caption(f"Source: {entry['source'].replace('_', ' ').title()}")
                                with col2:
                                    st.write(f"🕐 {entry['timestamp']}")
                                st.divider()
                    else:
                        st.info("No location history for this user")

# ---- Admin Dashboard ----
def show_admin_dashboard():
    st.markdown('<div class="safe-header"><h1>👑 Admin Dashboard</h1><p>System Administration Panel</p></div>', unsafe_allow_html=True)
    
    stats = get_system_stats()
    active_emergencies = get_active_emergencies()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats["total_users"], f"{stats['active_users']} active")
    with col2:
        st.metric("Total Emergencies", stats["total_emergencies"], f"{stats['today_emergencies']} today")
    with col3:
        st.metric("Active Now", len(active_emergencies), f"{stats['users_in_emergency']} users")
    with col4:
        st.metric("Live Locations", stats['recent_location_users'], "last 5 min")
    
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗺️ Live Tracking Map", use_container_width=True):
            st.session_state.view = "live_tracking"
            st.rerun()
    
    with col2:
        if st.button("📊 Generate Reports", use_container_width=True):
            st.session_state.view = "system_analytics"
            st.rerun()
    
    with col3:
        if st.button("👥 User Management", use_container_width=True):
            st.session_state.view = "user_management"
            st.rerun()
    
    with col4:
        if st.button("⚙️ System Settings", use_container_width=True):
            st.session_state.view = "system_settings"
            st.rerun()
    
    if active_emergencies:
        st.subheader("🚨 Active Emergencies Now")
        for event in active_emergencies[:5]:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{event.get('user_name', event['username'])}**")
                    st.caption(event['emergency_type'].title())
                with col2:
                    location = event['location']
                    st.write(f"📍 {location['lat']:.6f}, {location['lng']:.6f}")
                with col3:
                    if st.button(f"View on Map", key=f"view_active_{event['timestamp']}"):
                        st.session_state.view = "live_tracking"
                        st.rerun()
                st.divider()
    
    st.subheader("📍 Recent Location Updates")
    recent_locations = []
    for username, user_data in st.session_state.registered_users.items():
        if user_data.get("role") == "admin":
            continue
        loc = user_data.get("current_location")
        if loc and "timestamp" in loc:
            recent_locations.append({
                "User": user_data["name"],
                "Location": f"{loc.get('lat', 'N/A')}, {loc.get('lng', 'N/A')}",
                "Time": loc.get('timestamp', 'Unknown'),
                "Source": loc.get('source', 'unknown')
            })
    
    recent_locations.sort(key=lambda x: x["Time"], reverse=True)
    
    if recent_locations:
        for loc in recent_locations[:10]:
            st.caption(f"👤 {loc['User']} - 📍 {loc['Location']} - 🕐 {loc['Time']} - via {loc['Source']}")
    else:
        st.info("No location updates yet")
    
    st.subheader("📊 Emergency Type Distribution")
    if stats["emergency_types"] and PLOTLY_AVAILABLE:
        fig = px.pie(
            values=list(stats["emergency_types"].values()),
            names=list(stats["emergency_types"].keys()),
            title="Emergency Types"
        )
        safe_plotly_chart(fig, use_container_width=True)
    else:
        st.info("No emergency data available yet")

# ---- User Management ----
def show_user_management():
    st.markdown('<div class="safe-header"><h1>👥 User Management</h1><p>Manage system users and permissions</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 View Users", "➕ Add User", "📊 User Reports"])
    
    with tab1:
        st.subheader("User List")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search users by name, email, or username")
        with col2:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user"])
        
        users_data = []
        for username, user_data in st.session_state.registered_users.items():
            if username == "admin":
                continue
                
            if search_term and search_term.lower() not in username.lower() and search_term.lower() not in user_data['name'].lower() and search_term.lower() not in user_data['email'].lower():
                continue
            if role_filter != "All" and user_data['role'] != role_filter:
                continue
                
            location = user_data.get('current_location')
            location_str = f"{location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}" if location else "Not set"
            location_time = location.get('timestamp', 'Never') if location else "Never"
            
            users_data.append({
                "Username": username,
                "Name": user_data['name'],
                "Email": user_data['email'],
                "Role": user_data['role'],
                "Authority": user_data['authority'],
                "Status": user_data.get('status', 'active'),
                "Location": location_str,
                "Last Update": location_time,
                "Last Login": user_data.get('last_login', 'Never'),
                "Actions": username
            })
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("User Actions")
            selected_user = st.selectbox("Select user to manage", [u["Username"] for u in users_data])
            
            if selected_user:
                user_data = st.session_state.registered_users[selected_user]
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🔄 Reset Password", key="reset_pass"):
                        st.session_state.registered_users[selected_user]["password"] = "temp123"
                        st.success(f"Password reset to 'temp123' for {selected_user}")
                
                with col2:
                    new_status = "suspended" if user_data.get('status') == 'active' else 'active'
                    if st.button(f"🔒 {new_status.title()} User", key="toggle_status"):
                        st.session_state.registered_users[selected_user]["status"] = new_status
                        st.success(f"User {selected_user} {new_status}")
                        st.rerun()
                
                with col3:
                    if st.button("📍 View on Map", key="view_location"):
                        st.session_state.view = "live_tracking"
                        st.rerun()
                
                with col4:
                    if st.button("🗑️ Delete User", key="delete_user"):
                        if selected_user != st.session_state.user["username"]:
                            del st.session_state.registered_users[selected_user]
                            st.success(f"User {selected_user} deleted")
                            st.rerun()
                        else:
                            st.error("Cannot delete your own account")
        else:
            st.info("No users found matching the search criteria")
    
    with tab2:
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *")
                new_name = st.text_input("Full Name *")
                new_email = st.text_input("Email *")
            
            with col2:
                new_password = st.text_input("Password *", type="password")
                new_phone = st.text_input("Phone *")
                new_authority = st.selectbox("Authority", ["Civilian"])
                new_role = st.selectbox("Role", ["user"])
            
            if st.form_submit_button("➕ Add User"):
                if all([new_username, new_password, new_name, new_email, new_phone]):
                    success, message = register_user(new_username, new_password, new_name, new_email, new_phone, new_authority, new_role)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill in all required fields")
    
    with tab3:
        st.subheader("User Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Generate User Report", use_container_width=True):
                user_report = create_user_report()
                if not user_report.empty:
                    st.dataframe(user_report, use_container_width=True)
                    
                    csv = user_report.to_csv(index=False)
                    st.download_button(
                        label="📥 Download User Report (CSV)",
                        data=csv,
                        file_name=f"user_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No users to report")
        
        with col2:
            if st.button("📊 User Statistics", use_container_width=True):
                stats = get_system_stats()
                
                roles = {}
                for user in st.session_state.registered_users.values():
                    if user.get("role") == "admin":
                        continue
                    role = user['role']
                    roles[role] = roles.get(role, 0) + 1
                
                if roles and PLOTLY_AVAILABLE:
                    fig = px.pie(
                        values=list(roles.values()),
                        names=list(roles.keys()),
                        title="User Role Distribution"
                    )
                    safe_plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No user statistics available")

# ---- System Analytics ----
def show_system_analytics():
    st.markdown('<div class="safe-header"><h1>📊 System Analytics</h1><p>System performance and usage analytics</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🚨 Emergencies", "💾 Data Management"])
    
    with tab1:
        st.subheader("System Performance Metrics")
        st.info("Performance metrics will be displayed here based on actual system data.")
    
    with tab2:
        st.subheader("Emergency Analytics")
        
        if st.session_state.panic_events:
            emergency_report = create_emergency_report()
            if not emergency_report.empty:
                st.dataframe(emergency_report, use_container_width=True)
                
                csv = emergency_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download Emergency Report (CSV)",
                    data=csv,
                    file_name=f"emergency_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No emergency data available for analytics")
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Export System Data")
            st.write("Export all system data for backup or analysis")
            
            export_data = export_system_data()
            st.download_button(
                label="📥 Download System Backup",
                data=export_data,
                file_name=f"safetap_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            st.subheader("📥 Import System Data")
            st.write("Import system data from backup file")
            
            uploaded_file = st.file_uploader("Choose backup file", type="json")
            if uploaded_file is not None:
                if st.button("🔄 Import Data"):
                    success, message = import_system_data(uploaded_file)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        st.subheader("🧹 System Cleanup")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Old History", use_container_width=True):
                if len(st.session_state.history) > 100:
                    st.session_state.history = st.session_state.history[:100]
                    st.success("✅ Old history cleared")
                else:
                    st.info("No old history to clear")

# ---- System Settings ----
def show_system_settings():
    st.markdown('<div class="safe-header"><h1>⚙️ System Settings</h1><p>Configure system-wide settings</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 General", "🚨 Emergency", "🔐 Security"])
    
    with tab1:
        st.subheader("General System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.admin_settings["system_name"] = st.text_input(
                "System Name", 
                value=st.session_state.admin_settings.get("system_name", "SafeTap Emergency System")
            )
            
            st.session_state.admin_settings["emergency_response_time"] = st.selectbox(
                "Target Response Time",
                options=["3 minutes", "5 minutes", "10 minutes", "15 minutes"],
                index=1
            )
            
            st.session_state.admin_settings["max_users"] = st.number_input(
                "Maximum Users",
                min_value=100,
                max_value=10000,
                value=st.session_state.admin_settings.get("max_users", 1000)
            )
            
            st.session_state.admin_settings["location_update_interval"] = st.number_input(
                "Location Update Interval (seconds)",
                min_value=5,
                max_value=300,
                value=st.session_state.admin_settings.get("location_update_interval", 30)
            )
        
        with col2:
            st.session_state.admin_settings["auto_backup"] = st.toggle(
                "Automatic Backups",
                value=st.session_state.admin_settings.get("auto_backup", True)
            )
            
            st.session_state.admin_settings["data_retention_days"] = st.slider(
                "Data Retention (days)",
                min_value=30,
                max_value=365,
                value=st.session_state.admin_settings.get("data_retention_days", 90)
            )
            
            st.session_state.admin_settings["system_status"] = st.selectbox(
                "System Status",
                options=["operational", "maintenance", "degraded", "offline"],
                index=0
            )
    
    with tab2:
        st.subheader("Emergency Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.admin_settings["alert_cooldown"] = st.number_input(
                "Alert Cooldown (seconds)",
                min_value=60,
                max_value=3600,
                value=st.session_state.admin_settings.get("alert_cooldown", 300)
            )
        
        with col2:
            enable_location_tracking = st.toggle("Enable Location Tracking", value=True)
            enable_voice_recording = st.toggle("Enable Voice Recording", value=True)
        
        st.info("🔧 These settings affect all users in the system")
    
    with tab3:
        st.subheader("Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            require_strong_passwords = st.toggle("Require Strong Passwords", value=True)
            enable_2fa = st.toggle("Enable Two-Factor Authentication", value=False)
            session_timeout = st.selectbox(
                "Session Timeout",
                options=["15 minutes", "30 minutes", "1 hour", "4 hours", "8 hours"],
                index=2
            )
        
        with col2:
            enable_audit_log = st.toggle("Enable Audit Logging", value=True)
            max_login_attempts = st.number_input("Max Login Attempts", min_value=3, max_value=10, value=5)
        
        st.subheader("Danger Zone")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset All Settings", use_container_width=True):
                st.session_state.admin_settings = {
                    "system_name": "SafeTap Emergency System",
                    "emergency_response_time": "5 minutes",
                    "auto_backup": True,
                    "data_retention_days": 90,
                    "max_users": 1000,
                    "alert_cooldown": 300,
                    "system_status": "operational",
                    "location_update_interval": 30
                }
                st.success("✅ All settings reset to defaults")
        
        with col2:
            if st.button("🚨 Emergency Shutdown", use_container_width=True):
                st.session_state.admin_settings["system_status"] = "offline"
                st.error("🚨 System has been shut down for emergency maintenance")

# ---- Login View ----
def show_login():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="safe-header"><h1>🛡️ SafeTap</h1><p>Emergency Response System</p></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown('### 🔐 Account Login')
            
            role = st.radio("Select Account Type", ["User", "Admin"], horizontal=True)
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            if role == "Admin":
                st.info("""
                **Admin Account:**
                - **Username:** admin
                - **Password:** admin123
                """)
            
            if st.button("🚀 Sign In", use_container_width=True):
                if username and password:
                    authenticated, user_data = authenticate_user(username, password)
                    if authenticated:
                        expected_role = "admin" if role == "Admin" else "user"
                        if user_data.get("role") == expected_role:
                            st.session_state.user = user_data
                            st.session_state.user["username"] = username
                            
                            if user_data.get("role") == "admin":
                                st.session_state.view = "admin_dashboard"
                            else:
                                st.session_state.view = "main"
                            
                            st.success(f"✅ Welcome back, {user_data['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ This account is not registered as {role}")
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("❌ Please fill in all fields")
        
        with tab2:
            st.markdown('### 📝 Create New Account')
            st.warning("⚠️ New users can only register as regular users.")
            
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("👤 Username", placeholder="Choose a username")
                    new_name = st.text_input("📛 Full Name", placeholder="Enter your full name")
                    new_email = st.text_input("📧 Email", placeholder="Enter your email")
                with col2:
                    new_password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                    new_phone = st.text_input("📱 Phone", placeholder="+63 XXX XXX XXXX")
                
                new_authority = st.selectbox("🏢 Authority", ["Civilian"])
                
                if st.form_submit_button("📝 Register Account", use_container_width=True):
                    if all([new_username, new_password, new_name, new_email, new_phone]):
                        if new_password == confirm_password:
                            success, message = register_user(
                                new_username, new_password, new_name, new_email, new_phone, new_authority, "user"
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.session_state.user = st.session_state.registered_users[new_username]
                                st.session_state.user["username"] = new_username
                                st.session_state.view = "main"
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.error("❌ Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ---- Main App Logic ----
if st.session_state.user and st.session_state.view not in ["login", "signup"]:
    show_sidebar()

if st.session_state.view == "login":
    show_login()
elif st.session_state.view == "main":
    show_main()
elif st.session_state.view == "profile":
    show_profile()
elif st.session_state.view == "settings":
    show_settings()
elif st.session_state.view == "history":
    show_history()
elif st.session_state.view == "my_location":
    show_my_location()
elif st.session_state.view == "admin_dashboard":
    show_admin_dashboard()
elif st.session_state.view == "live_tracking":
    show_live_tracking()
elif st.session_state.view == "user_management":
    show_user_management()
elif st.session_state.view == "system_analytics":
    show_system_analytics()
elif st.session_state.view == "system_settings":
    show_system_settings()
else:
    st.session_state.view = "main"
    st.rerun()

# ---- Footer ----
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: white; opacity: 0.7;">
        SafeTap &copy; 2024 | Guardian Innovators<br>
        One Tap Can Save a Life | Emergency Response System
    </div>
""", unsafe_allow_html=True)
