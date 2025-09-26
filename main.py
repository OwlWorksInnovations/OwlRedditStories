from reddit import scrape_reddit
from format import format_posts
from tts import create_tts
from editor import subtitiles
from upload import upload_video
import asyncio
import json
import random
import os
import glob
from googleapiclient.errors import ResumableUploadError 

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
    
    if not video_files:
        print("ERROR: 'backgrounds' directory is empty. Cannot create video.")
        video_files_choice = None
    else:
        video_files_choice = random.choice(video_files)
    
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        name = post["name"]
        uploaded_status = post.get("uploaded", "false")

        if "uploaded_parts" not in post:
            post["uploaded_parts"] = []
            
        if uploaded_status == "false":
            if video_files_choice is not None:
                print(f"Creating video and subtitles for: {name}")
                subtitiles(os.path.basename(video_files_choice), f"tts/{name}.mp3", name, "sounds/sound.mp3")
                
                directory = "segments"
                pattern = os.path.join(directory, f"{name}-*.mp4")
                matching_files = glob.glob(pattern)
                normalized_files = [p.replace('\\', '/') for p in matching_files]

                post["parts"] = normalized_files
            else:
                print(f"Skipping creation {name} - No background video selected.")
        else:
            print(f"Skipping creation {name}")
            
            directory = "segments"
            pattern = os.path.join(directory, f"{name}-*.mp4")
            matching_files = glob.glob(pattern)
            normalized_files = [p.replace('\\', '/') for p in matching_files]
            post["parts"] = normalized_files

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=3)

def clean_media(post):
    name = post["name"]

    for part_file_path in post["parts"]:
        if os.path.exists(part_file_path):
            os.remove(part_file_path)

    tts_path = f"tts/{name}.mp3"

    if os.path.exists(tts_path):
        os.remove(tts_path)
    
    parts = []

def video_upload():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    should_stop_upload = False 
    
    for post in posts:
        if should_stop_upload:
            break
            
        name = post["name"]
        title = post["submission_title"]
        uploaded_status = post.get("uploaded", "false")
        parts = post["parts"]
        uploaded_parts = post.get("uploaded_parts", [])

        if uploaded_status == "false":
            if not parts:
                print(f"Skipping upload for {name}: No video parts found.")
                continue

            print(f"Starting upload for post: {name} (Total parts: {len(parts)}, Already uploaded: {len(uploaded_parts)})")
            
            post_upload_successful = True
            
            for idx, part_file_path in enumerate(parts, start=1):
                part_title = f"{name}-part-{idx:03d}"
                
                if part_file_path in uploaded_parts:
                    print(f"Skipping part {idx}: {part_file_path} (Already uploaded)")
                    continue
                    
                print(f"Uploading part {idx}: {part_file_path}")

                try:
                    upload_video(part_file_path, part_title,title,['AITA', 'AmItheAsshole', 'RedditStories', 'AITATiktok', 'Reddit', 'r/AmItheAsshole', 'StoryTime', 'RelationshipAdvice', 'FamilyDrama', 'DatingAdvice', 'Friendship', 'Workplace', 'Tifu', 'UnpopularOpinion', 'YouTubeShorts', 'Shorts', 'ShortStory', 'Viral', 'Trending'])
                    
                    uploaded_parts.append(part_file_path)
                    post["uploaded_parts"] = uploaded_parts
                    
                    with open("posts.json", "w", encoding="utf-8") as f:
                        json.dump(posts, f, ensure_ascii=False, indent=3)

                except ResumableUploadError as e:
                    if 'uploadLimitExceeded' in str(e):
                        print("\n[CRITICAL ERROR] YouTube Upload Limit Exceeded! Stopping all uploads.")
                        should_stop_upload = True
                        post_upload_successful = False
                        break
                    
                    print(f"\n[ERROR] Upload failed for {part_file_path}: {e}")
                    post_upload_successful = False
                    break

            if post_upload_successful and not should_stop_upload:
                if len(uploaded_parts) == len(parts):
                    post["uploaded"] = "true"
                
        else:
            print(f"Skipping {name} upload (Already uploaded)")
            if len(uploaded_parts) == len(parts) and len(parts) > 0 and len(post["parts"]) > 0:
                clean_media(post)
            
    if not should_stop_upload:
        with open("posts.json", "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=3)

    if should_stop_upload:
        print("Script terminated early due to upload limit.")

if __name__ == "__main__":
    scrape_reddit(1)
    format_posts()
    tts()
    make_video()
    video_upload()