#!/usr/bin/env python3
"""
Invoice Verifier Startup Script
Run this to start the invoice verification web application
"""

import uvicorn
import os
import sys

def main():
    """Start the Invoice Verifier application"""
    
    # Configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("🚀 Starting Invoice Verifier...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"🌐 URL: http://{host}:{port}")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Invoice Verifier stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
