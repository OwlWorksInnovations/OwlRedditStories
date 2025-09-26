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
    audio_duration_ms = AudioSegment.from_file(audio_file).duration_seconds
   
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
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ENCODER_CONFIGS = [
        {
            "name": "NVIDIA NVENC",
            "codec": "h264_nvenc",
            "params": ['-preset', 'p4', '-cq', '23', '-rc', 'vbr']
        },
        {
            "name": "AMD AMF",
            "codec": "h264_amf",
            "params": ['-preset', 'speed', '-rc', 'cbr', '-b:v', '6M']
        },
        {
            "name": "CPU Fallback",
            "codec": "libx264",
            "params": ['-preset', 'fast', '-crf', '23']
        }
    ]
    
    os.makedirs("output", exist_ok=True)
    
    encoding_successful = False
   
    for config in ENCODER_CONFIGS:
        print(f"Attempting to encode with: {config['name']}")
        filter_complex = (
            f"[0:v]subtitles={srt_filename}:"
            f"force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFF,Bold=1,"
            f"OutlineColour=&H000000,BorderStyle=0,Outline=2,Shadow=0,Alignment=10,MarginV=0',"
            f"trim=duration={audio_duration_ms}[v];"
            f"[2:a]volume=0.2[sound_vol];"
            f"[1:a][sound_vol]amix=inputs=2:duration=shortest[a]"
        )
        
        cmd = [
            'ffmpeg',
            '-i', f"backgrounds/{video}",
            '-i', audio_file,
            '-i', sound_file,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', config['codec'],
            *config['params'],
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            f"output/{title}.mp4"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully encoded using {config['name']}")
            encoding_successful = True
            break
        except subprocess.CalledProcessError as e:
            print(f"Encoding failed using {config['name']}. Trying next configuration.")
            print("\n--- FFmpeg ERROR OUTPUT ---\n")
            print(e.stderr)
            print("\n---------------------------\n")
           
    if not encoding_successful:
        print("FATAL: All encoding attempts failed. Video file was not created.")
        return
    
    final_video_path = f"output/{title}.mp4"
    if os.path.exists(final_video_path):
        os.makedirs("segments", exist_ok=True)
        
        split_cmd = [
            'ffmpeg',
            '-i', final_video_path,
            '-c', 'copy',
            '-map', '0',
            '-segment_time', '00:00:30',
            '-f', 'segment',
            f"segments/{title}-part-%03d.mp4"
        ]
       
        subprocess.run(split_cmd)
    
    # Cleanup
    if os.path.exists(final_video_path):
        os.remove(final_video_path)
    if os.path.exists(srt_filename):
        os.remove(srt_filename)