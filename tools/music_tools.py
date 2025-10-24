"""
Music generation tools for the Music Agent
"""
from langchain_core.tools import tool
from gradio_client import Client
from datetime import datetime
import shutil
import json
import os


@tool
def generate_music(tags: str, lyrics: str, duration: int = 15) -> str:
    """Generates AI music with custom parameters.
    
    Args:
        tags: Music style descriptors (e.g., "upbeat, cheerful, bright")
        lyrics: Song lyrics in format "[verse]\\nLyrics\\n[chorus]\\nMore lyrics"
        duration: Duration in seconds (default: 15)
    
    Returns:
        Path to generated music file
    """
    print(f"\n{'='*60}")
    print(f"MUSIC GENERATION STARTED")
    print(f"{'='*60}")
    print(f"   Duration: {duration}s")
    print(f"   Tags: {tags[:80]}...")
    print(f"   Lyrics: {lyrics[:80]}...")
    print(f"{'='*60}\n")
    
    try:
        print("Connecting to HuggingFace API...")
        client = Client("ACE-Step/ACE-Step")
        print("Connected successfully")
        
        print("Sending generation request...")
        result = client.predict(
            audio_duration=duration, prompt=tags, lyrics=lyrics,
            infer_step=60, guidance_scale=15, scheduler_type="euler",
            cfg_type="apg", omega_scale=10, manual_seeds=None,
            guidance_interval=0.5, guidance_interval_decay=0,
            min_guidance_scale=3, use_erg_tag=True, use_erg_lyric=False,
            use_erg_diffusion=True, oss_steps=None, guidance_scale_text=0,
            guidance_scale_lyric=0, audio2audio_enable=False,
            ref_audio_strength=0.5, ref_audio_input=None,
            lora_name_or_path="none", api_name="/__call__"
        )
        
        print("Generation completed")
        
        audio_path, metadata = result
        os.makedirs("generated_music", exist_ok=True)
        output_path = f"generated_music/music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        shutil.copy(audio_path, output_path)
        
        print(f"\n{'='*60}")
        print(f"SUCCESS: Music saved to {output_path}")
        print(f"{'='*60}\n")
        
        return f"Music generated successfully: {output_path}"
        
    except Exception as e:
        error_msg = str(e)
        
        print(f"\n{'='*60}")
        print(f"MUSIC GENERATION FAILED")
        print(f"{'='*60}")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {error_msg}")
        print(f"{'='*60}\n")
        
        # Provide user-friendly error messages
        if "quota" in error_msg.lower() or "gpu" in error_msg.lower():
            return f"GPU quota exceeded. The free HuggingFace service is currently at capacity. Please try again in 5-10 minutes or use a shorter duration (5-10 seconds)."
        elif "timeout" in error_msg.lower():
            return f"Request timeout. The service is busy. Please wait a few minutes and try again."
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            return f"Network error. Please check your internet connection and try again."
        else:
            return f"Error generating music: {error_msg[:200]}"


@tool
def get_music_mood_preset(mood: str) -> str:
    """Get preset tags and lyrics for a specific mood.
    
    Args:
        mood: Desired mood (happy, sad, energetic, calm, epic, chill)
    
    Returns:
        JSON string with 'tags' and 'lyrics' for the mood
    """
    presets = {
        "happy": {
            "tags": "upbeat, cheerful, bright, major key, 120 BPM",
            "lyrics": "[verse]\\nFeeling good today\\n[chorus]\\nHappiness all the way"
        },
        "sad": {
            "tags": "melancholic, emotional, slow, minor key, 70 BPM",
            "lyrics": "[verse]\\nQuiet moments here\\n[chorus]\\nFeeling all the tears"
        },
        "energetic": {
            "tags": "fast, powerful, intense, driving, 140 BPM",
            "lyrics": "[verse]\\nFull of energy\\n[chorus]\\nUnstoppable velocity"
        },
        "calm": {
            "tags": "peaceful, ambient, relaxing, meditation, 80 BPM",
            "lyrics": "[verse]\\nCalm and serene\\n[chorus]\\nPeaceful scene"
        },
        "epic": {
            "tags": "cinematic, orchestral, dramatic, powerful, 110 BPM",
            "lyrics": "[verse]\\nRising to the heights\\n[chorus]\\nEpic in our sights"
        },
        "chill": {
            "tags": "lo-fi, relaxed, smooth, laid-back, 90 BPM",
            "lyrics": "[verse]\\nTaking it easy\\n[chorus]\\nFeeling breezy"
        }
    }
    
    mood = mood.lower()
    if mood in presets:
        return json.dumps(presets[mood])
    else:
        return json.dumps({"error": f"Unknown mood: {mood}. Available: {', '.join(presets.keys())}"})