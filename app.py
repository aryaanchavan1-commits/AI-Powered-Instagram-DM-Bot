import streamlit as st
import asyncio
import json
import os
import time
from datetime import datetime
from aryan_core.user_db import UserDatabase
from aryan_core.groq_ai import GroqAI
from aryan_core.login import InstagramLogin
from aryan_core.sendmessage import mesj
import threading
import requests

# Page configuration
st.set_page_config(
    page_title="Instagram DM Bot ....BY Aryan chavan",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, responsive UI
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Dark background for login page */
    .stApp {
        background-color: #1a1a2e;
    }
    
    /* Header styling */
    h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #e0e0e0;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #c0c0c0;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #16213e;
        padding: 0.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        background-color: #0f3460;
        border-radius: 8px;
        border: 1px solid #4CAF50;
        font-weight: 500;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
        border-color: #4CAF50;
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button[kind="primary"] {
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    
    .stButton button[kind="primary"]:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    .stButton button[kind="secondary"] {
        background-color: #16213e;
        color: #ffffff;
        border: 1px solid #4CAF50;
    }
    
    .stButton button[kind="secondary"]:hover {
        background-color: #0f3460;
        border-color: #4CAF50;
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 8px;
        border: 1px solid #4CAF50;
        padding: 0.75rem;
        background-color: #16213e;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Card styling */
    .css-1r6slb0 {
        border: 1px solid #4CAF50;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #16213e;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric styling */
    .css-1xarl3l {
        font-size: 2rem;
        font-weight: 700;
        color: #4CAF50;
    }
    
    .css-1xarl3l + div {
        font-size: 0.9rem;
        color: #c0c0c0;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem;
    }
    
    .stSuccess {
        background-color: #1b4332;
        color: #95d5b2;
    }
    
    .stError {
        background-color: #5c1a1a;
        color: #f8d7da;
    }
    
    .stWarning {
        background-color: #5c4b1a;
        color: #fff3cd;
    }
    
    .stInfo {
        background-color: #1a3a5c;
        color: #d1ecf1;
    }
    
    /* Form styling */
    .stForm {
        border: 1px solid #4CAF50;
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #16213e;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        h2 {
            font-size: 1.25rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 auto;
            min-width: 100px;
            height: 45px;
            padding: 0 10px;
            font-size: 0.9rem;
        }
        
        .css-1r6slb0 {
            padding: 1rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'instagram_logged_in' not in st.session_state:
    st.session_state.instagram_logged_in = False
if 'instagram_auth' not in st.session_state:
    st.session_state.instagram_auth = None
if 'instagram_user_id' not in st.session_state:
    st.session_state.instagram_user_id = None
if 'requires_2fa' not in st.session_state:
    st.session_state.requires_2fa = False
if 'two_factor_identifier' not in st.session_state:
    st.session_state.two_factor_identifier = None
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'bot_thread' not in st.session_state:
    st.session_state.bot_thread = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Initialize databases
user_db = UserDatabase()

# Global bot control
bot_control = {
    "running": False,
    "auth": None,
    "user_id": None,
    "groq_api_key": None,
    "language": "english",
    "default_message": None,
    "group_messages": False,
    "username": None,
    "personal_info": None,
    "assistant_name": "Arcavan",
    "owner_name": None
}

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_users():
    """Get all users with caching"""
    return user_db.get_all_users()

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_user(username):
    """Get a specific user with caching"""
    return user_db.get_user(username)

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_cached_user_history(username, limit=50):
    """Get user history with caching"""
    return user_db.get_user_history(username, limit)

def main():
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        show_dashboard()

def show_auth_page():
    """Show login/register page with clean UI"""
    st.markdown("<h1 style='text-align: center;'>🤖 Instagram DM Bot ..by aryan chavan</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #c0c0c0;'>AI-Powered Instagram Direct Message Automation</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.container():
            st.markdown("### Welcome Back")
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Login", key="login_btn", type="primary"):
                    if login_username and login_password:
                        # Check for admin credentials
                        if login_username == "aryankali1" and login_password == "aryankali1":
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.session_state.is_admin = True
                            st.success("Admin login successful!")
                            st.rerun()
                        else:
                            # Regular user login
                            result = user_db.authenticate_user(login_username, login_password)
                            if result["success"]:
                                st.session_state.logged_in = True
                                st.session_state.username = login_username
                                st.session_state.user_data = result["user"]
                                st.session_state.is_admin = False
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error(result["message"])
                    else:
                        st.error("Please enter username and password")
    
    with tab2:
        with st.container():
            st.markdown("### Create Account")
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_email = st.text_input("Email (optional)", key="reg_email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a password")
            reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", placeholder="Confirm your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Register", key="register_btn", type="primary"):
                    if reg_username and reg_password:
                        if reg_password == reg_confirm_password:
                            result = user_db.create_user(reg_username, reg_password, reg_email)
                            if result["success"]:
                                st.success("Registration successful! Please login.")
                            else:
                                st.error(result["message"])
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.error("Please enter username and password")

def show_dashboard():
    """Show main dashboard with tab-based navigation"""
    # Header with logout button
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state.is_admin:
            st.markdown(f"<h2>👑 Admin Dashboard</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2>Welcome, {st.session_state.username}!</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary"):
            bot_control["running"] = False
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_data = None
            st.session_state.instagram_logged_in = False
            st.session_state.bot_running = False
            st.session_state.is_admin = False
            st.rerun()
    
    st.divider()
    
    if st.session_state.is_admin:
        show_admin_tabs()
    else:
        show_user_tabs()

def show_admin_tabs():
    """Show admin tabs"""
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👥 Users", "⚙️ System"])
    
    with tab1:
        show_admin_dashboard()
    
    with tab2:
        show_user_management()
    
    with tab3:
        show_system_stats()

def show_user_tabs():
    """Show user tabs"""
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard", "🔐 Instagram", "👤 Profile", "🤖 Assistant", "⚙️ Settings", "📜 History", "🎮 Bot"
    ])
    
    with tab1:
        show_dashboard_home()
    
    with tab2:
        show_instagram_login()
    
    with tab3:
        show_personal_info()
    
    with tab4:
        show_assistant_settings()
    
    with tab5:
        show_settings()
    
    with tab6:
        show_history()
    
    with tab7:
        show_bot_control()

def show_admin_dashboard():
    """Show admin dashboard"""
    col1, col2 = st.columns(2)
    
    with col1:
        users = get_cached_users()
        st.metric("Total Users", len(users))
    
    with col2:
        connected_instagram = sum(1 for u in users if u.get('instagram_username'))
        st.metric("Connected to Instagram", connected_instagram)
    
    st.markdown("### Recent Users")
    if users:
        for user in users[:5]:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <strong>{user.get('username')}</strong> - {user.get('email', 'No email')}<br>
                <small>Joined: {user.get('created_at', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No users yet")

def show_user_management():
    """Show user management page (admin only)"""
    users = get_cached_users()
    
    if not users:
        st.info("No users registered yet")
        return
    
    st.markdown("### All Users")
    
    for user in users:
        with st.expander(f"👤 {user.get('username')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                st.markdown(f"**Instagram:** {user.get('instagram_username', 'Not connected')}")
                st.markdown(f"**Language:** {user.get('language', 'english')}")
            
            with col2:
                st.markdown(f"**Joined:** {user.get('created_at', 'N/A')}")
                st.markdown(f"**Auto Reply:** {'Enabled' if user.get('auto_reply') else 'Disabled'}")
                st.markdown(f"**Assistant:** {user.get('assistant_name', 'Arcavan')}")
            
            if st.button(f"Delete {user.get('username')}", key=f"delete_{user.get('username')}", type="secondary"):
                result = user_db.delete_user(user.get('username'))
                if result["success"]:
                    st.success(f"User {user.get('username')} deleted")
                    st.rerun()
                else:
                    st.error(result["message"])

def show_system_stats():
    """Show system statistics (admin only)"""
    users = get_cached_users()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### User Statistics")
        st.markdown(f"**Total Users:** {len(users)}")
        connected_instagram = sum(1 for u in users if u.get('instagram_username'))
        st.markdown(f"**Connected to Instagram:** {connected_instagram}")
        auto_reply_enabled = sum(1 for u in users if u.get('auto_reply'))
        st.markdown(f"**Auto Reply Enabled:** {auto_reply_enabled}")
    
    with col2:
        st.markdown("### Bot Statistics")
        st.markdown(f"**Active Bots:** {sum(1 for u in users if u.get('auto_reply'))}")
        st.markdown(f"**Languages Used:** {len(set(u.get('language', 'english') for u in users))}")

def show_dashboard_home():
    """Show dashboard home"""
    user_data = get_cached_user(st.session_state.username)
    col1, col2 = st.columns(2)
    
    with col1:
        status = "Connected" if st.session_state.instagram_logged_in else "Disconnected"
        color = "green" if st.session_state.instagram_logged_in else "red"
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: {color};">{status}</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Instagram</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status = "Running" if bot_control["running"] else "Stopped"
        color = "green" if bot_control["running"] else "orange"
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: {color};">{status}</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Bot Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Recent Activity")
    history = user_db.get_user_history(st.session_state.username, limit=5)
    
    if history:
        for entry in history:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <strong>{entry.get('timestamp', 'N/A')}</strong> - {entry.get('action', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity")

def show_instagram_login():
    """Show Instagram login page"""
    if st.session_state.instagram_logged_in:
        st.success("✅ Instagram account is connected!")
        
        if st.button("Disconnect Instagram", type="secondary"):
            st.session_state.instagram_logged_in = False
            st.session_state.instagram_auth = None
            st.session_state.instagram_user_id = None
            bot_control["auth"] = None
            bot_control["user_id"] = None
            st.rerun()
        
        return
    
    user_data = get_cached_user(st.session_state.username)
    
    with st.form("instagram_login_form"):
        st.markdown("### Enter Instagram Credentials")
        
        ig_username = st.text_input(
            "Instagram Username",
            value=user_data.get("instagram_username", "") if user_data else "",
            placeholder="Enter your Instagram username"
        )
        ig_password = st.text_input(
            "Instagram Password",
            type="password",
            value=user_data.get("instagram_password", "") if user_data else "",
            placeholder="Enter your Instagram password"
        )
        
        # Proxy input (optional)
        proxy = st.text_input(
            "Proxy (optional)",
            placeholder="http://user:pass@host:port or socks5://user:pass@host:port",
            help="Use a proxy to avoid IP-based detection. Leave empty if not using a proxy."
        )
        
        if st.session_state.requires_2fa:
            verification_code = st.text_input("2FA Verification Code", placeholder="Enter 6-digit code")
        else:
            verification_code = None
        
        # CAPTCHA input (optional)
        captcha_response = st.text_input(
            "CAPTCHA Response (optional)",
            placeholder="Enter CAPTCHA response if prompted",
            help="If Instagram shows a CAPTCHA, enter the response here."
        )
        
        submitted = st.form_submit_button("Login to Instagram", type="primary")
        
        if submitted:
            if ig_username and ig_password:
                with st.spinner("Logging in to Instagram..."):
                    login_handler = InstagramLogin(proxy=proxy if proxy else None)
                    result = login_handler.login(ig_username, ig_password, verification_code, captcha_response=captcha_response if captcha_response else None)
                    
                    if result["success"]:
                        st.session_state.instagram_logged_in = True
                        st.session_state.instagram_auth = result["auth_token"]
                        st.session_state.instagram_user_id = result["user_id"]
                        st.session_state.requires_2fa = False
                        
                        bot_control["auth"] = result["auth_token"]
                        bot_control["user_id"] = result["user_id"]
                        
                        user_db.update_instagram_credentials(
                            st.session_state.username,
                            ig_username,
                            ig_password
                        )
                        
                        user_db.add_history_entry(st.session_state.username, {
                            "action": "Instagram login successful",
                            "instagram_username": ig_username
                        })
                        
                        st.success("Instagram login successful!")
                        st.rerun()
                    
                    elif result.get("requires_2fa"):
                        st.session_state.requires_2fa = True
                        st.session_state.two_factor_identifier = result.get("two_factor_identifier")
                        st.warning("2FA required. Please enter the verification code.")
                        st.rerun()
                    
                    elif result.get("requires_challenge"):
                        st.warning("Instagram requires a challenge. Please complete the challenge in your Instagram app.")
                        st.info(f"Challenge URL: {result.get('challenge_url')}")
                        st.info("After completing the challenge, try logging in again.")
                    
                    elif result.get("requires_checkpoint"):
                        st.warning("Instagram requires checkpoint verification. Please verify your account.")
                        st.info(f"Checkpoint URL: {result.get('checkpoint_url')}")
                        st.info("After verifying your account, try logging in again.")
                    
                    elif result.get("requires_email_verification"):
                        st.warning("Instagram requires email verification!")
                        st.info("Please check your email for a verification code.")
                        st.info("After entering the code, try logging in again.")
                        
                        # Show email verification form
                        with st.form("email_verification_form"):
                            st.markdown("### Enter Email Verification Code")
                            email_code = st.text_input("Verification Code", placeholder="Enter the code from your email")
                            verify_submitted = st.form_submit_button("Verify Email", type="primary")
                            
                            if verify_submitted and email_code:
                                with st.spinner("Verifying email..."):
                                    verify_result = login_handler.verify_email(
                                        ig_username,
                                        ig_password,
                                        email_code,
                                        result.get("checkpoint_url"),
                                        result.get("checkpoint_data")
                                    )
                                    
                                    if verify_result["success"]:
                                        st.session_state.instagram_logged_in = True
                                        st.session_state.instagram_auth = verify_result["auth_token"]
                                        st.session_state.instagram_user_id = verify_result["user_id"]
                                        
                                        bot_control["auth"] = verify_result["auth_token"]
                                        bot_control["user_id"] = verify_result["user_id"]
                                        
                                        user_db.update_instagram_credentials(
                                            st.session_state.username,
                                            ig_username,
                                            ig_password
                                        )
                                        
                                        user_db.add_history_entry(st.session_state.username, {
                                            "action": "Instagram email verification successful",
                                            "instagram_username": ig_username
                                        })
                                        
                                        st.success("Email verification successful!")
                                        st.rerun()
                                    else:
                                        st.error(f"Email verification failed: {verify_result.get('message')}")
                    
                    elif result.get("requires_manual_verification"):
                        st.error("Instagram detected suspicious activity!")
                        st.warning(result.get('message'))
                        st.info("Please follow these steps:")
                        st.info("1. Open Instagram on your phone and login manually")
                        st.info("2. Verify your email or phone number if prompted")
                        st.info("3. Wait 24 hours before trying again")
                        st.info("4. Consider using a different IP address or proxy")
                    
                    else:
                        st.error(f"Login failed: {result.get('message')}")
            else:
                st.error("Please enter Instagram credentials")

def show_personal_info():
    """Show personal information page"""
    user_data = get_cached_user(st.session_state.username)
    personal_info = user_data.get("personal_info", {}) if user_data else {}
    
    with st.form("personal_info_form"):
        st.markdown("### Your Personal Details")
        
        full_name = st.text_input(
            "Full Name",
            value=personal_info.get("full_name", "") if personal_info else "",
            placeholder="Enter your full name"
        )
        
        nickname = st.text_input(
            "Nickname",
            value=personal_info.get("nickname", "") if personal_info else "",
            placeholder="Enter your nickname"
        )
        
        bio = st.text_area(
            "Bio / About You",
            value=personal_info.get("bio", "") if personal_info else "",
            placeholder="Tell your followers about yourself"
        )
        
        profession = st.text_input(
            "Profession / Occupation",
            value=personal_info.get("profession", "") if personal_info else "",
            placeholder="Enter your profession"
        )
        
        interests = st.text_input(
            "Interests (comma-separated)",
            value=", ".join(personal_info.get("interests", [])) if personal_info else "",
            placeholder="e.g., photography, travel, technology"
        )
        
        location = st.text_input(
            "Location",
            value=personal_info.get("location", "") if personal_info else "",
            placeholder="Enter your location"
        )
        
        website = st.text_input(
            "Website",
            value=personal_info.get("website", "") if personal_info else "",
            placeholder="Enter your website URL"
        )
        
        contact_email = st.text_input(
            "Contact Email",
            value=personal_info.get("contact_email", "") if personal_info else "",
            placeholder="Enter your contact email"
        )
        
        submitted = st.form_submit_button("Save Personal Info", type="primary")
        
        if submitted:
            interests_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
            
            personal_info_data = {
                "full_name": full_name if full_name else None,
                "nickname": nickname if nickname else None,
                "bio": bio if bio else None,
                "profession": profession if profession else None,
                "interests": interests_list,
                "location": location if location else None,
                "website": website if website else None,
                "contact_email": contact_email if contact_email else None
            }
            
            result = user_db.update_personal_info(st.session_state.username, personal_info_data)
            
            if result["success"]:
                st.session_state.user_data = user_db.get_user(st.session_state.username)
                bot_control["personal_info"] = personal_info_data
                bot_control["owner_name"] = full_name or nickname
                st.success("Personal info saved successfully!")
                user_db.add_history_entry(st.session_state.username, {"action": "Personal info updated"})
            else:
                st.error(result["message"])

def show_assistant_settings():
    """Show assistant customization page"""
    user_data = get_cached_user(st.session_state.username)
    
    with st.form("assistant_settings_form"):
        st.markdown("### Customize Your AI Assistant")
        
        assistant_name = st.text_input(
            "Assistant Name",
            value=user_data.get("assistant_name", "Arcavan") if user_data else "Arcavan",
            placeholder="Choose a name for your AI assistant"
        )
        
        assistant_personality = st.selectbox(
            "Assistant Personality",
            ["friendly", "professional", "casual", "formal", "playful"],
            index=["friendly", "professional", "casual", "formal", "playful"].index(
                user_data.get("assistant_personality", "friendly") if user_data else "friendly"
            )
        )
        
        assistant_greeting = st.text_area(
            "Custom Greeting (optional)",
            value=user_data.get("assistant_greeting", "") if user_data else "",
            placeholder="Leave empty to use default greeting"
        )
        
        submitted = st.form_submit_button("Save Assistant Settings", type="primary")
        
        if submitted:
            result = user_db.update_assistant_settings(
                st.session_state.username,
                assistant_name=assistant_name,
                assistant_personality=assistant_personality,
                assistant_greeting=assistant_greeting if assistant_greeting else None
            )
            
            if result["success"]:
                st.session_state.user_data = user_db.get_user(st.session_state.username)
                bot_control["assistant_name"] = assistant_name
                st.success("Assistant settings saved successfully!")
                user_db.add_history_entry(st.session_state.username, {
                    "action": "Assistant settings updated",
                    "assistant_name": assistant_name
                })
            else:
                st.error(result["message"])

def show_settings():
    """Show settings page"""
    user_data = get_cached_user(st.session_state.username)
    
    with st.form("settings_form"):
        st.markdown("### Groq API Configuration")
        groq_api_key = st.text_input(
            "Groq API Key",
            value=user_data.get("groq_api_key", "") if user_data else "",
            type="password",
            placeholder="Enter your Groq API key"
        )
        
        st.markdown("### Bot Settings")
        language = st.selectbox(
            "Language",
            ["english", "spanish", "french", "german", "italian", "portuguese", "hindi", "chinese", "japanese"],
            index=["english", "spanish", "french", "german", "italian", "portuguese", "hindi", "chinese", "japanese"].index(
                user_data.get("language", "english") if user_data else "english"
            )
        )
        
        default_message = st.text_area(
            "Default Message (leave empty to use AI)",
            value=user_data.get("default_message", "") if user_data else "",
            placeholder="Enter a default message or leave empty for AI replies"
        )
        
        auto_reply = st.checkbox(
            "Enable Auto Reply",
            value=user_data.get("auto_reply", True) if user_data else True
        )
        
        group_messages = st.checkbox(
            "Reply to Group Messages",
            value=user_data.get("group_messages", False) if user_data else False
        )
        
        submitted = st.form_submit_button("Save Settings", type="primary")
        
        if submitted:
            updates = {
                "groq_api_key": groq_api_key,
                "language": language,
                "default_message": default_message if default_message else None,
                "auto_reply": auto_reply,
                "group_messages": group_messages
            }
            
            result = user_db.update_user(st.session_state.username, updates)
            
            if result["success"]:
                st.session_state.user_data = user_db.get_user(st.session_state.username)
                bot_control["groq_api_key"] = groq_api_key
                bot_control["language"] = language
                bot_control["default_message"] = default_message if default_message else None
                bot_control["group_messages"] = group_messages
                st.success("Settings saved successfully!")
                user_db.add_history_entry(st.session_state.username, {"action": "Settings updated"})
            else:
                st.error(result["message"])

def show_history():
    """Show history page"""
    history = get_cached_user_history(st.session_state.username, limit=100)
    
    if not history:
        st.info("No history yet")
        return
    
    for entry in reversed(history):
        with st.expander(f"{entry.get('timestamp', 'N/A')} - {entry.get('action', 'N/A')}"):
            st.json(entry)

def show_bot_control():
    """Show bot control page"""
    if not st.session_state.instagram_logged_in:
        st.warning("Please login to Instagram first")
        return
    
    user_data = get_cached_user(st.session_state.username)
    
    if not user_data.get("groq_api_key"):
        st.warning("Please set your Groq API key in Settings")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start Bot", disabled=bot_control["running"], type="primary"):
            bot_control["running"] = True
            bot_control["auth"] = st.session_state.instagram_auth
            bot_control["user_id"] = st.session_state.instagram_user_id
            bot_control["groq_api_key"] = user_data.get("groq_api_key")
            bot_control["language"] = user_data.get("language", "english")
            bot_control["default_message"] = user_data.get("default_message")
            bot_control["group_messages"] = user_data.get("group_messages", False)
            bot_control["username"] = st.session_state.username
            bot_control["personal_info"] = user_data.get("personal_info")
            bot_control["assistant_name"] = user_data.get("assistant_name", "Arcavan")
            bot_control["owner_name"] = user_data.get("personal_info", {}).get("full_name") or user_data.get("personal_info", {}).get("nickname")
            
            st.session_state.bot_running = True
            st.success("Bot started!")
            user_db.add_history_entry(st.session_state.username, {"action": "Bot started"})
            
            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            st.session_state.bot_thread = thread
    
    with col2:
        if st.button("⏹️ Stop Bot", disabled=not bot_control["running"], type="secondary"):
            bot_control["running"] = False
            st.session_state.bot_running = False
            st.success("Bot stopped!")
            user_db.add_history_entry(st.session_state.username, {"action": "Bot stopped"})
    
    st.divider()
    
    st.markdown("### Bot Status")
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px;">
        <strong>Status:</strong> {'Running' if bot_control['running'] else 'Stopped'}<br>
        <strong>Instagram:</strong> {'Connected' if st.session_state.instagram_logged_in else 'Disconnected'}<br>
        <strong>Auto Reply:</strong> {'Enabled' if user_data.get('auto_reply', True) else 'Disabled'}<br>
        <strong>Language:</strong> {user_data.get('language', 'english')}<br>
        <strong>Group Messages:</strong> {'Enabled' if user_data.get('group_messages', False) else 'Disabled'}<br>
        <strong>Assistant Name:</strong> {user_data.get('assistant_name', 'Arcavan')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Live Bot Logs")
    if bot_control["running"]:
        st.info("Bot is running... Check console for detailed logs.")

def run_bot():
    """Run the bot in background"""
    print("🤖 Bot started!")
    
    try:
        groq_api = GroqAI(api_key=bot_control["groq_api_key"])
        processed_items = {}
        owner_last_activity = {}
        
        # Load device ID from session file
        device_id = "android-a19180f55839e822"  # Default fallback
        try:
            import json
            import os
            if os.path.exists("instagram_session.json"):
                with open("instagram_session.json", 'r') as f:
                    session_data = json.load(f)
                    device_id = session_data.get('device_id', device_id)
        except Exception as e:
            print(f"⚠️ Could not load device ID from session: {e}")
        
        while bot_control["running"]:
            try:
                auth = bot_control["auth"]
                if not auth:
                    print("❌ No auth token available")
                    time.sleep(5)
                    continue
                
                headers = {
                    "Authorization": auth,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Host": "i.instagram.com",
                    "User-Agent": "Instagram 342.0.0.33.103 Android (31/12; 454dpi; 1080x2254; Xiaomi/Redmi; Redmi Note 9 Pro; joyeuse; qcom; tr_TR; 627400398)",
                    "X-IG-App-ID": "567067343352427",
                    "X-IG-Capabilities": "3brTv10=",
                    "X-IG-Connection-Type": "WIFI",
                    "X-IG-Device-ID": device_id,
                    "X-IG-Device-Locale": "en_US",
                    "X-IG-Family-Device-ID": "dummy",
                    "X-IG-Mapped-Locale": "en_US"
                }
                
                response = requests.get(
                    "https://i.instagram.com/api/v1/direct_v2/inbox/",
                    headers=headers,
                    params={"persistentBadging": "true", "use_unified_inbox": "true"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    threads = data.get("inbox", {}).get("threads", [])
                    
                    print(f"📬 Found {len(threads)} threads")
                    
                    for thread in threads:
                        if not bot_control["running"]:
                            break
                        
                        thread_id = thread.get("thread_id")
                        items = thread.get("items", [])
                        is_group = thread.get("is_group", False)
                        
                        if is_group and not bot_control["group_messages"]:
                            continue
                        
                        if items:
                            last_item = items[0]
                            item_id = last_item.get("item_id")
                            text = last_item.get("text", None)
                            sender = last_item.get("user_id", None)
                            
                            if text is None:
                                continue
                            
                            if str(sender) == str(bot_control["user_id"]):
                                print(f"👤 Owner is active in thread {thread_id}, pausing bot for this thread")
                                owner_last_activity[thread_id] = time.time()
                                continue
                            
                            if thread_id in owner_last_activity:
                                time_since_owner = time.time() - owner_last_activity[thread_id]
                                if time_since_owner < 30:
                                    print(f"👤 Owner was recently active in thread {thread_id}, skipping")
                                    continue
                            
                            if thread_id in processed_items and processed_items[thread_id] == item_id:
                                continue
                            
                            print(f"💬 New message from {sender}: {text}")
                            
                            default_msg = bot_control["default_message"]
                            if default_msg:
                                ai_reply = default_msg
                                print(f"📤 Using default message")
                            else:
                                print(f"🤖 Generating AI reply...")
                                emotion = groq_api.detect_emotion(text)
                                print(f"😊 Detected emotion: {emotion}")
                                
                                ai_reply = groq_api.generate_reply(
                                    text,
                                    language=bot_control["language"],
                                    user_context=f"User seems to be feeling: {emotion}",
                                    personal_info=bot_control.get("personal_info"),
                                    assistant_name=bot_control.get("assistant_name", "Arcavan"),
                                    owner_name=bot_control.get("owner_name")
                                )
                                print(f"✅ AI reply generated: {ai_reply[:50]}...")
                            
                            print(f"📤 Sending reply to thread {thread_id}...")
                            try:
                                t = threading.Thread(
                                    target=mesj,
                                    args=(
                                        auth,
                                        str(bot_control["user_id"]),
                                        "android-1",
                                        ai_reply,
                                        [sender],
                                        str(thread_id),
                                        str(item_id)
                                    )
                                )
                                t.start()
                                t.join(timeout=30)
                                print(f"✅ Reply sent successfully")
                            except Exception as e:
                                print(f"❌ Error sending message: {e}")
                            
                            processed_items[thread_id] = item_id
                            
                            user_db.add_history_entry(bot_control["username"], {
                                "action": "Message replied",
                                "thread_id": thread_id,
                                "sender": sender,
                                "user_message": text,
                                "ai_reply": ai_reply
                            })
                
                elif response.status_code == 401:
                    print("❌ Auth token expired or invalid")
                    bot_control["running"] = False
                    break
                
                else:
                    print(f"⚠️ API returned status code: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                
                time.sleep(3)
            
            except requests.exceptions.Timeout:
                print("⚠️ Request timeout, retrying...")
                time.sleep(5)
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(5)
    
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
    
    print("🛑 Bot stopped")

if __name__ == "__main__":
    main()
