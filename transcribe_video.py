import os
import whisper
from datetime import timedelta
import time
from tqdm import tqdm
import torch

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_single_video(video_path: str, output_dir: str, model) -> bool:
    """Transcribe a single video"""
    # Generate output file paths
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    txt_path = os.path.join(output_dir, f"{base_name}.txt")
    
    # Skip if files already exist
    if os.path.exists(srt_path) and os.path.exists(txt_path):
        print(f"Subtitle files already exist for {base_name}")
        return True
    
    try:
        print(f"Starting transcription for: {base_name}")
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        result = model.transcribe(video_path)
        
        # Save as TXT file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # Save as SRT file
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        print(f"Completed transcription for: {base_name}")
        return True
        
    except Exception as e:
        print(f"Transcription failed for {base_name}: {str(e)}")
        return False

def transcribe_videos(videos_dir: str, output_dir: str) -> None:
    """Transcribe all videos in the directory"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of video files
    video_files = []
    for file in os.listdir(videos_dir):
        if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            video_files.append(os.path.join(videos_dir, file))
    
    if not video_files:
        print("No video files found in the directory")
        return
    
    print(f"Found {len(video_files)} video files to process")
    
    # Load Whisper model
    print("Loading Whisper model...")
    model = whisper.load_model("medium")
    
    # Process videos
    successful_transcriptions = 0
    failed_transcriptions = 0
    
    for video_path in tqdm(video_files, desc="Transcribing videos"):
        success = transcribe_single_video(video_path, output_dir, model)
        if success:
            successful_transcriptions += 1
        else:
            failed_transcriptions += 1
    
    # Print summary
    print("\nTranscription Summary:")
    print(f"Total videos: {len(video_files)}")
    print(f"Successful transcriptions: {successful_transcriptions}")
    print(f"Failed transcriptions: {failed_transcriptions}")

if __name__ == "__main__":
    # Input and output directories
    videos_dir = "./videos"
    output_dir = "./transcripts"
    
    # Start transcription
    start_time = time.time()
    transcribe_videos(videos_dir, output_dir)
    end_time = time.time()
    
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds") 