from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import whisper

def subtitiles(video, audio, title):
    model = whisper.load_model("base")
    result = whisper.transcribe(audio)
    clip = (
        VideoFileClip(f"backgrounds/{video}.mp4")
    )

    # Generate a text clip. You can customize the font, color, etc.
    txt_clip = TextClip(
        font="Arial.ttf",
        text=result,
        font_size=70,
        color='white'
    ).with_duration(10).with_position('center')

    # Overlay the text clip on the first video clip
    final_video = CompositeVideoClip([clip, txt_clip])
    final_video.write_videofile(f"output/{title}.mp4")

subtitiles("backgrounds/Minecraft (1).mp4", "tts/askingAITAquestion.mp3", "askingAITAquestion")