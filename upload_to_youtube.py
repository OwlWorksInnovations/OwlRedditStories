import os
import re
import glob
import json
from typing import Dict, List, Optional

# Google/YouTube API imports
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ------------------------
# Configuration
# ------------------------
# Required scope to upload videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Directory where your generated videos live
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# Which files to upload (default: only Shorts parts with new naming convention)
UPLOAD_GLOB = os.getenv("UPLOAD_GLOB", os.path.join(OUTPUT_DIR, "*_pt*.mp4"))

# OAuth client secret JSON file path (download from Google Cloud Console)
# Example: set YT_CLIENT_SECRETS_FILE=C:\\path\\to\\client_secret_XXXXXXXX.json
CLIENT_SECRETS_FILE = os.getenv("YT_CLIENT_SECRETS_FILE", os.path.join(os.getcwd(), "client_secret.json"))

# Where to store OAuth token for subsequent runs
TOKEN_FILE = os.getenv("YT_TOKEN_FILE", os.path.join(os.getcwd(), "token.json"))

# Default privacy status for uploads: "private", "unlisted", or "public"
PRIVACY_STATUS = os.getenv("YT_PRIVACY_STATUS", "public")

# Video categoryId (22 = People & Blogs is a safe default)
CATEGORY_ID = os.getenv("YT_CATEGORY_ID", "22")

# Tags and hashtags
TAGS = ["redditstories", "reddit", "aita"]  # API tags (no # needed)
HASHTAGS_LINE = "#redditstories #reddit #aita"

# Optional: path to a posts.json (if available) to map author names -> post titles
POSTS_JSON_PATH = os.getenv("POSTS_JSON_PATH", os.path.join(os.getcwd(), "posts.json"))

# Create an ".uploaded" sidecar after successful upload to avoid duplicates
CREATE_UPLOADED_MARKER = True


# ------------------------
# Helpers
# ------------------------

def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def load_title_map(posts_json_path: str) -> Dict[str, str]:
    """Load a mapping from safe author name -> post_title from posts.json if present.

    Expected structure of posts.json: a list of objects with keys:
      - name
      - post_title
    """
    mapping: Dict[str, str] = {}
    if not os.path.exists(posts_json_path):
        return mapping
    try:
        with open(posts_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                name = item.get("name")
                title = item.get("post_title")
                if name and title:
                    mapping[safe_name(str(name))] = str(title)
    except Exception as e:
        print(f"Warning: failed to read {posts_json_path}: {e}")
    return mapping


def infer_title_from_filename(filepath: str, title_map: Dict[str, str]) -> str:
    """Infer a human title for the video using filename and optional title map.

    If filename is like NAME_partN.mp4 and title_map has NAME -> Post Title,
    return "Post Title - Part N". Otherwise, fall back to filename stem.
    """
    base = os.path.splitext(os.path.basename(filepath))[0]
    # Updated regex to match new naming convention (username_pt1, username_pt2, etc.)
    m = re.match(r"(.+)_pt(\d+)$", base)
    if m:
        key = m.group(1)
        part_num = int(m.group(2))
        post_title = title_map.get(key)
        if post_title:
            return f"{post_title} - Part {part_num}"
        return f"{key} - Part {part_num}"
    # Not a part file; try to map to post title by key
    post_title = title_map.get(base)
    return post_title or base


def get_authenticated_service() -> any:
    """Authenticate and return an authorized YouTube API client.

    First run requires a browser-based OAuth consent. Subsequent runs
    use the stored token.json.
    """
    creds: Optional[Credentials] = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or request new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Client secret file not found at {CLIENT_SECRETS_FILE}.\n"
                    f"Set YT_CLIENT_SECRETS_FILE to your OAuth client_secret JSON path."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, filepath: str, title: str, description: str, tags: List[str], category_id: str, privacy_status: str) -> Optional[str]:
    """Upload a single video file to YouTube. Returns the videoId on success."""
    body = {
        "snippet": {
            "title": title[:100],  # YouTube title max length is 100
            "description": description,
            "tags": tags,
            "categoryId": str(category_id),
            # You can also set default language and more fields if desired
        },
        "status": {
            "privacyStatus": privacy_status,
            # Shorts are just normal videos under 60s vertical; no special flag required
        },
    }

    media = MediaFileUpload(filepath, chunksize=-1, resumable=True, mimetype="video/*")

    try:
        request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading {os.path.basename(filepath)}: {int(status.progress() * 100)}%")
        video_id = response.get("id")
        if not video_id:
            print(f"Upload finished but no video ID returned for {filepath}")
            return None
        print(f"Uploaded: {filepath} -> https://youtu.be/{video_id}")
        return video_id
    except HttpError as e:
        print(f"YouTube API error for {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {filepath}: {e}")
        return None


def main():
    # Discover candidate files
    files = sorted(glob.glob(UPLOAD_GLOB))
    if not files:
        print(f"No files matched pattern: {UPLOAD_GLOB}")
        return

    # Load optional title mapping
    title_map = load_title_map(POSTS_JSON_PATH)

    # Authenticate
    youtube = get_authenticated_service()

    for path in files:
        if not os.path.isfile(path):
            continue
        marker_path = f"{path}.uploaded"
        if CREATE_UPLOADED_MARKER and os.path.exists(marker_path):
            print(f"Skipping (already uploaded): {path}")
            continue

        title = infer_title_from_filename(path, title_map)
        description = f"{HASHTAGS_LINE}\n\nAuto-uploaded."
        video_id = upload_video(
            youtube=youtube,
            filepath=path,
            title=title,
            description=description,
            tags=TAGS,
            category_id=CATEGORY_ID,
            privacy_status=PRIVACY_STATUS,
        )
        if video_id and CREATE_UPLOADED_MARKER:
            try:
                with open(marker_path, "w", encoding="utf-8") as f:
                    f.write(video_id)
            except Exception as e:
                print(f"Warning: failed to write marker for {path}: {e}")


if __name__ == "__main__":
    main()
