# OwlRedditStories

OwlRedditStories is an automated pipeline for generating, editing, and uploading Reddit story videos to YouTube. It scrapes posts from Reddit, formats and cleans the text, generates TTS audio, creates subtitled videos with background footage, and uploads the final videos in segments.

## Features

- Scrapes posts from the r/AmItheAsshole subreddit using Reddit API
- Cleans and formats post content for TTS
- Generates TTS audio using Microsoft Edge TTS voices
- Automatically creates subtitled videos with background Minecraft footage
- Splits videos into 30-second segments for upload
- Uploads video segments to YouTube using the YouTube Data API
- Handles YouTube upload limits and resumes uploads
- **Bigger**: Option to generate larger subtitles or video elements

## Requirements

- Python 3.11 (Other versions may work)
- FFmpeg installed and available in your PATH  
  (or set the binary location with:  
  `export FFMPEG_BINARY=/usr/bin/ffmpeg`)
- Reddit API credentials
- YouTube Data API credentials

Install dependencies:

```sh
pip install -r requirements.txt
```

## Setup

1. **Reddit API**:  
   Create a `.env` file with your Reddit API credentials:
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   USER_AGENT=your_user_agent
   ```

2. **YouTube API**:  
   Place your `client_secret.json` in the project root.  
   The script will generate `token.json` on first run.

3. **Background Videos**:  
   Place background `.mp4` files in the `backgrounds` directory.

4. **Sounds**:  
   Place a background sound file as `sounds/sound.mp3`.

## Usage

Run the full pipeline:

```sh
python main.py
```

This will:
- Scrape new Reddit posts
- Format and clean the posts
- Generate TTS audio
- Create subtitled videos (with bigger text, different font, and subscribe animation)
- Upload video segments to YouTube

You can also run the pipeline step-by-step by calling functions in `main.py`.

## File Structure

- `main.py`: Orchestrates the pipeline
- `reddit.py`: Scrapes Reddit posts
- `format.py`: Cleans and formats post text
- `tts.py`: Generates TTS audio
- `editor.py`: Creates subtitled videos and splits them
- `upload.py`: Handles YouTube uploads

## Notes

- Output videos and segments are stored in `output/` and `segments/`.
- Temporary TTS files are stored in `tts/`.
- Posts and their metadata are tracked in `posts.json`.

---

# Track Progress

Script runs every hour at [OwlRedditStories](https://www.youtube.com/@OwlRedditStories)
