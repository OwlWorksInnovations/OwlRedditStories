import asyncio
import edge_tts
import os

async def create_tts(title, text):
    os.makedirs('tts', exist_ok=True)
    communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural", rate="+5%")
    print(f"[+] Starting TTS for: {title}")
    await communicate.save(f"tts/{title}.mp3")
    print(f"[+] TTS done for: {title}")