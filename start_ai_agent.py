#!/usr/bin/env python3
"""
Startup script for the LinkedIn Data Extraction AI Agent
"""

import os
import sys
from web_interface import app

def main():
    """Main function to start the Flask application."""
    print("🚀 Starting LinkedIn Data Extraction AI Agent...")
    print("=" * 50)
    print("AI Agent Features:")
    print("✅ Intelligent MHTML parsing with multiple fallback strategies")
    print("✅ AI-powered GPT-4 parsing option for complex formats")
    print("✅ Data quality scoring and analysis")
    print("✅ Multiple export formats (CSV, JSON)")
    print("✅ Modern web interface with drag & drop")
    print("✅ Secure file processing (local only)")
    print("=" * 50)
    
    # Ensure templates directory exists
    if not os.path.exists('templates'):
        print("❌ Error: 'templates' directory not found!")
        print("Please ensure you're running this from the project root directory.")
        sys.exit(1)
    
    # Ensure uploads directory exists
    os.makedirs('uploads', exist_ok=True)
    
    print("✅ All directories verified")
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 