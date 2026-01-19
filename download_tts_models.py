"""
Download Piper TTS models for English and Arabic
"""

import os
import urllib.request
import tarfile
from pathlib import Path


MODELS_DIR = Path("./models/piper")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Model download URLs from Hugging Face
MODELS = {
    "en_US-lessac-medium": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
        "description": "English (US) - Lessac - Medium quality"
    },
    "ar_JO-kareem-medium": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx",
        "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json",
        "description": "Arabic (Jordan) - Kareem - Medium quality"
    }
}


def download_model(model_name: str, model_info: dict):
    """Download and extract a Piper model"""
    
    model_dir = MODELS_DIR / model_name
    
    # Convert model name to lowercase with hyphens for filenames
    model_filename = model_name.replace("_", "-").lower()
    model_file = model_dir / f"{model_filename}.onnx"
    config_file = model_dir / f"{model_filename}.onnx.json"
    
    # Check if already downloaded
    if model_file.exists() and config_file.exists():
        print(f"✅ {model_name} already downloaded")
        return
    
    print(f"📥 Downloading {model_name}...")
    print(f"   Description: {model_info['description']}")
    
    # Create model directory
    model_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download ONNX model file
        print(f"   Downloading model file...")
        urllib.request.urlretrieve(model_info['url'], model_file)
        print(f"   ✓ Model file downloaded: {model_file.name}")
        
        # Download JSON config file
        print(f"   Downloading config file...")
        urllib.request.urlretrieve(model_info['config_url'], config_file)
        print(f"   ✓ Config file downloaded: {config_file.name}")
        
        # Verify files exist
        if model_file.exists() and config_file.exists():
            print(f"✅ {model_name} installed successfully")
            print(f"   Model size: {model_file.stat().st_size / (1024*1024):.1f} MB")
        else:
            print(f"⚠️  Warning: Expected files not found after download")
            
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        # Clean up on error
        if model_file.exists():
            model_file.unlink()
        if config_file.exists():
            config_file.unlink()


def main():
    """Download all required models"""
    print("=" * 60)
    print("🔊 Piper TTS Model Downloader")
    print("=" * 60)
    print(f"Models directory: {MODELS_DIR.absolute()}")
    print()
    
    for model_name, model_info in MODELS.items():
        download_model(model_name, model_info)
        print()
    
    print("=" * 60)
    print("✅ Model download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
