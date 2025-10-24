"""
Marketing and social media tools for the Marketing Agent
"""
from langchain_core.tools import tool
from datetime import datetime
import shutil
import os


@tool
def get_latest_music() -> str:
    """Gets the latest generated music file path.
    
    Returns:
        Path to the most recent music file
    """
    print("Finding latest music...")
    music_dir = "generated_music"
    
    if not os.path.exists(music_dir):
        return "No music directory found. Generate music first."
    
    files = [f for f in os.listdir(music_dir) if f.endswith('.mp3') and '_sample_' not in f]
    
    if not files:
        return "No music files found. Generate music first."
    
    files.sort(reverse=True)
    latest_file = os.path.join(music_dir, files[0])
    
    return f"Latest music file: {latest_file}"


@tool
def create_music_sample(music_file: str, duration: int = 30) -> str:
    """Creates preview sample from a music file.
    
    Args:
        music_file: Path to the music file
        duration: Sample duration in seconds (default: 30)
    
    Returns:
        Path to the sample file
    """
    print("Creating sample...")
    
    if not os.path.exists(music_file):
        return f"Music file not found: {music_file}"
    
    sample_path = music_file.replace('.mp3', f'_sample_{duration}s.mp3')
    
    # Simulate sample creation (in real app, use audio processing)
    shutil.copy(music_file, sample_path)
    
    return f"Sample created: {sample_path} ({duration} seconds)"


@tool
def post_to_social_media(music_file: str, caption: str, platform: str = "all") -> str:
    """Posts music to social media platforms.
    
    Args:
        music_file: Path to the music file or sample
        caption: Engaging caption for the post
        platform: Target platform (default: "all" for all platforms)
    
    Returns:
        Confirmation of post with details
    """
    print("Posting to social media...")
    
    if not os.path.exists(music_file):
        return f"Music file not found: {music_file}"
    
    platforms = ["Twitter", "Instagram", "Facebook"] if platform == "all" else [platform]
    now = datetime.now()
    post_id = f"POST_{now.strftime('%Y%m%d%H%M%S')}"
    
    return f"Posted to {', '.join(platforms)}!\n- File: {music_file}\n- Caption: {caption}\n- Post ID: {post_id}\n- Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"