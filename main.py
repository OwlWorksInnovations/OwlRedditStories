from reddit import scrape_reddit
from format import format_posts
from tts import create_tts
import asyncio
import json

def tts():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        asyncio.run(create_tts(post["name"], post["tts_content"]))

if __name__ == "__main__":
    scrape_reddit(1)
    format_posts()
    tts()