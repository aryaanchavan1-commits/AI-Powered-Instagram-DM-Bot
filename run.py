#!/usr/bin/env python3
"""
Startup script for Instagram DM Bot
Run this file to start the Streamlit application
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import streamlit
        import requests
        import aiohttp
        import Cryptodome
        import groq
        import bcrypt
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found")
        print("Please create .env file with your GROQ_API_KEY")
        print("See .env.example for reference")
        return False
    print("✅ .env file found")
    return True

def main():
    print("=" * 50)
    print("🤖 AI-Powered Instagram DM Bot by aryan chavan")
    print("=" * 50)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check .env file
    if not check_env_file():
        print("\nYou can still run the app and set API key in Settings")
    
    print()
    print("Starting Streamlit application...")
    print("The app will open in your browser at http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 50)
    
    # Run Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
