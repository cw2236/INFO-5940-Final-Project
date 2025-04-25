import os
import whisper
from datetime import timedelta

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_video(video_path, output_dir):
    # Check if output directory exists, create if not
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output file paths
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    txt_path = os.path.join(output_dir, f"{base_name}.txt")
    
    # Skip if files already exist
    if os.path.exists(srt_path) and os.path.exists(txt_path):
        print(f"Subtitle files already exist: {srt_path} and {txt_path}")
        return
    
    try:
        print("Loading Whisper model...")
        model = whisper.load_model("medium")
        
        print(f"Starting video transcription: {video_path}")
        result = model.transcribe(video_path)
        
        # Save as TXT file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"Saved text file: {txt_path}")
        
        # Save as SRT file
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        print(f"Saved SRT file: {srt_path}")
        
    except Exception as e:
        print(f"Transcription failed: {str(e)}")

if __name__ == "__main__":
    # Video path
    video_path = "./videos/video1.mp4"
    
    # Output directory
    output_dir = "./transcripts"
    
    # Transcribe video
    transcribe_video(video_path, output_dir) 