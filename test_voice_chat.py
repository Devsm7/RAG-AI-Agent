"""
Test voice-chat endpoint with TTS integration
"""

import requests
import base64
import wave
import struct

def create_test_audio(text="Hello", duration_seconds=2, filename="test_voice.wav"):
    """Create a simple test WAV file (silence)"""
    sample_rate = 16000
    num_samples = sample_rate * duration_seconds
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write silence (zeros)
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack('<h', 0))
    
    return filename

def test_voice_chat():
    """Test the /api/voice-chat endpoint"""
    print("=" * 60)
    print("🧪 Testing Voice Chat with TTS")
    print("=" * 60)
    
    # Create a test audio file
    print("\n📝 Creating test audio file...")
    audio_file = create_test_audio()
    print(f"✅ Created: {audio_file}")
    
    # Test voice chat endpoint
    print("\n📝 Testing /api/voice-chat endpoint...")
    print("-" * 60)
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            data = {'session_id': 'test_session'}
            
            response = requests.post(
                'http://localhost:8001/api/voice-chat',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success!")
            print(f"\n📊 Response Details:")
            print(f"   - Transcription: {result.get('transcription', 'N/A')}")
            print(f"   - Response Text: {result.get('response', 'N/A')[:100]}...")
            print(f"   - Detected Language: {result.get('detected_language', 'N/A')}")
            print(f"   - TTS Language: {result.get('tts_language', 'N/A')}")
            print(f"   - Sample Rate: {result.get('sample_rate', 'N/A')} Hz")
            print(f"   - Session ID: {result.get('session_id', 'N/A')}")
            
            # Check if audio is present
            if 'audio_base64' in result:
                audio_size = len(result['audio_base64'])
                print(f"   - Audio Base64 Length: {audio_size} characters")
                
                # Decode and save audio
                audio_data = base64.b64decode(result['audio_base64'])
                output_file = "voice_chat_response.wav"
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                print(f"   - Saved TTS audio to: {output_file}")
                print(f"   - Audio size: {len(audio_data)} bytes")
            else:
                print(f"   ⚠️  No audio in response")
            
            print("\n✅ Voice chat with TTS is working!")
            return True
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI server is running on http://localhost:8001")
    print("   The server should have been reloaded with the fix.\n")
    
    import time
    time.sleep(2)
    
    try:
        success = test_voice_chat()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ All voice chat tests passed!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ Voice chat test failed")
            print("=" * 60)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Please make sure the server is running: python src/run.py")
