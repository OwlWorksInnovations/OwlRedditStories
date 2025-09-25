import asyncio
import edge_tts
import os
import json

async def create_tts(title, text):
    os.makedirs('tts', exist_ok=True)
    communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural", rate="+5%")
    print(f"[+] Starting TTS for: {title}")
    await communicate.save(f"tts/{title}.mp3")

    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        post["tts"] = 'true'

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=3)

    print(f"[+] TTS done for: {title}")