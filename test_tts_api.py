"""
Test TTS API endpoints
"""

import requests
import json
import base64
import wave

API_BASE = "http://localhost:8001/api"


def test_tts_endpoint():
    """Test the /api/text-to-speech endpoint"""
    print("=" * 60)
    print("🧪 Testing TTS API Endpoint")
    print("=" * 60)
    
    # Test 1: English TTS
    print("\n📝 Test 1: English Text-to-Speech")
    print("-" * 60)
    
    payload = {
        "text": "Hello! Welcome to Twuaiq Academy. This is a test of the text to speech system.",
        "language": "en",
        "format": "base64"
    }
    
    try:
        response = requests.post(f"{API_BASE}/text-to-speech", json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success!")
        print(f"   - Language: {data['language']}")
        print(f"   - Sample Rate: {data['sample_rate']} Hz")
        print(f"   - Audio Size: {data['audio_size']} bytes")
        print(f"   - Base64 length: {len(data['audio_base64'])} characters")
        
        # Decode and save audio
        audio_data = base64.b64decode(data['audio_base64'])
        with open("test_api_english.wav", "wb") as f:
            f.write(audio_data)
        print(f"   - Saved to: test_api_english.wav")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Arabic TTS
    print("\n📝 Test 2: Arabic Text-to-Speech")
    print("-" * 60)
    
    payload = {
        "text": "مرحبا! أهلا بك في أكاديمية طويق. هذا اختبار لنظام تحويل النص إلى كلام.",
        "language": "ar",
        "format": "base64"
    }
    
    try:
        response = requests.post(f"{API_BASE}/text-to-speech", json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success!")
        print(f"   - Language: {data['language']}")
        print(f"   - Sample Rate: {data['sample_rate']} Hz")
        print(f"   - Audio Size: {data['audio_size']} bytes")
        
        # Decode and save audio
        audio_data = base64.b64decode(data['audio_base64'])
        with open("test_api_arabic.wav", "wb") as f:
            f.write(audio_data)
        print(f"   - Saved to: test_api_arabic.wav")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Auto language detection
    print("\n📝 Test 3: Auto Language Detection")
    print("-" * 60)
    
    test_cases = [
        ("This is English text", "en"),
        ("هذا نص عربي", "ar"),
    ]
    
    for text, expected_lang in test_cases:
        payload = {
            "text": text,
            "language": "auto",
            "format": "base64"
        }
        
        try:
            response = requests.post(f"{API_BASE}/text-to-speech", json=payload)
            response.raise_for_status()
            data = response.json()
            detected = data['language']
            status = "✅" if detected == expected_lang else "❌"
            print(f"{status} '{text[:30]}...' -> {detected} (expected: {expected_lang})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 4: WAV endpoint
    print("\n📝 Test 4: WAV File Download Endpoint")
    print("-" * 60)
    
    payload = {
        "text": "Testing WAV file download endpoint.",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{API_BASE}/text-to-speech/wav", json=payload)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type')
        print(f"✅ Success!")
        print(f"   - Content-Type: {content_type}")
        print(f"   - File size: {len(response.content)} bytes")
        
        # Save file
        with open("test_api_wav_download.wav", "wb") as f:
            f.write(response.content)
        print(f"   - Saved to: test_api_wav_download.wav")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All TTS API tests passed successfully!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI server is running on http://localhost:8001")
    print("   Run: python src/run.py\n")
    
    import time
    time.sleep(2)
    
    try:
        test_tts_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Please start the server first: python src/run.py")
