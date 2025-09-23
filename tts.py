import asyncio
import edge_tts

async def edgetts(title, text):
    communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural", rate="+5%")
    print(f"[+] Starting TTS for: {title}")
    await communicate.save(f"tts/{title}.mp3")
    print(f"[+] TTS done for: {title}")