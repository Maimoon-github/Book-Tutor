#!/usr/bin/env python3
"""
Utility script to check if Ollama is properly installed and 
the required model is available.
"""

import sys
import requests
import argparse
import json
from urllib.parse import urljoin
import time

def check_ollama_status(base_url):
    """Check if Ollama server is running."""
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print(f"❌ Ollama server returned status code {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Could not connect to Ollama server")
        print("   Make sure Ollama is running with: ollama serve")
        return False

def list_available_models(base_url):
    """List all models available in the local Ollama instance."""
    try:
        response = requests.get(urljoin(base_url, "/api/tags"))
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("\nAvailable models:")
                for model in models:
                    print(f"- {model['name']} (Size: {format_size(model.get('size', 0))})")
                return models
            else:
                print("\nNo models found. You need to pull a model using 'ollama pull <model>'")
                return []
        else:
            print(f"❌ Failed to retrieve models (Status code: {response.status_code})")
            return []
    except requests.ConnectionError:
        print("❌ Could not connect to Ollama server")
        return []
    except Exception as e:
        print(f"❌ Error retrieving models: {e}")
        return []

def check_model_availability(base_url, model_name):
    """Check if the specified model is available."""
    models = list_available_models(base_url)
    model_names = [model["name"] for model in models]
    
    if model_name in model_names:
        print(f"\n✅ Model '{model_name}' is available")
        return True
    else:
        print(f"\n❌ Model '{model_name}' is not available")
        print(f"   You can pull it using: ollama pull {model_name}")
        return False

def test_model_inference(base_url, model_name):
    """Test model inference with a simple prompt."""
    print(f"\nTesting inference with model '{model_name}'...")
    
    try:
        start_time = time.time()
        response = requests.post(
            urljoin(base_url, "/api/generate"),
            json={
                "model": model_name,
                "prompt": "Respond with a single sentence: What is the purpose of education?",
                "stream": False
            },
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Model responds in {end_time - start_time:.2f} seconds:")
            print(f"   \"{result.get('response', 'No response')}\"")
            return True
        else:
            print(f"\n❌ Inference failed with status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("\n❌ Inference request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Error during inference: {e}")
        return False

def format_size(size_bytes):
    """Format bytes to a human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

def main():
    parser = argparse.ArgumentParser(description="Check Ollama setup for Book AI Tutor")
    parser.add_argument("--model", default="deepseek-r1:1.5b", help="Model name to check")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama server URL")
    parser.add_argument("--test", action="store_true", help="Test model inference")
    
    args = parser.parse_args()
    
    print("\n=== Ollama Setup Checker for Book AI Tutor ===\n")
    
    # Check if Ollama server is running
    if not check_ollama_status(args.url):
        sys.exit(1)
    
    # Check if the specified model is available
    if not check_model_availability(args.url, args.model):
        sys.exit(1)
    
    # Test model inference if requested
    if args.test and not test_model_inference(args.url, args.model):
        sys.exit(1)
    
    print("\n✅ All checks passed! The Book AI Tutor should work correctly with your Ollama setup.\n")

if __name__ == "__main__":
    main()
