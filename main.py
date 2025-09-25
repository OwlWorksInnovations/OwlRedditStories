from reddit import scrape_reddit
from format import format_posts
from tts import create_tts
from editor import subtitiles
from upload import upload_video
import asyncio
import json
import random
import os

def tts():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        name = post["name"]
        uploaded_status = post.get("uploaded", "false")

        if uploaded_status == "false":
            asyncio.run(create_tts(post["name"], post["tts_content"]))
        else:
            print(f"Skipping tts {name}")

def make_video():
    video_files = os.listdir("backgrounds")
    video_files_choice = random.choice(video_files)
    
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        name = post["name"]
        uploaded_status = post.get("uploaded", "false")

        if uploaded_status == "false":
            subtitiles(os.path.basename(video_files_choice), f"tts/{name}.mp3", name, "sounds/sound.mp3")
        else:
            print(f"Skipping creation {name}")

def video_upload():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        name = post["name"]
        title = post["submission_title"]
        uploaded_status = post.get("uploaded", "false")

        if uploaded_status == "false":
            upload_video(f"output/{name}.mp4", title, title, ['AITA', 'AmItheAsshole', 'RedditStories', 'AITATiktok', 'Reddit', 'r/AmItheAsshole', 'StoryTime', 'RelationshipAdvice', 'FamilyDrama', 'DatingAdvice', 'Friendship', 'Workplace', 'Tifu', 'UnpopularOpinion', 'YouTubeShorts', 'Shorts', 'ShortStory', 'Viral', 'Trending'])
            post["uploaded"] = "true"
        else:
            print(f"Skipping {name} upload")

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=3)

if __name__ == "__main__":
    scrape_reddit(10)
    format_posts()
    tts()
    make_video()
    video_upload()
    