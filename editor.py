import subprocess
import whisper_timestamped as whisper
import os
from pydub import AudioSegment

def time_to_srt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def subtitiles(video, audio_file, title, sound_file):
    model = whisper.load_model("tiny", device="cpu")
    result = whisper.transcribe(model, audio_file)

    audio_duration_ms = AudioSegment.from_mp3(audio_file).duration_seconds
    
    srt_content = ""
    counter = 1

    for seg in result["segments"]:
        for word in seg["words"]:
            start = time_to_srt(word["start"])
            end = time_to_srt(word["end"])

            srt_content += f"{counter}\n"
            srt_content += f"{start} --> {end}\n"
            srt_content += f"{word['text']}\n\n"
            counter += 1

    srt_filename = f"temp_{title}.srt"
    with open(srt_filename, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    # Ai generated command : Sorry guys but ohh my days moviepy was wasting my memory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_filename = "clarencealt-heavy.otf"
    font_path = os.path.join(script_dir, font_filename)
    cmd = [
        'ffmpeg',
        '-i', f"backgrounds/{video}",
        '-i', audio_file,
        '-i', sound_file,
        '-filter_complex',
        f"[0:v]subtitles={srt_filename}:force_style='FontName={font_path},FontSize=30,PrimaryColour=&H00FFFF,Bold=1,OutlineColour=&H000000,BorderStyle=0,Outline=2,Shadow=0,Alignment=10,MarginV=0',hwupload_cuda,trim=duration={audio_duration_ms}[v];[2:a]volume=0.2[sound_vol];[1:a][sound_vol]amix=inputs=2:duration=shortest[a]",
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'h264_nvenc',
        '-preset', 'p4',
        '-cq', '23',
        '-rc', 'vbr',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-y',
        f"output/{title}.mp4"
    ]

    subprocess.run(cmd)
    
    # Clean up
    os.remove(srt_filename)
