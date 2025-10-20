#!/usr/bin/env python3
"""
Main entry point for Cloud Run deployment
This file tells Cloud Run how to start the LinkedIn Data Extraction application
"""

import os
from dotenv import load_dotenv
from web_interface import app

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # For local development, run the Flask app
    # For Cloud Run, this file just exports the app
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting LinkedIn Data Extraction AI Agent...")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print(f"⏹️  Press Ctrl+C to stop the server")
    app.run(debug=True, host="0.0.0.0", port=port)
