import streamlit as st
import time
import datetime
import pandas as pd
import folium
from streamlit_folium import folium_static, st_folium
import base64
from PIL import Image
import io
import random
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

# ---- Enhanced Custom CSS with Consistent Color Scheme ----
st.markdown("""
<style>
    /* Consistent Blue/Purple Gradient Background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: white;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
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
    
    /* Enhanced Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }
    
    .sidebar .sidebar-content {
        background: transparent !important;
    }
    
    [data-testid="stSidebarNav"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
    }
    
    .sidebar-section {
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 15px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid transparent;
        font-weight: 600;
        color: white !important;
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
        color: white !important;
    }
    
    .sidebar-section.active {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(255, 193, 7, 0.3));
        border-left: 4px solid #ff6b6b;
        color: white !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
    
    .sidebar-header {
        text-align: center;
        padding: 25px 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 25px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Enhanced Sidebar User Info */
    .sidebar-user-info {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
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
        opacity: 0.8;
    }
    
    .user-info-value {
        font-size: 0.9rem;
        font-weight: bold;
        color: #ffeb3b;
    }
    
    /* Emergency Type Selector in Sidebar */
    .emergency-type-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid rgba(255, 235, 59, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .emergency-type-title {
        color: #ffeb3b;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .emergency-option {
        padding: 12px 15px;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        border: 2px solid transparent;
        font-weight: 600;
        margin: 8px 0;
        width: 100%;
    }
    
    .emergency-option:hover {
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        background: rgba(255,255,255,0.15);
    }
    
    .emergency-option.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        border: 2px solid #ffeb3b;
        box-shadow: 0 8px 25px rgba(255, 235, 59, 0.4);
        transform: translateY(-3px) scale(1.03);
    }
    
    .emergency-icon {
        font-size: 1.8rem;
        margin-bottom: 5px;
        display: block;
    }
    
    /* Enhanced Header - Consistent Blue/Purple */
    .safe-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        backdrop-filter: blur(15px);
        color: white;
        border-radius: 0 0 25px 25px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        padding: 3rem 0 2rem 0;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
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
    
    /* Circular Emergency Alert Button - Icon Only */
    .emergency-alert-button {
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b6b, #ff4757);
        color: white;
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
    
    .emergency-alert-button-active {
        animation: alarm 0.8s infinite alternate, pulse-glow 1s infinite alternate;
    }
    
    .alert-icon {
        font-size: 5rem;
        margin-bottom: 0.5rem;
    }
    
    .alert-text {
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    
    .alert-instruction {
        font-size: 0.7rem;
        opacity: 0.9;
        text-align: center;
        font-weight: normal;
        line-height: 1.2;
        margin-top: 0.3rem;
    }
    
    @keyframes pulse-glow {
        0% { 
            box-shadow: 0 0 20px 5px rgba(255, 107, 107, 0.6);
        }
        50% { 
            box-shadow: 0 0 30px 15px rgba(255, 107, 107, 0.8);
        }
        100% { 
            box-shadow: 0 0 20px 5px rgba(255, 107, 107, 0.6);
        }
    }
    
    @keyframes alarm {
        from { 
            background: linear-gradient(135deg, #ff6b6b, #ff4757);
        }
        to { 
            background: linear-gradient(135deg, #ff0000, #ff6b6b);
        }
    }
    
    /* Hide the actual Streamlit button */
    .stButton button[key="panic_btn"] {
        display: none !important;
    }
    
    /* Enhanced Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-top: 1rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(118, 75, 162, 0.25));
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.35), rgba(118, 75, 162, 0.35));
    }
    
    .stat-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #ffeb3b;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    .stat-change {
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .change-positive {
        color: #4CAF50;
    }
    
    .change-neutral {
        color: #ffeb3b;
    }
    
    /* Dashboard Container */
    .dashboard-container {
        margin: 2rem 0;
    }
    
    .dashboard-title {
        color: #ffeb3b;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
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

    /* Fix for Streamlit elements */
    .stButton button {
        width: 100%;
    }
    
    /* Ensure proper text contrast */
    .stMarkdown {
        color: white !important;
    }
    
    /* Fix for form elements */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stSelectbox select {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
    }
    
    /* Fix progress bar */
    .stProgress > div > div > div {
        background-color: #ffeb3b !important;
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
            
            // Random properties with more variation
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
    
    // Smooth scroll and transition enhancements
    document.addEventListener('DOMContentLoaded', function() {
        // Add smooth fade-in for all content
        const elements = document.querySelectorAll('.stat-card');
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

# ---- Enhanced Session State ----
if "registered_users" not in st.session_state:
    # Initialize with ONLY admin account - no demo users
    st.session_state.registered_users = {
        "admin": {
            "password": "admin123",
            "name": "System Administrator",
            "email": "admin@safetap.com",
            "phone": "+63 900 000 0000",
            "id": "ADMIN001",
            "authority": "Administrator",
            "role": "admin",
            "created_at": "2024-01-01",
            "profile_pic": None,
            "status": "active",
            "last_login": "2024-01-01 00:00:00"
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
    st.session_state.location = {"lat": 14.5995, "lng": 120.9842, "accuracy": 50}
if "history" not in st.session_state:
    st.session_state.history = []
if "contacts" not in st.session_state:
    st.session_state.contacts = [
        {"name": "Emergency Services", "number": "911", "type": "emergency", "icon": "🚨", "priority": 1},
        {"name": "Family Contact", "number": "+63 912 345 6792", "type": "family", "icon": "👨‍👩‍👧‍👦", "priority": 2}
    ]
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

# ---- NEW: Enhanced Emergency Features ----
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
if "battery_level" not in st.session_state:
    st.session_state.battery_level = 85
if "offline_mode" not in st.session_state:
    st.session_state.offline_mode = False

# ---- NEW: Admin Tracking ----
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
        "system_status": "operational"
    }

# ---- Enhanced Emergency Protocols ----
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

# ---- Enhanced Helper Functions ----
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
    event = {
        "username": username,
        "emergency_type": emergency_type,
        "location": location,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.datetime.now().strftime("%B %d, %Y - %H:%M")
    }
    st.session_state.panic_events.insert(0, event)

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
    protocol = EMERGENCY_PROTOCOLS[st.session_state.emergency_type]
    
    # Log the panic event for admin tracking
    if st.session_state.user:
        log_panic_event(st.session_state.user["username"], st.session_state.emergency_type, st.session_state.location)
    
    # Send to appropriate contacts based on emergency type
    contacts_to_notify = []
    if "all" in protocol["contacts"]:
        contacts_to_notify = st.session_state.contacts
    else:
        contacts_to_notify = [c for c in st.session_state.contacts if c["type"] in protocol["contacts"]]
    
    # Add priority contacts
    priority_contacts = [c for c in st.session_state.contacts if c.get("priority", 0) == 1]
    contacts_to_notify.extend(priority_contacts)
    
    # Remove duplicates
    contacts_to_notify = list({c["name"]: c for c in contacts_to_notify}.values())
    
    # Simulate sending alerts
    for contact in contacts_to_notify:
        add_history("alert", f"Alert sent to {contact['name']}", 
                   f"Emergency: {st.session_state.emergency_type}. {protocol['message']}")
    
    # Activate siren if enabled
    if st.session_state.settings.get("sound_alerts", True):
        add_history("alert", "Emergency Siren Activated", "Loud alarm activated to attract attention")
    
    st.success(f"🚨 {protocol['icon']} {protocol['message']} Sent to {len(contacts_to_notify)} contacts!")

def simulate_battery_drain():
    """Simulate battery drain over time"""
    if random.random() < 0.1:  # 10% chance to reduce battery each run
        st.session_state.battery_level = max(5, st.session_state.battery_level - random.randint(1, 5))

def register_user(username, password, name, email, phone, authority="Civilian", role="user"):
    """Register a new user"""
    if username in st.session_state.registered_users:
        return False, "Username already exists"
    
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
        "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return True, "User registered successfully"

def authenticate_user(username, password):
    """Authenticate user credentials"""
    if username in st.session_state.registered_users:
        user_data = st.session_state.registered_users[username]
        if user_data["password"] == password:
            # Update last login
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

# ---- NEW: Admin Functions ----
def get_system_stats():
    """Get comprehensive system statistics for admin dashboard"""
    total_users = len(st.session_state.registered_users)
    active_users = len([u for u in st.session_state.registered_users.values() if u.get("status") == "active"])
    total_emergencies = len(st.session_state.panic_events)
    today_emergencies = len([e for e in st.session_state.panic_events 
                           if e["timestamp"].startswith(datetime.datetime.now().strftime("%Y-%m-%d"))])
    
    # Emergency type distribution
    emergency_types = {}
    for event in st.session_state.panic_events:
        e_type = event["emergency_type"]
        emergency_types[e_type] = emergency_types.get(e_type, 0) + 1
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_emergencies": total_emergencies,
        "today_emergencies": today_emergencies,
        "emergency_types": emergency_types,
        "system_uptime": "99.8%",
        "response_time": "4.2s"
    }

def generate_emergency_analytics():
    """Generate analytics data for emergencies"""
    # Create sample time series data for emergencies
    dates = pd.date_range(start='2024-01-01', end=datetime.datetime.now(), freq='D')
    emergency_data = []
    
    for date in dates:
        # Simulate emergency counts
        count = random.randint(0, 5)
        emergency_data.append({
            "date": date,
            "emergencies": count,
            "type": "daily"
        })
    
    return pd.DataFrame(emergency_data)

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
            "Last Login": user_data.get("last_login", "Never")
        })
    return pd.DataFrame(users_data)

def create_emergency_report():
    """Create a comprehensive emergency report"""
    emergencies_data = []
    for event in st.session_state.panic_events:
        emergencies_data.append({
            "Username": event["username"],
            "Emergency Type": event["emergency_type"],
            "Timestamp": event["timestamp"],
            "Date": event["date"],
            "Latitude": event["location"]["lat"],
            "Longitude": event["location"]["lng"]
        })
    return pd.DataFrame(emergencies_data)

# ---- Enhanced Sidebar with User Info ----
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🛡️ SafeTap</h2>
            <p>One Tap Can Save a Life</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation sections - ONLY admin sections since only admin exists
        if st.session_state.user and st.session_state.user.get("role") == "admin":
            sections = [
                {"icon": "🏠", "name": "Admin Dashboard", "view": "admin_dashboard"},
                {"icon": "👥", "name": "User Management", "view": "user_management"},
                {"icon": "📊", "name": "System Analytics", "view": "system_analytics"},
                {"icon": "⚙️", "name": "System Settings", "view": "system_settings"},
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
        
        # User info if logged in
        if st.session_state.user:
            st.markdown("---")
            
            # User info section in sidebar
            st.markdown("""
            <div class="sidebar-user-info">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0;">👋 Admin Info</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display user information in organized format
            user_info_items = [
                ("Authority", st.session_state.user['authority']),
                ("Status", "🟢 Online & Active"),
                ("Role", "Administrator"),
                ("User ID", st.session_state.user['id'])
            ]
            
            for label, value in user_info_items:
                st.markdown(f"""
                <div class="user-info-item">
                    <span class="user-info-label">{label}</span>
                    <span class="user-info-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
                st.session_state.user = None
                st.session_state.view = "login"
                st.rerun()

# ---- Enhanced Mini Dashboard ----
def show_mini_dashboard():
    # Calculate statistics
    alerts_sent = len([h for h in st.session_state.history if h["type"] == "alert"])
    location_updates = len([h for h in st.session_state.history if h["type"] == "location"])
    contacts_count = len(st.session_state.contacts)
    
    # Create dashboard with proper styling
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
                <div class="stat-change change-positive">+1 today</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📍</div>
                <div class="stat-value">{}</div>
                <div class="stat-label">Location Updates</div>
                <div class="stat-change change-positive">+5 today</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value">{}</div>
                <div class="stat-label">Emergency Contacts</div>
                <div class="stat-change change-neutral">All active</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔋</div>
                <div class="stat-value">{}%</div>
                <div class="stat-label">Battery Level</div>
                <div class="stat-change change-neutral">Optimal</div>
            </div>
        </div>
    </div>
    """.format(alerts_sent, location_updates, contacts_count, st.session_state.battery_level), unsafe_allow_html=True)

# ---- Enhanced Emergency Button Component - Icon Only ----
def create_emergency_button():
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
        # Create only the alert icon (no text button)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Hidden button for functionality
            st.button("", key="panic_btn", on_click=start_panic_timer)
            
            # Custom styled emergency icon only
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

# ---- Clean Main View with Circular Emergency Button ----
def show_main():
    # Check various timers
    if check_panic_timer():
        send_enhanced_emergency_alert()
        st.rerun()
    
    # SafeTap Header
    st.markdown('<div class="safe-header"><h1>🛡️ SafeTap Dashboard</h1><p>Enhanced Emergency Response System</p></div>', unsafe_allow_html=True)
    
    # Simple welcome message
    if st.session_state.user:
        st.write(f"### 👋 Welcome, {st.session_state.user['name']}")
        st.write("Your safety is our priority. Tap the alert icon below in case of emergency.")
        st.write("")  # Add some spacing
    
    # Emergency Alert Icon Section
    create_emergency_button()
    
    # Mini Dashboard
    show_mini_dashboard()

# ---- View Functions ----
def show_profile():
    st.markdown('<div class="safe-header"><h1>👤 User Profile</h1><p>Manage your account information</p></div>', unsafe_allow_html=True)
    
    if st.session_state.user:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Profile Picture")
            
            # Get current profile picture
            current_profile_pic = get_profile_picture(st.session_state.user["username"])
            
            # Display current profile picture if exists
            if current_profile_pic is not None:
                image = Image.open(current_profile_pic)
                st.image(image, caption="Current Profile Picture", width=150)
            else:
                st.info("No profile picture uploaded")
            
            # Profile picture upload
            uploaded_file = st.file_uploader("Upload Profile Picture", type=['jpg', 'png', 'jpeg'], key="profile_pic_uploader")
            if uploaded_file is not None:
                # Save the uploaded file to user data
                if save_profile_picture(st.session_state.user["username"], uploaded_file):
                    st.success("✅ Profile picture saved successfully!")
                    st.rerun()
            
            # Remove profile picture button
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
            
            # Display user info in editable form
            with st.form("profile_form"):
                name = st.text_input("Full Name", value=st.session_state.user.get('name', ''))
                email = st.text_input("Email", value=st.session_state.user.get('email', ''))
                phone = st.text_input("Phone", value=st.session_state.user.get('phone', ''))
                authority = st.text_input("Authority", value=st.session_state.user.get('authority', ''), disabled=True)
                
                if st.form_submit_button("💾 Update Profile"):
                    # Update user information
                    st.session_state.user['name'] = name
                    st.session_state.user['email'] = email
                    st.session_state.user['phone'] = phone
                    st.success("✅ Profile updated successfully!")
        
        # Emergency Contacts Section
        st.subheader("🆘 Emergency Contacts")
        contacts_col1, contacts_col2, contacts_col3 = st.columns(3)
        
        with contacts_col1:
            st.write("**Primary Contacts**")
            for contact in st.session_state.contacts[:2]:
                st.info(f"{contact['icon']} **{contact['name']}**\n\n{contact['number']}")
        
        with contacts_col2:
            st.write("**Secondary Contacts**")
            for contact in st.session_state.contacts[2:]:
                st.info(f"{contact['icon']} **{contact['name']}**\n\n{contact['number']}")
        
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
                    else:
                        st.error("❌ Please fill in all fields")

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
        
        with col2:
            st.write("**Location Services**")
            update_freq = st.selectbox("Update Frequency", ["Real-time", "Every 30s", "Every 1min", "Every 5min"])
            st.info("📍 Location accuracy affects battery life")
    
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
            st.info(f"**Battery Level:** {st.session_state.battery_level}%")
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

def show_history():
    st.markdown('<div class="safe-header"><h1>📚 History</h1><p>View your emergency activity history</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("📝 No history records yet. Your emergency alerts and activities will appear here.")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "Alert", "Location", "System", "Test"])
        with col2:
            date_filter = st.date_input("Filter by Date")
        with col3:
            search_term = st.text_input("Search History")
        
        # Display history items
        for i, event in enumerate(st.session_state.history):
            if filter_type != "All" and event["type"] != filter_type.lower():
                continue
            
            if search_term and search_term.lower() not in event["title"].lower() and search_term.lower() not in event["details"].lower():
                continue
            
            # Create a nice card for each history item
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Determine icon based on event type
                    icon = "📱"
                    if event["type"] == "alert":
                        icon = "🚨"
                    elif event["type"] == "location":
                        icon = "📍"
                    elif event["type"] == "system":
                        icon = "⚙️"
                    elif event["type"] == "test":
                        icon = "🧪"
                    
                    st.write(f"**{icon} {event['title']}**")
                    st.write(event["details"])
                
                with col2:
                    st.write(f"**{event['date']}**")
                    st.caption(event["timestamp"])
                
                st.divider()

def show_location():
    st.markdown('<div class="safe-header"><h1>📍 Location</h1><p>View and manage your location settings</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 Current Location")
        
        # Create a folium map
        m = folium.Map(
            location=[st.session_state.location["lat"], st.session_state.location["lng"]],
            zoom_start=15
        )
        
        # Add marker for current location
        folium.Marker(
            [st.session_state.location["lat"], st.session_state.location["lng"]],
            popup="Your Current Location",
            tooltip="SafeTap User",
            icon=folium.Icon(color="red", icon="user-shield", prefix="fa")
        ).add_to(m)
        
        # Add circle for accuracy
        folium.Circle(
            location=[st.session_state.location["lat"], st.session_state.location["lng"]],
            radius=st.session_state.location["accuracy"],
            popup="Location Accuracy",
            color="red",
            fill=True,
            fillColor="red",
            fillOpacity=0.2
        ).add_to(m)
        
        # Display the map
        folium_static(m, width=700, height=400)
    
    with col2:
        st.subheader("📍 Location Info")
        
        st.info(f"**Latitude:** {st.session_state.location['lat']}")
        st.info(f"**Longitude:** {st.session_state.location['lng']}")
        st.info(f"**Accuracy:** ±{st.session_state.location['accuracy']} meters")
        st.info(f"**Last Updated:** {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        st.subheader("📍 Location Actions")
        
        if st.button("🔄 Update Location", use_container_width=True):
            # Simulate location update
            st.session_state.location = {
                "lat": 14.5995 + random.uniform(-0.01, 0.01),
                "lng": 120.9842 + random.uniform(-0.01, 0.01),
                "accuracy": random.randint(30, 100)
            }
            add_history("location", "Location Updated", "Your location has been refreshed")
            st.success("✅ Location updated successfully!")
            st.rerun()
        
        if st.button("📱 Share Location", use_container_width=True):
            add_history("alert", "Location Shared", "Your current location has been shared with emergency contacts")
            st.success("✅ Location shared with emergency contacts!")
        
        if st.button("📍 Save Location", use_container_width=True):
            add_history("system", "Location Saved", "Current location saved to history")
            st.success("✅ Location saved to history!")

# ---- NEW: Enhanced Admin Functions ----
def show_admin_dashboard():
    st.markdown('<div class="safe-header"><h1>👑 Admin Dashboard</h1><p>System Administration Panel</p></div>', unsafe_allow_html=True)
    
    # Get system statistics
    stats = get_system_stats()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats["total_users"], f"{stats['active_users']} active")
    with col2:
        st.metric("Total Emergencies", stats["total_emergencies"], f"{stats['today_emergencies']} today")
    with col3:
        st.metric("System Uptime", stats["system_uptime"])
    with col4:
        st.metric("Avg Response Time", stats["response_time"])
    
    # Emergency type distribution
    st.subheader("📊 Emergency Type Distribution")
    if stats["emergency_types"]:
        fig = px.pie(
            values=list(stats["emergency_types"].values()),
            names=list(stats["emergency_types"].keys()),
            title="Emergency Types"
        )
        safe_plotly_chart(fig, use_container_width=True)
    else:
        st.info("No emergency data available yet")
    
    # Recent emergency events
    st.subheader("🚨 Recent Emergency Events")
    if st.session_state.panic_events:
        recent_events = st.session_state.panic_events[:10]  # Show last 10 events
        for event in recent_events:
            with st.expander(f"{event['timestamp']} - {event['username']} - {event['emergency_type'].title()}"):
                st.write(f"**Location:** {event['location']['lat']}, {event['location']['lng']}")
                st.write(f"**Date:** {event['date']}")
    else:
        st.info("No emergency events recorded yet")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Reports", use_container_width=True):
            st.session_state.view = "system_analytics"
            st.rerun()
    
    with col2:
        if st.button("👥 User Management", use_container_width=True):
            st.session_state.view = "user_management"
            st.rerun()
    
    with col3:
        if st.button("⚙️ System Settings", use_container_width=True):
            st.session_state.view = "system_settings"
            st.rerun()

def show_user_management():
    st.markdown('<div class="safe-header"><h1>👥 User Management</h1><p>Manage system users and permissions</p></div>', unsafe_allow_html=True)
    
    # User management tabs
    tab1, tab2, tab3 = st.tabs(["👥 View Users", "➕ Add User", "📊 User Reports"])
    
    with tab1:
        st.subheader("User List")
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search users by name, email, or username")
        with col2:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user"])
        
        # Display users in a table
        users_data = []
        for username, user_data in st.session_state.registered_users.items():
            if search_term and search_term.lower() not in username.lower() and search_term.lower() not in user_data['name'].lower() and search_term.lower() not in user_data['email'].lower():
                continue
            if role_filter != "All" and user_data['role'] != role_filter:
                continue
                
            users_data.append({
                "Username": username,
                "Name": user_data['name'],
                "Email": user_data['email'],
                "Role": user_data['role'],
                "Authority": user_data['authority'],
                "Status": user_data.get('status', 'active'),
                "Last Login": user_data.get('last_login', 'Never'),
                "Actions": username
            })
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # User actions
            st.subheader("User Actions")
            selected_user = st.selectbox("Select user to manage", [u["Username"] for u in users_data])
            
            if selected_user:
                user_data = st.session_state.registered_users[selected_user]
                col1, col2, col3 = st.columns(3)
                
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
                new_authority = st.selectbox("Authority", ["Civilian", "Administrator"])
                new_role = st.selectbox("Role", ["user", "admin"])
            
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
                st.dataframe(user_report, use_container_width=True)
                
                # Export option
                csv = user_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download User Report (CSV)",
                    data=csv,
                    file_name=f"user_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 User Statistics", use_container_width=True):
                stats = get_system_stats()
                
                # Create user role distribution
                roles = {}
                for user in st.session_state.registered_users.values():
                    role = user['role']
                    roles[role] = roles.get(role, 0) + 1
                
                if roles:
                    fig = px.pie(
                        values=list(roles.values()),
                        names=list(roles.keys()),
                        title="User Role Distribution"
                    )
                    safe_plotly_chart(fig, use_container_width=True)

def show_system_analytics():
    st.markdown('<div class="safe-header"><h1>📊 System Analytics</h1><p>Comprehensive system performance and usage analytics</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🚨 Emergencies", "💾 Data Management"])
    
    with tab1:
        st.subheader("System Performance Metrics")
        
        # Generate sample performance data
        dates = pd.date_range(start='2024-01-01', end=datetime.datetime.now(), freq='D')
        performance_data = []
        
        for date in dates:
            performance_data.append({
                "date": date,
                "response_time": random.uniform(2.0, 6.0),
                "uptime": random.uniform(98.5, 99.9),
                "active_users": random.randint(50, 150)
            })
        
        df = pd.DataFrame(performance_data)
        
        # Response time chart
        fig1 = px.line(df, x='date', y='response_time', title='Average Response Time (seconds)')
        safe_plotly_chart(fig1, use_container_width=True)
        
        # Uptime chart
        fig2 = px.line(df, x='date', y='uptime', title='System Uptime (%)')
        safe_plotly_chart(fig2, use_container_width=True)
        
        # Active users chart
        fig3 = px.line(df, x='date', y='active_users', title='Daily Active Users')
        safe_plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.subheader("Emergency Analytics")
        
        # Generate emergency analytics
        emergency_df = generate_emergency_analytics()
        
        if not emergency_df.empty:
            # Emergency trends
            fig1 = px.line(emergency_df, x='date', y='emergencies', title='Daily Emergency Alerts')
            safe_plotly_chart(fig1, use_container_width=True)
            
            # Emergency type distribution
            stats = get_system_stats()
            if stats["emergency_types"]:
                fig2 = px.bar(
                    x=list(stats["emergency_types"].keys()),
                    y=list(stats["emergency_types"].values()),
                    title="Emergency Types Distribution"
                )
                safe_plotly_chart(fig2, use_container_width=True)
            
            # Emergency report
            st.subheader("Emergency Report")
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
        
        # System cleanup
        st.subheader("🧹 System Cleanup")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Old History", use_container_width=True):
                # Keep only last 100 history items
                if len(st.session_state.history) > 100:
                    st.session_state.history = st.session_state.history[:100]
                    st.success("✅ Old history cleared")
                else:
                    st.info("No old history to clear")
        
        with col2:
            if st.button("🔄 Reset Demo Data", use_container_width=True):
                # Reset to initial demo data
                st.session_state.panic_events = []
                st.session_state.history = []
                st.success("✅ Demo data reset")

def show_system_settings():
    st.markdown('<div class="safe-header"><h1>⚙️ System Settings</h1><p>Configure system-wide settings and preferences</p></div>', unsafe_allow_html=True)
    
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
            
            default_emergency_message = st.text_area(
                "Default Emergency Message",
                value=st.session_state.settings.get("emergency_message", ""),
                height=100
            )
        
        with col2:
            enable_test_alerts = st.toggle("Enable Test Alerts", value=True)
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
            ip_whitelist = st.text_area("IP Whitelist (one per line)", height=100)
        
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
                    "system_status": "operational"
                }
                st.success("✅ All settings reset to defaults")
        
        with col2:
            if st.button("🚨 Emergency Shutdown", use_container_width=True):
                st.session_state.admin_settings["system_status"] = "offline"
                st.error("🚨 System has been shut down for emergency maintenance")

# ---- Simplified Login View ----
def show_login():
    # Hide sidebar for login page
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="safe-header"><h1>🛡️ SafeTap</h1><p>Enhanced Emergency Response System</p></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        
        # Tab selection for Login/Register
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown('### 🔐 Account Login')
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            # Removed the admin credentials reminder
            
            if st.button("🚀 Sign In", use_container_width=True):
                if username and password:
                    authenticated, user_data = authenticate_user(username, password)
                    if authenticated:
                        # Check if role matches (only admin exists)
                        if user_data.get("role") == "admin":
                            st.session_state.user = user_data
                            st.session_state.user["username"] = username
                            
                            # Set to admin dashboard
                            st.session_state.view = "admin_dashboard"
                            
                            st.success(f"✅ Welcome back, {user_data['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ This account is not authorized as Admin")
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("❌ Please fill in all fields")
        
        with tab2:
            st.markdown('### 📝 Create New Account')
            st.warning("⚠️ New users can only register as regular users. Admin privileges are reserved for system administrators.")
            
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
                
                # All new users are regular users
                role = "user"
                
                if st.form_submit_button("📝 Register Account", use_container_width=True):
                    if all([new_username, new_password, new_name, new_email, new_phone]):
                        if new_password == confirm_password:
                            success, message = register_user(
                                new_username, new_password, new_name, new_email, new_phone, new_authority, role
                            )
                            if success:
                                st.success(f"✅ {message}")
                                # Auto-login after registration
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
# Show sidebar only when user is logged in
if st.session_state.user and st.session_state.view not in ["login", "signup"]:
    show_sidebar()

# View routing
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
elif st.session_state.view == "location":
    show_location()
elif st.session_state.view == "admin_dashboard":
    show_admin_dashboard()
elif st.session_state.view == "user_management":
    show_user_management()
elif st.session_state.view == "system_analytics":
    show_system_analytics()
elif st.session_state.view == "system_settings":
    show_system_settings()
else:
    # Fallback to main view
    st.session_state.view = "main"
    st.rerun()

# ---- Footer ----
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: white; opacity: 0.7;">
        SafeTap &copy; 2024 | Guardian Innovators<br>
        One Tap Can Save a Life | Enhanced Emergency Response System
    </div>
""", unsafe_allow_html=True)
