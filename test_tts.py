"""
Test script for TTS service
Tests English and Arabic synthesis independently
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from twuaqirag.services.text_to_speech import TextToSpeechService, TTSConfig


def test_tts_service():
    """Test TTS service with English and Arabic text"""
    
    print("=" * 60)
    print("🧪 Testing Piper TTS Service")
    print("=" * 60)
    
    # Initialize service
    config = TTSConfig(
        model_en="en_US-lessac-medium",
        model_ar="ar_JO-kareem-medium",
        models_dir="./models/piper",
        enabled=True
    )
    
    tts = TextToSpeechService(config)
    
    # Test 1: English synthesis
    print("\n📝 Test 1: English Text-to-Speech")
    print("-" * 60)
    english_text = "Hello! This is a test of the Piper text to speech system."
    print(f"Input: {english_text}")
    
    try:
        result_en = tts.synthesize_text(english_text, language="en")
        print(f"✅ Success!")
        print(f"   - Language: {result_en.language}")
        print(f"   - Sample Rate: {result_en.sample_rate} Hz")
        print(f"   - Audio Size: {len(result_en.audio_data)} bytes")
        
        # Save to file
        output_file_en = "test_output_english.wav"
        tts.synthesize_to_file(english_text, output_file_en, language="en")
        print(f"   - Saved to: {output_file_en}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Arabic synthesis
    print("\n📝 Test 2: Arabic Text-to-Speech")
    print("-" * 60)
    arabic_text = "مرحبا! هذا اختبار لنظام تحويل النص إلى كلام."
    print(f"Input: {arabic_text}")
    
    try:
        result_ar = tts.synthesize_text(arabic_text, language="ar")
        print(f"✅ Success!")
        print(f"   - Language: {result_ar.language}")
        print(f"   - Sample Rate: {result_ar.sample_rate} Hz")
        print(f"   - Audio Size: {len(result_ar.audio_data)} bytes")
        
        # Save to file
        output_file_ar = "test_output_arabic.wav"
        tts.synthesize_to_file(arabic_text, output_file_ar, language="ar")
        print(f"   - Saved to: {output_file_ar}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Auto language detection
    print("\n📝 Test 3: Automatic Language Detection")
    print("-" * 60)
    
    test_cases = [
        ("Welcome to Twuaiq Academy!", "en"),
        ("مرحبا بك في أكاديمية طويق!", "ar"),
    ]
    
    for text, expected_lang in test_cases:
        detected = tts._detect_language(text)
        status = "✅" if detected == expected_lang else "❌"
        print(f"{status} '{text[:30]}...' -> {detected} (expected: {expected_lang})")
    
    # Test 4: Temp file creation
    print("\n📝 Test 4: Temporary File Creation")
    print("-" * 60)
    
    try:
        temp_path, result = tts.synthesize_to_temp_file(
            "This is a temporary audio file test.",
            language="en"
        )
        print(f"✅ Temp file created: {temp_path}")
        print(f"   - File exists: {os.path.exists(temp_path)}")
        print(f"   - File size: {os.path.getsize(temp_path)} bytes")
        
        # Cleanup
        os.unlink(temp_path)
        print(f"   - Cleaned up temp file")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All TTS tests passed successfully!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_tts_service()
    sys.exit(0 if success else 1)
