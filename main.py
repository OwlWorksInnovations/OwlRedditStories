from reddit import scrape_reddit
from format import format_text_for_tts, format_reddit_post_for_tts
from tts import edgetts
import json
import os
import asyncio

def scrape_and_format():
    scrape_reddit()
    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        tts_ready_text = format_text_for_tts(post["submission_post"])
        post["tts_content"] = tts_ready_text

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)

async def tts():
    processed = 0
    os.makedirs("tts", exist_ok=True)

    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        processed += 1
        await edgetts(post["name"], post["tts_content"])
        print(f"[?] Saved {processed} tts audios.")

if __name__ == "__main__":
    scrape_and_format()
    asyncio.run(tts())
    
