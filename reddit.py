import praw
import json
import os
from dotenv import load_dotenv

def scrape_reddit(target_count):
    load_dotenv()

    reddit = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT"),
    )

    old_posts = []
    if os.path.exists("posts.json"):
        try:
            with open("posts.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    old_posts = json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            old_posts = []

    existing_ids = {post.get("id") for post in old_posts}

    new_posts = []
    processed = 0
    for submission in reddit.subreddit("AmItheAsshole").hot(limit=100):
        processed += 1
        if submission.id in existing_ids:
            print(f"[?] Skipping duplicate {submission.title}.")
            continue

        if not submission.author:
            continue

        if submission.author in ("AutoModerator", "AITAMod"):
            print(f"[?] Skipping AITAMod and AutoModerator.")
            continue

        post_data = {
            "id": submission.id,
            "name": submission.author.name,
            "submission_title": submission.title,
            "submission_post": submission.selftext,
        }

        new_posts.append(post_data)
        print(f"[+] Added new post: {submission.title}")

        if len(new_posts) >= target_count:
            break

    all_posts = old_posts + new_posts

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"[?] Saved {len(new_posts)} new posts. Total now: {len(all_posts)}. Proccesed: {processed}")
