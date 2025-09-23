import json

def format_post():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    for post in posts:
        content = post["submission_post"]
