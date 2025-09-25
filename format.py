import json
import re


def format_posts():
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    for post in posts:
        content: str = post['submission_post']

        cleaned = re.sub(r"\n", "", content)
        cleaned = cleaned.replace('(', '').replace(')', '')
        matches = re.findall(r'\d+[fm]', cleaned, re.IGNORECASE)
        for match in matches:
            if match[-1].lower() == 'f':
                # :-1 keeps the orginal except the last one
                replacement = match[:-1] + ' female'
            else:
                replacement = match[:-1] + ' male'

            cleaned = cleaned.replace(match, replacement)
                    
        matches2 = re.findall(r'(^|\s)([fm])(\s|$)', cleaned, re.IGNORECASE)
        for match2 in matches2:
            # match2 is a tuple: (before, letter, after)
            before, letter, after = match2
            
            if letter.lower() == 'f':
                replacement2 = before + ' female' + after
            elif letter.lower() == 'm':
                replacement2 = before + ' male' + after
            
            # Reconstruct the original match to replace
            original_match = before + letter + after
            cleaned = cleaned.replace(original_match, replacement2, 1)
        
        abbr_match = re.findall(r'\bAITA\b', cleaned)
        
        for abbr_matched in abbr_match:
            if abbr_matched:
                abbr_replacement = 'Am I the asshole'
            else:
                continue
            
            cleaned = cleaned.replace(abbr_matched, abbr_replacement)
        post["tts_content"] = cleaned

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=3)
        
        