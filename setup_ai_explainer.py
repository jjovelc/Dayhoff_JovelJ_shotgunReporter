#!/usr/bin/env python3
"""
Setup script for AI Microbiome Plot Explainer
Helps users get started with the system
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ollama():
    """Check if Ollama is available"""
    print("\n🔍 Checking for Ollama...")
    try:
        # Try to run ollama --version
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found in PATH")
        return False

def install_ollama():
    """Provide instructions for installing Ollama"""
    print("\n📥 Ollama Installation Instructions:")
    print("=" * 50)
    
    if sys.platform == "darwin":  # macOS
        print("For macOS:")
        print("1. Visit: https://ollama.ai/download")
        print("2. Download and install the macOS app")
        print("3. Or use Homebrew: brew install ollama")
        
    elif sys.platform.startswith("linux"):
        print("For Linux:")
        print("1. Run: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Or visit: https://ollama.ai/download")
        
    elif sys.platform == "win32":  # Windows
        print("For Windows:")
        print("1. Visit: https://ollama.ai/download")
        print("2. Download and install the Windows installer")
    
    print("\nAfter installation:")
    print("1. Start Ollama: ollama serve")
    print("2. Pull the model: ollama pull gpt-oss:20b")
    print("3. Run the AI explainer: python ai_plot_explainer.py")

def pull_model():
    """Pull the required AI model"""
    print("\n🤖 Pulling AI model (this may take a while)...")
    try:
        subprocess.check_call(["ollama", "pull", "gpt-oss:20b"])
        print("✅ Model downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download model: {e}")
        return False

def main():
    """Main setup function"""
    print("🧬 AI Microbiome Plot Explainer Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install Python dependencies
    if not install_requirements():
        return
    
    # Check Ollama
    if not check_ollama():
        install_ollama()
        return
    
    # Try to pull the model
    print("\n🤖 Checking if AI model is available...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "gpt-oss:20b" in result.stdout:
            print("✅ AI model already available")
        else:
            print("📥 AI model not found, downloading...")
            if not pull_model():
                return
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return
    
    print("\n🎉 Setup complete!")
    print("\nTo use the AI explainer:")
    print("1. Ensure Ollama is running: ollama serve")
    print("2. Run: python ai_plot_explainer.py")
    print("\nThe system will:")
    print("- Scan for microbiome plots in the current directory")
    print("- Generate AI explanations for each plot")
    print("- Create an HTML report with explanations")
    print("- Save explanations to JSON format")

if __name__ == "__main__":
    main()
