import os
import yt_dlp

def download_video(video_url, output_path):
    # Check if output directory exists, create if not
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Skip download if file already exists
    if os.path.exists(output_path):
        print(f"Video already exists: {output_path}")
        return
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'best',  # Download highest quality
        'outtmpl': output_path,  # Output file path
        'quiet': True,  # Reduce output information
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting video download: {video_url}")
            ydl.download([video_url])
            print(f"Video saved to: {output_path}")
    except Exception as e:
        print(f"Download failed: {str(e)}")

if __name__ == "__main__":
    # Video URL
    video_url = "https://www.youtube.com/watch?v=wLtLz4wQtOg"
    
    # Output path
    output_path = "./videos/video1.mp4"
    
    # Download video
    download_video(video_url, output_path) 