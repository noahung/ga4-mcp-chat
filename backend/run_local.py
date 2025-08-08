#!/usr/bin/env python3
"""
Helper script to run the GA4 MCP Chat backend locally
"""

import os
import argparse
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("Error: Required dependencies not found.")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False
    return True

def check_mcp():
    """Check if Google Analytics MCP is installed"""
    try:
        result = subprocess.run(
            ["google-analytics-mcp", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Warning: google-analytics-mcp command returned an error.")
            print(result.stderr)
            return False
        print(f"Found Google Analytics MCP: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("Warning: google-analytics-mcp command not found.")
        print("Please install it with: pip install google-analytics-mcp")
        return False

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("No .env file found. Creating from .env.example...")
            with open(env_example, "r") as example:
                with open(env_file, "w") as env:
                    env.write(example.read())
            print(".env file created. Please edit it with your settings.")
        else:
            print("Warning: No .env or .env.example file found.")
            print("Using default environment variables.")
    
    # Set development environment
    os.environ["ENVIRONMENT"] = "development"
    
    # Load .env file if it exists
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                os.environ[key] = value

def main():
    parser = argparse.ArgumentParser(description="Run GA4 MCP Chat backend locally")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
    
    check_mcp()
    load_env()
    
    print(f"\nStarting GA4 MCP Chat backend on http://{args.host}:{args.port}")
    print(f"Password: {os.environ.get('CHAT_PASSWORD', 'changeme')}")
    print("Press Ctrl+C to stop the server\n")
    
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    main()